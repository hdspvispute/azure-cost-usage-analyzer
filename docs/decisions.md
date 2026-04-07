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
Keep Azure API calls in app/azure_api, business logic in app/services, and UI logic in app/ui.

**Consequences**:
- Improves maintainability through clear boundaries and single responsibility.
- Enables targeted unit testing of service logic independent of UI rendering.
- Makes it easier to switch between live Azure clients and mock implementations.

Alternatives considered: place most logic directly in Streamlit page files.

## ADR-006: Data Access Mode — SQLite Cache First with Manual Refresh

**Status**: Accepted

**Context**:
Users need predictable performance and control over when live Azure data is refreshed. Re-fetching from Azure on every UI interaction can increase latency and API noise.

**Decision**:
Use local SQLite as the default read source for selected subscription + resource group sets. Fetch live Azure data only when user clicks refresh, then persist refreshed snapshot and timestamp.

**Consequences**:
- Faster and more stable user experience on repeated views.
- Clear user control over refresh behavior and data freshness.
- Requires cache lifecycle handling and explicit UI indicators for last refreshed time and source.

Alternatives considered: always-live Azure fetch on each selection, in-memory-only cache.

## ADR-007: Resource Group Selection — Multi-Select Aggregation

**Status**: Accepted

**Context**:
FinOps users often need a combined view of multiple resource groups in one subscription. Single resource group analysis limits usefulness.

**Decision**:
Support multi-select resource groups and aggregate cost/usage outputs across selected groups in services layer.

**Consequences**:
- Broader analysis scope for teams and environments.
- More complex aggregation and caching key strategy.
- UI must clearly display selected resource groups and aggregate context.

Alternatives considered: single-select only, separate tabs per resource group.

## ADR-008: Authentication UX — No In-App az login/logout Buttons

**Status**: Accepted

**Context**:
In-app execution of az login/logout is unreliable in Streamlit server context and is not a valid model for Azure Container Apps production deployment.

**Decision**:
Use credential status + guidance in sidebar instead of invoking Azure CLI login/logout from the UI. Local authentication is performed in terminal (az login). Cloud authentication uses managed identity.

**Consequences**:
- Avoids false success/failure UI states caused by shell/process differences.
- Aligns local and production deployment behavior with least operational surprise.
- Requires clear documentation for local auth and managed identity RBAC setup.

Alternatives considered: in-app CLI subprocess login/logout, embedded interactive browser/device code auth flow.

## ADR-009: UI Test Strategy — Unit + Live + Playwright E2E

**Status**: Accepted

**Context**:
Unit tests with mocks can pass while real Streamlit UI workflows still fail in browser.

**Decision**:
Use layered tests: unit tests for services/auth, optional live Azure contract tests, and optional Playwright UI smoke tests against a running Streamlit instance.

**Consequences**:
- Better confidence in real user-visible behavior.
- Requires additional test dependencies and a running app endpoint for E2E.
- E2E should remain smoke-level and opt-in to keep CI stable.

Alternatives considered: unit-only strategy, manual-only UI verification.
