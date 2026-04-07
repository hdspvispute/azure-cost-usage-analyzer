# Azure Cost & Usage Analyzer (ACUA) — Architecture

## 1. Architecture Overview
ACUA is a lightweight Python Streamlit application with a clear layered structure: UI, services, Azure clients, and local SQLite cache. The UI layer handles user interactions, service modules handle business logic for cost and usage summaries, Azure client modules handle external API communication using `DefaultAzureCredential`, and local cache modules persist snapshots for fast reloads. This separation keeps the system simple to maintain while supporting reliable local development through mock fallbacks.

## 2. Component Diagram (text-based)
```text
+------------------+        +------------------------------+
|   User Browser   | -----> | Streamlit UI (app/ui/)       |
+------------------+        +------------------------------+
								 |                    |
								 v                    v
				  +---------------------------+  +---------------------------+
				  | Cost Service              |  | Usage Service             |
				  | (app/services/            |  | (app/services/            |
				  |  cost_service.py)         |  |  usage_service.py)        |
				  +---------------------------+  +---------------------------+
						   |                             |
						   v                             v
		  +--------------------------------+   +-----------------------------------+
		| Cost Client                    |   | Resource Client                   |
		| (app/azure_api/cost_client.py)|   | (app/azure_api/resource_client.py)|
		  +--------------------------------+   +-----------------------------------+
						   |                             |
						   +-------------+---------------+
										 v
					 +---------------------------------------+
					 | DefaultAzureCredential (Azure CLI)    |
					 +---------------------------------------+

Cost Service ---------> Mock fallback (if Azure unavailable)
Usage Service --------> Mock fallback (if Azure unavailable)
UI/Services ----------> SQLite cache (app/services/local_db.py)
```

## 3. Folder Structure
```text
azure-cost-usage-analyzer/
|-- app/
|   |-- ui/                # Streamlit pages and UI components
|   |-- services/          # Business logic + local cache repository
|   `-- azure_api/         # Azure SDK clients (cost, resource, subscription, auth)
|-- docs/                  # Human-readable documentation
|-- context/               # Machine-readable structured context
|-- skills/                # Copilot skill playbooks
|-- tests/                 # Unit tests (pytest)
`-- .github/               # Copilot instructions, agents, CI/CD workflows
```

## 4. Key Design Decisions
- **Streamlit as UI framework**: Chosen over Flask/FastAPI-based custom UIs to deliver a working data app quickly with minimal frontend overhead and built-in widgets for filters and charts.
- **DefaultAzureCredential for authentication**: Chosen over service principal secrets in source or `.env` files to avoid credential handling in code and align with Azure CLI local auth plus managed identity in cloud deployment.
- **Mock fallback in services**: Included so app behavior remains demonstrable even when Azure APIs fail, are inaccessible, or return empty responses in non-production environments.
- **Service layer separated from UI**: Business rules stay in `app/services/` and Azure calls in `app/azure_api/`, making the app easier to test, maintain, and evolve without coupling UI code to external APIs.
- **SQLite cache-first reads**: App reads from local SQLite by default and only fetches fresh Azure data when the user clicks refresh. This improves perceived performance and gives users explicit control over refresh behavior.

## 5. Mock Fallback Strategy
The app reads cached snapshots from local SQLite first for the selected subscription + resource group set. If user requests refresh, the service layer fetches live Azure API data and updates the cache. If an API call fails (for example due to network errors, permissions, throttling) or returns no usable data, the corresponding service returns predefined mock data with a clear indicator that mock mode is active. This ensures the Streamlit UI always renders meaningful output, supports local development without mandatory Azure access, and keeps demos stable in constrained environments.
