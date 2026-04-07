# Azure Cost & Usage Analyzer (ACUA) — Requirements

## 1. Core Features
- **Azure authentication via Azure CLI**: Users sign in with existing `az login` session through `DefaultAzureCredential`; no manual token entry and no hardcoded credentials.
- **Subscription selector**: App displays a dropdown of subscriptions the authenticated user can access.
- **Resource group selector**: After subscription selection, app displays a dropdown of resource groups filtered to that subscription.
- **Cost tab (last 30 days)**: App shows total spend for the selected resource group, plus breakdown by service and resource type, including top 5 cost drivers.
- **Usage tab**: App shows resource inventory summary for the selected resource group, including counts grouped by resource type.

## 2. User Flow
1. User opens the Streamlit application.
2. App initializes authentication using `DefaultAzureCredential` and existing Azure CLI login context.
3. User selects a subscription from the subscription dropdown.
4. App loads and displays resource groups for the selected subscription.
5. User selects a resource group.
6. App loads cost data for the selected resource group (last 30 days) and displays total cost and top cost drivers.
7. App loads usage data for the selected resource group and displays resource counts by type.
8. If data is unavailable or access is limited, app shows a clear, user-friendly message.

## 3. Scope (v1)
- Read-only Azure cost and usage analysis for a single selected subscription and resource group.
- Authentication using Azure CLI and `DefaultAzureCredential` only.
- Cost insights limited to the last 30 days.
- Cost breakdown by service and resource type, including top 5 cost drivers.
- Usage summary showing resource counts by type.
- Local execution via Streamlit for developers, DevOps, and FinOps users.

## 4. Out of Scope (v1)
- No budget alerts or budget policy enforcement.
- No cost forecasting or predictive analytics.
- No CSV or Excel export.
- No real-time monitoring dashboards.
- No multi-tenant or cross-tenant support.
- No cost comparison between multiple resource groups.

## 5. Dependencies
- **Python runtime**
	- Python 3.11+
- **UI framework**
	- `streamlit`
- **Azure identity and management SDKs**
	- `azure-identity`
	- `azure-mgmt-costmanagement`
	- `azure-mgmt-resource`
	- `azure-mgmt-subscription`
- **Supporting Python packages**
	- `pandas` (tabular shaping and summaries)
	- `plotly` (optional charting for cost/usage visuals in Streamlit)
