# Azure Cost & Usage Analyzer (ACUA) — Non-Functional Requirements

This document defines measurable quality requirements for ACUA, a Python Streamlit application that reads Azure cost and usage data, runs locally, and is deployable to Azure Container Apps.

## 1. Security

| Requirement | How to verify |
|---|---|
| Authentication must use Azure CLI with DefaultAzureCredential only. No credentials, keys, passwords, subscription IDs, or tenant IDs may be hardcoded in source files. | Run a repository scan for sensitive patterns (for example: password, secret, tenant, subscription, client_secret). Manually inspect authentication modules to confirm use of DefaultAzureCredential and no inline secrets. |
| Login/logout controls must not store tokens in SQLite or local files. | Inspect SQLite schema and code paths; confirm only aggregated cost/usage snapshots and timestamps are persisted. |
| Authorization is read-only: app operations require Reader access to target subscriptions/resource groups and must not perform write operations. | Execute app flows using a Reader role account and confirm all features work. Review Azure client modules to ensure only read/list/query operations are called. |
| No real credentials are stored in committed .env files or other tracked configuration files. | Validate .gitignore includes local secret files and run a git history and working tree scan for credential-like values before merge. |
| Dependencies must be limited to approved packages in requirements.txt; no unverified third-party packages are allowed. | Compare imported packages against requirements.txt and run dependency review during pull request checks. Block merges with undeclared or unapproved packages. |

## 2. Performance

| Requirement | How to verify |
|---|---|
| Initial page load completes in under 5 seconds on a standard developer machine and connection. | Measure elapsed time from app start page request to first fully rendered UI using repeated runs (minimum 5), then confirm average is under 5 seconds. |
| Cached snapshot load from SQLite completes in under 2 seconds for typical selection sizes. | Measure elapsed time from selection to render when cache hit occurs; verify median < 2s over at least 10 runs. |
| Subscription list loads in under 3 seconds after authentication context is available. | Instrument timing around subscription fetch in logs and verify median response time is under 3 seconds over at least 10 runs. |
| Cost data for selected resource group (last 30 days) loads in under 10 seconds. | Measure end-to-end time from resource group selection to cost panel render and confirm median time is under 10 seconds across at least 10 runs. |
| Redundant API calls are avoided by caching subscription and resource group lists for the active session. | Enable request logging and confirm repeated UI interactions in the same session do not re-call list APIs unless cache invalidation conditions are met. |

## 3. Reliability

| Requirement | How to verify |
|---|---|
| If Azure Cost Management API returns no data, the app must show a friendly no-data message and continue running. | Simulate empty API response and confirm UI displays a non-technical message with no unhandled exceptions. |
| If cache exists and user has not requested refresh, app must render data from SQLite and show last refreshed timestamp. | Populate cache, disable refresh, reload app, and verify data source + timestamp are shown from cache. |
| If user clicks refresh, app must fetch from Azure, update cache, and refresh timestamp. | Trigger refresh and verify new timestamp in UI and updated row in SQLite snapshot table. |
| If user has no accessible subscriptions, the app must show a friendly no subscriptions found message. | Test with an account lacking visible subscriptions and verify the UI state is informative and stable. |
| If Azure API fails (network error, rate limit, or permission error), app must fall back to mock data and clearly label output as mock. | Inject failure scenarios and confirm fallback dataset is shown with visible mock indicator and warning-level log entry. |
| Empty resource groups must be handled without errors. | Select a resource group containing zero resources and verify usage and cost views render gracefully with empty-state messaging. |

## 4. Observability

| Requirement | How to verify |
|---|---|
| All Azure API calls must be logged with timestamp and response status using Python logging (not print). | Review logs during normal runs and confirm each API request has structured log lines with time and status code/result marker. |
| Cache reads and writes must be logged with selection key and refresh source (cache/live). | Run cache hit and refresh scenarios and inspect logs for explicit source markers and timestamps. |
| All exceptions must be logged with full exception details to console logs. | Trigger controlled failures and verify stack traces or full exception context appear in logs for debugging. |
| Mock fallback activation must log a warning with the reason fallback was triggered. | Force a fallback path and confirm warning log includes the triggering condition (for example timeout, permission, or no data). |
| Logs must not contain sensitive data such as access tokens or full subscription identifiers. | Run automated log redaction checks and manual sampling to ensure sensitive fields are masked or omitted. |

## 5. Maintainability

| Requirement | How to verify |
|---|---|
| Each module must have one clear responsibility (UI, services, Azure clients separated). | Review module boundaries in code review and confirm concerns are not mixed across layers. |
| No function should exceed 50 lines of code (excluding comments and blank lines). | Run static checks or script-based lint rule in CI to flag functions longer than the limit. |
| All Azure API calls must exist only in app/azure_api and not in UI or service layers. | Search for Azure SDK client usage/imports outside app/azure_api and fail review if found. |
| requirements.txt must remain minimal and version-pinned for reproducible builds. | Enforce pinned versions in dependency review and verify each package has a documented usage reason. |
