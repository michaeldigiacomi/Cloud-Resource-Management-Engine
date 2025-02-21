import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List
from logging import getLogger
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from tenacity import retry, stop_after_attempt, wait_exponential

from types.policy import PolicyDefinition, PolicyCondition, RemediationAction
from services.eventhub_service import EventHubService
from services.aws_service import AWSService

class PolicyEngine:
    def __init__(self, subscription_id: str, cloud_provider: str = 'azure', management_group_id: str = None):
        self.logger = getLogger(__name__)
        self.cloud_provider = cloud_provider
        self.management_group_id = management_group_id
        if cloud_provider == 'azure':
            self.credential = DefaultAzureCredential()
            self.client = ResourceManagementClient(self.credential, subscription_id)
        elif cloud_provider == 'aws':
            self.client = AWSService()
        self.subscription_id = subscription_id
        self.state_file = Path("./state/remediation_state.json")
        self.state_file.parent.mkdir(exist_ok=True)
        self.remediation_state = self._load_state()
        self.eventhub = EventHubService()
        self.resource_cache = {}  # {cache_key: (timestamp, resources)}
        self.cache_timeout = timedelta(seconds=300)  # 5 minutes

    def _load_state(self) -> Dict:
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.remediation_state, f)

    def _get_resource_key(self, resource: Any) -> str:
        return f"{resource.id}:{resource.type}"

    def _get_cache(self, key: str):
        cached = self.resource_cache.get(key)
        if cached:
            timestamp, resources = cached
            if datetime.utcnow() - timestamp < self.cache_timeout:
                return resources
        return None

    def _set_cache(self, key: str, resources: List[Any]):
        self.resource_cache[key] = (datetime.utcnow(), resources)

    async def evaluate_policy(self, policy: PolicyDefinition) -> None:
        if self.cloud_provider == 'azure':
            # Check for defined scope
            if policy.scope and policy.scope.get('managementGroup'):
                cache_key = f"mg:{policy.scope['managementGroup']}"
                resources = self._get_cache(cache_key)
                if not resources:
                    resources = list(self.client.resources.list_by_management_group(policy.scope['managementGroup']))
                    self._set_cache(cache_key, resources)
            elif policy.scope and policy.scope.get('subscription'):
                cache_key = f"sub:{policy.scope['subscription']}"
                resources = self._get_cache(cache_key)
                if not resources:
                    resources = list(self.client.resources.list_by_subscription(policy.scope['subscription']))
                    self._set_cache(cache_key, resources)
            else:
                cache_key = "all"
                resources = self._get_cache(cache_key)
                if not resources:
                    resources = list(self.client.resources.list())
                    self._set_cache(cache_key, resources)
        elif self.cloud_provider == 'aws':
            resources = self.client.get_resources(policy.resource_type)
        
        for resource in resources:
            if resource.type == policy.resource_type:
                if self._evaluate_conditions(resource, policy.conditions):
                    await self._handle_remediation(resource, policy)

    async def _handle_remediation(self, resource: Any, policy: PolicyDefinition) -> None:
        resource_key = self._get_resource_key(resource)
        current_time = datetime.utcnow()
        
        if policy.remediation_action.timing:
            if resource_key not in self.remediation_state:
                await self.eventhub.send_event(
                    "PolicyViolationDetected",
                    resource.id,
                    policy.id,
                    {"first_violation": current_time.isoformat()}
                )
                self.remediation_state[resource_key] = {
                    "first_violation": current_time.isoformat(),
                    "policy_id": policy.id,
                    "warnings_sent": []
                }
                self._save_state()
                return
            state = self.remediation_state[resource_key]
            first_violation = datetime.fromisoformat(state["first_violation"])
            delay = policy.remediation_action.timing.delay

            if (policy.remediation_action.timing.warning_threshold and 
                current_time - first_violation >= policy.remediation_action.timing.warning_threshold and
                "warning_sent" not in state["warnings_sent"]):
                await self.eventhub.send_event(
                    "PolicyViolationWarning",
                    resource.id,
                    policy.id,
                    {"warning_time": current_time.isoformat()}
                )
                await self._send_warning(resource, policy)
                state["warnings_sent"].append("warning_sent")
                self._save_state()

            if current_time - first_violation >= delay:
                await self.eventhub.send_event(
                    "PolicyRemediation",
                    resource.id,
                    policy.id,
                    {"remediation_type": policy.remediation_action.type}
                )
                await self._apply_remediation(resource, policy.remediation_action)
                del self.remediation_state[resource_key]
                self._save_state()
        else:
            await self.eventhub.send_event(
                "ImmediateRemediation",
                resource.id,
                policy.id,
                {"remediation_type": policy.remediation_action.type}
            )
            await self._apply_remediation(resource, policy.remediation_action)

    async def _send_warning(self, resource: Any, policy: PolicyDefinition) -> None:
        print(f"WARNING: Resource {resource.id} will be remediated soon due to policy {policy.id}")

    def _evaluate_conditions(self, resource: Any, conditions: List[PolicyCondition]) -> bool:
        return all(self._evaluate_single_condition(resource, condition) for condition in conditions)

    def _evaluate_single_condition(self, resource: Any, condition: PolicyCondition) -> bool:
        value = self._get_nested_value(resource, condition.field)
        if condition.operator == 'equals':
            return value == condition.value
        elif condition.operator == 'notEquals':
            return value != condition.value
        elif condition.operator == 'exists':
            return value is not None
        elif condition.operator == 'notExists':
            return value is None
        elif condition.operator == 'contains':
            return condition.value in value if value else False
        return False

    def _get_nested_value(self, obj: Dict, path: str) -> Any:
        parts = path.split('.')
        for part in parts:
            if obj is None:
                return None
            obj = getattr(obj, part, None)
        return obj

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _apply_remediation(self, resource: Any, action: RemediationAction) -> None:
        try:
            if self.cloud_provider == 'azure':
                client = ResourceManagementClient(self.credential, self.subscription_id)
                if action.type == 'modify':
                    await client.resources.begin_update(
                        resource_group_name=resource.resource_group,
                        resource_provider_namespace=resource.type.split('/')[0],
                        parent_resource_path='',
                        resource_type=resource.type.split('/')[-1],
                        resource_name=resource.name,
                        parameters=action.parameters
                    )
                elif action.type == 'delete':
                    await client.resources.begin_delete(
                        resource_group_name=resource.resource_group,
                        resource_provider_namespace=resource.type.split('/')[0],
                        parent_resource_path='',
                        resource_type=resource.type.split('/')[-1],
                        resource_name=resource.name
                    )
                elif action.type == 'tag':
                    tags = {**resource.tags, **action.parameters}
                    await client.tags.begin_create_or_update_at_scope(
                        scope=resource.id,
                        parameters={'tags': tags}
                    )
            elif self.cloud_provider == 'aws':
                self.client.apply_remediation(resource['ResourceARN'], action)
        except Exception as e:
            self.logger.error(f"Remediation error for resource {resource.id}: {e}")
            await self.eventhub.send_event("RemediationError", resource.id, action.type, {"error": str(e)})
            raise
