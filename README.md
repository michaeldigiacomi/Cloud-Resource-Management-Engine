# Azure Resource Management Platform

A flexible platform for managing and enforcing Azure resource policies with automated remediation capabilities.

## Features

- JSON-based policy definitions
- Automated policy enforcement
- Configurable evaluation frequencies
- Multiple remediation actions (modify, delete, tag)
- Scope filtering by management group and subscription
- Built-in monitoring and metrics collection
- Resource state caching for improved performance
- Async policy evaluation
- Configurable retry logic
- Delayed remediation with warnings

## Installation

### Requirements
- Python 3.8+
- Azure SDK

```bash
pip install -r requirements.txt
```

## Configuration

Set up your Azure credentials using environment variables:

```bash
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
```

Optional configuration:
```bash
export POLICY_CONFIG="./policies/sample-policies.json"
export AZURE_MANAGEMENT_GROUP_ID="your-management-group-id"
```

## Policy Definition Structure

```json
{
    "id": "unique-policy-id",
    "name": "Policy Name",
    "description": "Policy Description",
    "resource_type": "Microsoft.*/ResourceType",
    "evaluation_frequency": 5,
    "conditions": [
        {
            "field": "property.path",
            "operator": "equals|notEquals|contains|exists|notExists",
            "value": "optional-value"
        }
    ],
    "remediation_action": {
        "type": "modify|delete|tag",
        "parameters": {
            "key": "value"
        },
        "timing": {
            "delay": "30d",
            "warning_threshold": "25d"
        }
    },
    "scope": {
        "managementGroup": "optional-mg-id",
        "subscription": "optional-sub-id"
    }
}
```

## Policy Examples

### Azure Examples

#### 1. Enforce Storage Account Encryption

```json
{
    "id": "enforce-storage-encryption",
    "name": "Enforce Storage Encryption",
    "description": "Ensures all storage accounts have encryption enabled",
    "resourceType": "Microsoft.Storage/storageAccounts",
    "evaluationFrequency": 5,
    "conditions": [
        {
            "field": "properties.encryption.services.blob.enabled",
            "operator": "notEquals",
            "value": true
        }
    ],
    "remediationAction": {
        "type": "modify",
        "parameters": {
            "properties": {
                "encryption": {
                    "services": {
                        "blob": {
                            "enabled": true
                        }
                    }
                }
            }
        }
    },
    "scope": {
        "managementGroup": "your-management-group-id",
        "subscription": "your-subscription-id"
    }
}
```

#### 2. Enforce Resource Tagging

```json
{
    "id": "enforce-environment-tag",
    "name": "Enforce Environment Tag",
    "description": "Ensures all resources have an environment tag",
    "resourceType": "Microsoft.Resources/resources",
    "evaluationFrequency": 10,
    "conditions": [
        {
            "field": "tags.environment",
            "operator": "notExists"
        }
    ],
    "remediationAction": {
        "type": "tag",
        "parameters": {
            "environment": "development"
        }
    },
    "scope": {
        "managementGroup": "your-management-group-id",
        "subscription": "your-subscription-id"
    }
}
```

## Monitoring and Metrics

The platform provides built-in monitoring through the MonitoringService:

```python
@dataclass
class MetricData:
    policy_id: str
    resource_id: str
    action: str
    status: str
    duration: float
```

### Available Metrics

| Event Type | Description |
|------------|-------------|
| violation_detected | Initial policy violation |
| violation_warning | Warning threshold reached |
| remediation | Remediation action applied |
| immediate_remediation | Immediate remediation applied |

### Status Types

- pending: Initial violation state
- warning: Warning threshold reached
- success: Remediation completed
- failed: Remediation failed

## Resource Caching

Resources are cached to improve performance:
- Management group resources: `mg:{group_id}`
- Subscription resources: `sub:{subscription_id}`
- All resources: `all`
- Cache timeout: 5 minutes (configurable)

## Best Practices

1. Start with non-destructive policies
2. Use appropriate evaluation frequencies
3. Implement warning thresholds for destructive actions
4. Monitor remediation metrics
5. Use scoped policies for better performance
6. Configure proper retry strategies
7. Review monitoring logs regularly

## Error Handling

The platform implements:
- Retry logic for Azure API calls
- Metric tracking for failures
- Warning thresholds before remediation
- Resource state persistence
- Async operation error handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT
