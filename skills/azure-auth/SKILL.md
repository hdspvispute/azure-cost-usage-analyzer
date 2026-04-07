# Azure Authentication Skill — ACUA

Guidance for implementing secure Azure authentication in Azure Cost & Usage Analyzer using `DefaultAzureCredential` and Azure CLI credentials.

## When to Use This Skill

Reference this skill when:
- Implementing any new Azure SDK client module (cost client, resource client, subscription client)
- Setting up credential handling and initialization in the app
- Adding authentication error handling to UI layers
- Writing or reviewing tests that interact with Azure credentials
- Troubleshooting authentication or permission failures in local or deployed environments
- Ensuring no credentials leak into source code or logs

## Tech Context

- **Language**: Python 3.11+
- **Auth library**: `azure-identity` (specifically `DefaultAzureCredential`)
- **Local authentication**: Azure CLI (users run `az login` before app start)
- **Deployed authentication**: Managed Identity (Azure Container Apps)
- **Required package**: `azure-identity` (pinned in requirements.txt)
- **Scope**: Read-only access to subscriptions and resource groups; no write operations

## Rules

1. **Always use DefaultAzureCredential** — never hardcode credentials, API keys, connection strings, or access tokens in source code.

2. **Never hardcode subscription IDs, tenant IDs, or client IDs** — these are considered credentials; use environment variables or configuration files if needed, never stored in Git.

3. **Never store credentials in committed .env files** — use `.gitignore` to exclude local secret files; validate this in pre-commit hooks before merge.

4. **Always catch `azure.core.exceptions.AuthenticationError` and related exceptions** — wrap credential initialization in try-except blocks; show users a friendly message directing them to run `az login`.

5. **In tests, always mock `DefaultAzureCredential`** — never require real Azure access to run unit tests; mock SDK clients to return test data.

6. **Log authentication state using Python logging, not print** — log success/failure of credential initialization and Azure API calls; omit sensitive data (tokens, IDs) from logs.

7. **Pass the same credential instance to all Azure SDK clients** — initialize once, reuse; this ensures consistent identity and avoids redundant authentication attempts.

8. **Verify Reader role permissions before production** — test locally with an account that has exactly Reader access to target subscriptions; document required permissions in setup guides.

## Implementation Pattern

```python
import logging
from azure.identity import DefaultAzureCredential, ClientAuthenticationError
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.subscription import SubscriptionClient

logger = logging.getLogger(__name__)

def initialize_credentials():
    """
    Initialize Azure credentials using DefaultAzureCredential.
    Attempts multiple auth methods in order: managed identity, Azure CLI, environment.
    
    Returns:
        DefaultAzureCredential: Authenticated credential object.
    
    Raises:
        ClientAuthenticationError: If no valid credential source is found.
    """
    try:
        credential = DefaultAzureCredential()
        logger.info("Azure credentials initialized successfully.")
        return credential
    except ClientAuthenticationError as e:
        logger.error("Failed to initialize Azure credentials. Ensure Azure CLI is installed and az login has been run.")
        raise

def get_azure_clients(credential):
    """
    Create Azure SDK client objects using the provided credential.
    
    Args:
        credential: DefaultAzureCredential instance.
    
    Returns:
        dict: Dictionary of initialized Azure clients.
    """
    return {
        "subscription_client": SubscriptionClient(credential),
        "resource_client": ResourceManagementClient(credential),
        "cost_client": CostManagementClient(credential),
    }

# Usage in app initialization:
if __name__ == "__main__":
    credential = initialize_credentials()
    clients = get_azure_clients(credential)
    # Pass clients to services
```

## Expected Output

Correct authentication produces:
- Successful credential initialization with log entry: `"Azure credentials initialized successfully."`
- Azure SDK clients are created without errors.
- Subsequent API calls using those clients succeed (or fail gracefully with API-level errors, not auth errors).
- No credentials appear in logs, console output, or error messages.
- On local machine after `az login`, the app immediately recognizes the user without additional token entry.
- In Azure Container Apps with managed identity enabled, credential initialization succeeds without any local setup.

## Limitations

1. **No multi-tenant support**: `DefaultAzureCredential` authenticates to a single tenant; cross-tenant resource access is not supported in v1.

2. **No B2C or custom identity provider support**: Authentication is strictly through Azure AD (Entra ID) for the subscription tenant; other identity systems require custom implementation.

3. **No service-to-service delegation**: If the app needs to call Azure APIs on behalf of a different service principal or user, a different auth mechanism (certificate-based or interactive flow) is required.

4. **No fine-grained RBAC beyond Reader role**: The app requires Reader permissions across all accessed resources; custom roles or resource-specific permissions require additional YAML setup in Azure Container Apps.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Hardcoding `client_id` or `tenant_id` in code | Always use environment variables or remove entirely; rely on DefaultAzureCredential's automatic detection. |
| Storing `.env` file with real credentials in Git | Add `.env` and `.env.local` to `.gitignore` before commit; use pre-commit hooks to scan for common secret patterns. |
| Forgetting to catch `ClientAuthenticationError` | Wrap credential initialization in try-except; log the error and show users a friendly message like "Please run `az login` first." |
| Printing credentials or sensitive data in logs | Use Python logging module with `logger.error()`, never `print()`; configure log handlers to redact sensitive fields. |
| Creating a new credential instance per API call | Initialize credentials once and reuse; creating new instances per call wastes resources and is poor practice. |
