# GitHub Copilot Instructions — Azure Cost & Usage Analyzer (ACUA)

## Project Overview
This is a Python Streamlit application that lets users explore Azure subscription
costs and usage by resource group. Users authenticate via Azure CLI (az login).

## Tech Stack
- Language: Python 3.11+
- UI: Streamlit
- Azure SDKs: azure-mgmt-costmanagement, azure-mgmt-resource, azure-identity
- Auth: DefaultAzureCredential (Azure CLI — never hardcode credentials)
- Testing: pytest

## Rules

### Before writing any code
- Always read the docs/ folder first
- Always read context/app_context.json for current assumptions and limits
- Always check the relevant skills/ folder before implementing a feature

### Code style
- Keep functions small and single-purpose (one responsibility per function)
- Prefer explicit over implicit — name things clearly
- All Azure API calls must use DefaultAzureCredential
- Never hardcode credentials, subscription IDs, tenant IDs, or resource names
- Use environment variables or Azure SDK defaults only

### Architecture
- Follow the structure in docs/architecture.md
- UI logic belongs in app/ui/
- Business logic belongs in app/services/
- Azure API integration belongs in app/azure/
- Keep concerns separated — UI must not call Azure APIs directly

### Testing
- Write tests for all business logic in tests/
- Test service functions, not UI
- Use mocks for Azure API calls in tests — do not require real Azure access to run tests

### Do NOT
- Do not overwrite existing logic without reading it first
- Do not generate code without reading the context
- Do not add unnecessary dependencies to requirements.txt
- Do not over-engineer — build only what is defined in docs/requirements.md