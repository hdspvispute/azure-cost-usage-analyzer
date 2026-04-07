# Azure Cost & Usage Analyzer (ACUA) — Architecture

## 1. Architecture Overview
ACUA is a lightweight Python Streamlit application with a clear three-layer structure: UI, services, and Azure clients. The UI layer handles user interactions, service modules handle business logic for cost and usage summaries, and Azure client modules handle external API communication using `DefaultAzureCredential` with Azure CLI context. This separation keeps the system simple to maintain while supporting reliable local development through mock fallbacks.

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
		  | (app/azure/cost_client.py)    |   | (app/azure/resource_client.py)   |
		  +--------------------------------+   +-----------------------------------+
						   |                             |
						   +-------------+---------------+
										 v
					 +---------------------------------------+
					 | DefaultAzureCredential (Azure CLI)    |
					 +---------------------------------------+

Cost Service ---------> Mock fallback (if Azure unavailable)
Usage Service --------> Mock fallback (if Azure unavailable)
```

## 3. Folder Structure
```text
azure-cost-usage-analyzer/
|-- app/
|   |-- ui/                # Streamlit pages and UI components
|   |-- services/          # Business logic (cost calculations, usage summaries)
|   `-- azure/             # Azure SDK clients (cost, resource)
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
- **Service layer separated from UI**: Business rules stay in `app/services/` and Azure calls in `app/azure/`, making the app easier to test, maintain, and evolve without coupling UI code to external APIs.

## 5. Mock Fallback Strategy
The service layer attempts live Azure API calls first through the Azure client modules. If an API call fails (for example due to network errors, permissions, throttling) or returns no usable data, the corresponding service returns predefined mock data with a clear indicator that mock mode is active. This ensures the Streamlit UI always renders meaningful output, supports local development without mandatory Azure access, and keeps demos stable in constrained environments.
