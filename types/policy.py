from typing import List, Dict, Any
from datetime import timedelta

class RemediationTiming:
    def __init__(self, delay: timedelta, warning_threshold: timedelta = None):
        self.delay = delay
        self.warning_threshold = warning_threshold

class RemediationAction:
    def __init__(self, action_type: str, parameters: Dict[str, Any] = None, timing: RemediationTiming = None):
        self.type = action_type
        self.parameters = parameters or {}
        self.timing = timing

class PolicyCondition:
    def __init__(self, field: str, operator: str, value: Any = None):
        self.field = field
        self.operator = operator
        self.value = value

class PolicyDefinition:
    def __init__(self, policy_id: str, resource_type: str, conditions: List[PolicyCondition], remediation_action: RemediationAction):
        self.id = policy_id
        self.resource_type = resource_type
        self.conditions = conditions
        self.remediation_action = remediation_action

class AWSPolicyCondition:
    def __init__(self, field: str, operator: str, value: Any = None):
        self.field = field
        self.operator = operator
        self.value = value

class AWSPolicyDefinition:
    def __init__(self, policy_id: str, resource_type: str, conditions: List[AWSPolicyCondition], remediation_action: RemediationAction):
        self.id = policy_id
        self.resource_type = resource_type
        self.conditions = conditions
        self.remediation_action = remediation_action
