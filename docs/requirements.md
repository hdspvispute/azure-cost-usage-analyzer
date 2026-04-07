# Azure Cost & Usage Analyzer (ACUA) — Requirements

## 1. Core Features
- **Azure authentication via Azure CLI**: Users sign in with existing `az login` session through `DefaultAzureCredential`; no manual token entry and no hardcoded credentials.
- **Authentication status panel**: App shows current Azure credential status and guidance for local CLI auth vs Container Apps managed identity.
- **Subscription selector**: App displays a dropdown of subscriptions the authenticated user can access.
- **Multi-select resource groups**: After subscription selection, app displays a multi-select list of resource groups filtered to that subscription.
- **Cost tab (last 30 days)**: App shows aggregated total spend for selected resource groups, plus breakdown by service and resource type, including top 5 cost drivers.
- **Usage tab**: App shows aggregated resource inventory summary for selected resource groups, including counts grouped by resource type.
- **SQLite local cache**: App stores cost/usage snapshots in local SQLite DB and loads cached data by default.
- **Manual refresh from Azure**: User can explicitly refresh live data from Azure; app updates cache and displays last refreshed timestamp.

## 2. User Flow
1. User opens the Streamlit application.
2. App initializes authentication using `DefaultAzureCredential` and validates Azure Management token acquisition.
3. User selects a subscription from the subscription dropdown.
4. App loads and displays resource groups for the selected subscription.
5. User selects one or more resource groups.
6. App checks local SQLite cache for selected subscription + resource group set.
7. If cached snapshot exists and user has not requested refresh, app renders cached data and shows last refreshed timestamp.
8. If user clicks refresh (or cache is missing), app fetches from Azure, updates cache, and renders latest data.
9. If data is unavailable or access is limited, app shows a clear, user-friendly message and marks output as mock fallback.

## 3. Scope (v1)
- Read-only Azure cost and usage analysis for a single selected subscription and one or more selected resource groups.
- Authentication using Azure CLI and `DefaultAzureCredential` only.
- Cost insights limited to the last 30 days.
- Cost breakdown by service and resource type, including top 5 cost drivers, aggregated across selected resource groups.
- Usage summary showing resource counts by type, aggregated across selected resource groups.
- Local SQLite cache with manual refresh behavior.
- Local execution via Streamlit for developers, DevOps, and FinOps users.
- Optional Playwright UI E2E smoke tests for rendered dashboard behavior.

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
