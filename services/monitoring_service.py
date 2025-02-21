import logging
from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime

@dataclass
class MetricData:
    policy_id: str
    resource_id: str
    action: str
    status: str
    duration: float

class MonitoringService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics: Dict[str, Any] = {}

    def record_metric(self, metric: MetricData):
        key = f"{metric.policy_id}:{metric.resource_id}"
        self.metrics[key] = {
            "timestamp": datetime.utcnow(),
            "action": metric.action,
            "status": metric.status,
            "duration": metric.duration
        }
        self.logger.info(f"Recorded metric: {metric}")

    def get_metrics(self):
        return self.metrics
