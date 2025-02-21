from typing import Dict, Any
import json

class EventHubService:
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string

    async def initialize(self):
        pass  # No initialization needed for console logging

    async def send_event(self, event_type: str, resource_id: str, policy_id: str, additional_data: Dict[str, Any] = None):
        event_data = {
            "eventType": event_type,
            "resourceId": resource_id,
            "policyId": policy_id,
            **(additional_data or {})
        }
        print(json.dumps(event_data, indent=2))
