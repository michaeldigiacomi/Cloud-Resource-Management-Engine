from dataclasses import dataclass
from typing import List, Dict, Any, Literal, Optional
from datetime import timedelta

@dataclass
class TimingConfig:
    delay: timedelta
    warning_threshold: Optional[timedelta] = None

@dataclass
class PolicyCondition:
    field: str
    operator: Literal['equals', 'notEquals', 'contains', 'exists', 'notExists']
    value: Any = None

@dataclass
class RemediationAction:
    type: Literal['modify', 'delete', 'tag']
    parameters: Dict[str, Any]
    timing: Optional[TimingConfig] = None

@dataclass
class PolicyDefinition:
    id: str
    name: str
    description: str
    resource_type: str
    evaluation_frequency: int  # in minutes
    conditions: List[PolicyCondition]
    remediation_action: RemediationAction
