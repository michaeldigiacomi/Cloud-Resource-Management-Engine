import unittest
from unittest.mock import AsyncMock, patch
from datetime import timedelta
from policy_engine import PolicyEngine
from types.policy import PolicyDefinition, PolicyCondition, RemediationAction, RemediationTiming

class TestPolicyEngine(unittest.TestCase):
    @patch('policy_engine.ResourceManagementClient')
    @patch('policy_engine.DefaultAzureCredential')
    def setUp(self, MockCredential, MockClient):
        self.subscription_id = 'test-subscription-id'
        self.management_group_id = 'test-management-group-id'
        self.policy_engine = PolicyEngine(self.subscription_id, 'azure', self.management_group_id)
        self.policy_engine.client = MockClient()
        self.policy_engine.eventhub = AsyncMock()

    def test_evaluate_policy(self):
        policy = PolicyDefinition(
            id="test-policy",
            name="Test Policy",
            description="A test policy",
            resource_type="Microsoft.Resources/resources",
            evaluation_frequency=5,
            conditions=[PolicyCondition(field="tags.environment", operator="notExists")],
            remediation_action=RemediationAction(
                type="tag",
                parameters={"environment": "development"},
                timing=RemediationTiming(delay=timedelta(days=7), warning_threshold=timedelta(days=5))
            )
        )
        self.policy_engine.client.resources.list_by_management_group.return_value = [
            AsyncMock(id="resource1", type="Microsoft.Resources/resources", tags={})
        ]
        self.policy_engine.client.resources.list_by_subscription.return_value = [
            AsyncMock(id="resource2", type="Microsoft.Resources/resources", tags={})
        ]

        self.policy_engine.evaluate_policy(policy)
        self.policy_engine.eventhub.send_event.assert_called()

if __name__ == '__main__':
    unittest.main()
