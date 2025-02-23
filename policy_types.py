from dataclasses import dataclass
from typing import List, Dict, Any, Literal, Optional, Union
from datetime import timedelta
import re

def parse_duration(duration_str: str) -> timedelta:
    if not duration_str:
        return timedelta()
    
    pattern = re.compile(r'(\d+)([dhm])')
    match = pattern.match(duration_str)
    if not match:
        raise ValueError(f"Invalid duration format: {duration_str}")
    
    value, unit = match.groups()
    value = int(value)
    
    if unit == 'd':
        return timedelta(days=value)
    elif unit == 'h':
        return timedelta(hours=value)
    elif unit == 'm':
        return timedelta(minutes=value)
    
    raise ValueError(f"Invalid duration unit: {unit}")

@dataclass
class TimingConfig:
    delay: Union[timedelta, str]
    warning_threshold: Optional[Union[timedelta, str]] = None

    def __post_init__(self):
        if isinstance(self.delay, str):
            self.delay = parse_duration(self.delay)
        if isinstance(self.warning_threshold, str):
            self.warning_threshold = parse_duration(self.warning_threshold)

@dataclass
class Scope:
    managementGroup: Optional[str] = None
    subscription: Optional[str] = None

@dataclass
class PolicyCondition:
    field: str
    operator: Literal[
        'equals',
        'notEquals',
        'contains',
        'exists',
        'notExists'
    ]
    value: Any = None

@dataclass
class RemediationAction:
    type: Literal['modify', 'delete', 'tag']
    parameters: Dict[str, Any]
    timing: Optional[TimingConfig] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

@dataclass
class PolicyDefinition:
    id: str
    name: str
    description: str
    resource_type: str
    evaluation_frequency: int  # in minutes
    conditions: List[PolicyCondition]
    remediation_action: RemediationAction
    scope: Optional[Scope] = None
