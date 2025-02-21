from azure.eventhub import EventHubProducerClient, EventData
from typing import Dict, Any
import json

class EventHubService:
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string
        self.producer = None

    async def initialize(self):
        if self.connection_string:
            self.producer = EventHubProducerClient.from_connection_string(self.connection_string)

    async def send_event(self, event_type: str, resource_id: str, policy_id: str, additional_data: Dict[str, Any] = None):
        if not self.producer:
            return  # Silent fail if not configured

        event_data = {
            "eventType": event_type,
            "resourceId": resource_id,
            "policyId": policy_id,
            **(additional_data or {})
        }

        event = EventData(json.dumps(event_data))
        async with self.producer:
            await self.producer.send_batch([event])
