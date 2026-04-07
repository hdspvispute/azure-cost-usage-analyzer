# Azure Cost & Usage Analyzer (ACUA) — Architecture Decision Records

This document records key architecture decisions for ACUA and explains why each decision was made.

## ADR-001: UI Framework — Streamlit

**Status**: Accepted

**Context**:
ACUA needs a fast path to a working data-focused user interface for Python developers. The app requires simple interactive controls such as subscription and resource group dropdowns, plus charts and summaries for cost and usage.

**Decision**:
Use Streamlit as the UI framework.

**Consequences**:
- Faster delivery with minimal frontend setup and no separate frontend build pipeline.
- Built-in widgets and layout primitives simplify implementation of filters and dashboards.
- Less flexibility for advanced custom UI behavior compared with a full frontend stack.

Alternatives considered: Flask, Dash, FastAPI + React.

## ADR-002: Authentication — DefaultAzureCredential / Azure CLI

**Status**: Accepted

**Context**:
The project must avoid hardcoded credentials and should work both locally and in Azure-hosted environments. Developers already authenticate locally with Azure CLI, and production deployment targets Azure Container Apps.

**Decision**:
Use DefaultAzureCredential for authentication, relying on Azure CLI identity locally and managed identity in Azure environments.

**Consequences**:
- No client secrets or API keys stored in source code.
- Improved security posture and reduced secret management overhead.
- Requires users to run az login locally and have correct RBAC permissions.

Alternatives considered: service principal with client secret in .env, API keys.

## ADR-003: Mock Fallback

**Status**: Accepted

**Context**:
Azure APIs may be temporarily unavailable due to network issues, throttling, permission gaps, or environment constraints during demos. The UI should remain usable even when live data cannot be retrieved.

**Decision**:
Service modules will fall back to mock data when Azure API calls fail or return unusable data.

**Consequences**:
- Application remains functional for local development, demos, and testing without requiring live Azure access.
- Reduces user-facing failures and improves resilience of the experience.
- Requires clear UI and logging indicators so users can distinguish mock data from live data.

Alternatives considered: fail with hard errors when APIs fail, require Azure access for all testing.

## ADR-004: Deployment — Azure Container Apps

**Status**: Accepted

**Context**:
The application should be easy to deploy, scalable without VM management, and compatible with managed identity-based authentication.

**Decision**:
Deploy ACUA to Azure Container Apps.

**Consequences**:
- Serverless container platform reduces operational overhead.
- Managed scaling and managed identity support align with project requirements.
- Deployment depends on container image build and runtime configuration discipline.

Alternatives considered: Azure App Service, Azure Functions, Azure VM.

## ADR-005: Architecture — Separated Services Layer

**Status**: Accepted

**Context**:
The app includes UI logic, business logic, and external API integration. Without separation, code becomes difficult to test, change, and maintain as features expand.

**Decision**:
Keep Azure API calls in app/azure, business logic in app/services, and UI logic in app/ui.

**Consequences**:
- Improves maintainability through clear boundaries and single responsibility.
- Enables targeted unit testing of service logic independent of UI rendering.
- Makes it easier to switch between live Azure clients and mock implementations.

Alternatives considered: place most logic directly in Streamlit page files.
