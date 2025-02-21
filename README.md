# Azure Policy Management Platform

A flexible platform for managing and enforcing Azure resource policies with automated remediation capabilities. This platform allows you to define policies in JSON and automatically enforces them across your Azure resources.

## Features

- JSON-based policy definitions
- Automated policy enforcement
- Configurable evaluation frequencies
- Multiple remediation actions (modify, delete, tag)
- Supports both Python and TypeScript implementations

## Installation

### Python Version
```bash
pip install azure-identity azure-mgmt-resource dacite
```

### TypeScript Version
```bash
npm install @azure/identity @azure/arm-resources
```

## Configuration

Set up your Azure credentials using environment variables:

```bash
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"

# EventHub Configuration
export AZURE_EVENTHUB_CONNECTION_STRING="your-eventhub-connection-string"
export AZURE_EVENTHUB_NAME="your-eventhub-name"
```

## Policy Definition Structure

Policies are defined in JSON format with the following structure:

```json
{
    "id": "unique-policy-id",
    "name": "Policy Name",
    "description": "Policy Description",
    "resourceType": "Microsoft.*/resourceType",
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

### 1. Enforce Storage Account Encryption

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

### 2. Enforce Resource Tagging

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

### 3. Block Public IP on Network Interfaces

```json
{
    "id": "block-public-ip",
    "name": "Block Public IP",
    "description": "Prevents network interfaces from having public IPs",
    "resourceType": "Microsoft.Network/networkInterfaces",
    "evaluationFrequency": 5,
    "conditions": [
        {
            "field": "properties.ipConfigurations[0].properties.publicIPAddress",
            "operator": "exists"
        }
    ],
    "remediationAction": {
        "type": "modify",
        "parameters": {
            "properties": {
                "ipConfigurations": [
                    {
                        "properties": {
                            "publicIPAddress": null
                        }
                    }
                ]
            }
        }
    }
}
```

### 4. Remove Inactive Storage Accounts

```json
{
    "id": "remove-inactive-storage",
    "name": "Remove Inactive Storage Accounts",
    "description": "Deletes storage accounts that have been inactive for 90 days, with warnings at 75 days",
    "resourceType": "Microsoft.Storage/storageAccounts",
    "evaluationFrequency": 1440,
    "conditions": [
        {
            "field": "properties.lastAccessTime",
            "operator": "exists"
        }
    ],
    "remediationAction": {
        "type": "delete",
        "parameters": {},
        "timing": {
            "delay": "90d",
            "warning_threshold": "75d"
        }
    }
}
```

### 5. Enforce Storage Account Keys Removal

```json
{
    "id": "remove-storage-keys",
    "name": "Remove Storage Account Keys",
    "description": "Removes storage account keys after 7 days, with warning at 5 days",
    "resourceType": "Microsoft.Storage/storageAccounts",
    "evaluationFrequency": 60,
    "conditions": [
        {
            "field": "properties.accessKeys",
            "operator": "exists"
        }
    ],
    "remediationAction": {
        "type": "modify",
        "parameters": {
            "properties": {
                "accessKeys": null
            }
        },
        "timing": {
            "delay": "7d",
            "warning_threshold": "5d"
        }
    }
}
```

### 6. Clean Up Unused Network Security Groups

```json
{
    "id": "cleanup-unused-nsgs",
    "name": "Clean Up Unused NSGs",
    "description": "Removes NSGs that have no associated resources for 30 days",
    "resourceType": "Microsoft.Network/networkSecurityGroups",
    "evaluationFrequency": 120,
    "conditions": [
        {
            "field": "properties.networkInterfaces",
            "operator": "notExists"
        },
        {
            "field": "properties.subnets",
            "operator": "notExists"
        }
    ],
    "remediationAction": {
        "type": "delete",
        "parameters": {},
        "timing": {
            "delay": "30d",
            "warning_threshold": "25d"
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

### TypeScript Version
```bash
npm start
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
- resourceId: Azure resource ID
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
