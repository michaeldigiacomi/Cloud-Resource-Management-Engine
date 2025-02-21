# Cloud Policy Management Platform

A flexible platform for managing and enforcing cloud resource policies with automated remediation capabilities. This platform allows you to define policies in JSON and automatically enforces them across your Azure and AWS resources.

## Features

- JSON-based policy definitions
- Automated policy enforcement
- Configurable evaluation frequencies
- Multiple remediation actions (modify, delete, tag)
- Supports both Azure and AWS

## Installation

### Python Version
```bash
pip install azure-identity azure-mgmt-resource boto3 dacite
```

## Configuration

Set up your cloud credentials using environment variables:

### Azure
```bash
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"

# EventHub Configuration
export AZURE_EVENTHUB_CONNECTION_STRING="your-eventhub-connection-string"
export AZURE_EVENTHUB_NAME="your-eventhub-name"
```

### AWS
```bash
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_REGION="your-region"
```

## Policy Definition Structure

Policies are defined in JSON format with the following structure:

```json
{
    "id": "unique-policy-id",
    "name": "Policy Name",
    "description": "Policy Description",
    "resourceType": "CloudProvider/ResourceType",
    "evaluationFrequency": 5,
    "conditions": [
        {
            "field": "property.path",
            "operator": "equals|notEquals|contains|exists|notExists",
            "value": "optional-value"
        }
    ],
    "remediationAction": {
        "type": "modify|delete|tag",
        "parameters": {
            "key": "value"
        }
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
    }
}
```

### AWS Examples

#### 1. Enforce S3 Bucket Encryption

```json
{
    "id": "enforce-s3-encryption",
    "name": "Enforce S3 Encryption",
    "description": "Ensures all S3 buckets have encryption enabled",
    "resourceType": "AWS::S3::Bucket",
    "evaluationFrequency": 5,
    "conditions": [
        {
            "field": "ServerSideEncryptionConfiguration.Rules[0].ApplyServerSideEncryptionByDefault.SSEAlgorithm",
            "operator": "notEquals",
            "value": "AES256"
        }
    ],
    "remediationAction": {
        "type": "modify",
        "parameters": {
            "ServerSideEncryptionConfiguration": {
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }
                ]
            }
        }
    }
}
```

#### 2. Enforce Resource Tagging

```json
{
    "id": "enforce-environment-tag",
    "name": "Enforce Environment Tag",
    "description": "Ensures all resources have an environment tag",
    "resourceType": "AWS::Resource::Tag",
    "evaluationFrequency": 10,
    "conditions": [
        {
            "field": "Tags.environment",
            "operator": "notExists"
        }
    ],
    "remediationAction": {
        "type": "tag",
        "parameters": {
            "environment": "development"
        }
    }
}
```

#### 3. Shutdown Instances if Tags are Missing

```json
{
    "id": "shutdown-instances-missing-tags",
    "name": "Shutdown Instances Missing Tags",
    "description": "Shuts down instances that are missing required tags",
    "resourceType": "AWS::EC2::Instance",
    "evaluationFrequency": 10,
    "conditions": [
        {
            "field": "Tags.environment",
            "operator": "notExists"
        }
    ],
    "remediationAction": {
        "type": "modify",
        "parameters": {
            "InstanceId": "instance-id",
            "State": "stopped"
        }
    }
}
```

## Usage

1. Create your policy definitions in a JSON file (e.g., `policies/sample-policies.json`)
2. Run the platform:

### Python Version
```bash
python src/main.py
```

## Policy Operators

- `equals`: Exact match comparison
- `notEquals`: Negative exact match comparison
- `contains`: Check if value is in array or string
- `exists`: Check if field exists
- `notExists`: Check if field doesn't exist

## Remediation Actions

- `modify`: Update resource properties
- `delete`: Remove the resource
- `tag`: Add or update resource tags

## Timing Configuration

Policies can include timing configurations for delayed remediation:

```json
"timing": {
    "delay": "30d",        // Delay before remediation (e.g., 30d, 24h, 60m)
    "warning_threshold": "25d"  // When to send warning (optional)
}
```

Supported time units:
- `d`: days
- `h`: hours
- `m`: minutes

## Event Types

The platform sends the following events to Azure Event Hub:

- `PolicyViolationDetected`: When a policy violation is first detected
- `PolicyViolationWarning`: When a warning threshold is reached
- `PolicyRemediation`: When remediation is applied
- `ImmediateRemediation`: When immediate remediation is applied

Each event contains:
- eventType: The type of event
- timestamp: UTC timestamp
- resourceId: Cloud resource ID
- policyId: Policy identifier
- details: Additional event-specific information

## Best Practices

1. Start with non-destructive policies (tagging) before implementing destructive ones
2. Test policies on non-production resources first
3. Use reasonable evaluation frequencies to avoid API throttling
4. Include clear descriptions in policy definitions
5. Monitor policy execution logs for unexpected behavior

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT
