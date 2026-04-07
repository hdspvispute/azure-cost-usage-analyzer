Project Charter: Azure Cost & Usage Analyzer (ACUA)
1. Outcome Statement
Azure Cost & Usage Analyzer (ACUA) is a Python Streamlit application that helps developers, DevOps engineers, and FinOps teams quickly understand Azure spend and usage at the resource-group level. Users authenticate with their existing Azure CLI session, select a subscription and resource group, and get an immediate view of 30-day cost, top cost drivers, and resource usage composition. The value is faster, self-service cost visibility without requiring deep Azure Portal navigation or custom scripts.

2. Success Criteria
Authentication works with Azure CLI credentials via DefaultAzureCredential, with zero hardcoded credentials, and succeeds for at least one test user account with Reader access.
The app lists all subscriptions visible to the signed-in user and allows selection of one subscription in the UI.
After subscription selection, the app lists resource groups from that subscription and allows selection of one resource group.
For the selected resource group, the app displays total cost for the last 30 days, and the value matches Azure Cost Management data within an acceptable variance of 1% due to timing/rounding.
The app shows a top cost driver breakdown by both service and resource type, with at least the top 5 entries in each view when data is available.
The app shows a usage summary including total resource count and counts by resource type, and handles API failures with user-friendly error messages (no raw stack traces in UI).
3. Out of Scope (v1)
Cost forecasting, anomaly detection, or budget recommendations.
Budget creation, alerts, or policy enforcement actions.
Cross-tenant aggregation or multi-tenant login flows.
Write operations to Azure resources (read-only analysis only).
Export features (CSV, Excel, PDF) and scheduled reports.
Historical trend dashboards beyond the fixed last-30-days view.
4. Key Assumptions
Target users already use Azure CLI and can run az login in their environment.
Users have at least Reader permissions on target subscriptions/resource groups and permissions needed to read cost data.
Azure Cost Management and Resource Management APIs are available and not blocked by tenant policy.
Initial usage is interactive and low-to-moderate volume, so Streamlit with on-demand API calls is sufficient for performance.
5. Risks and Mitigations
Risk: Incomplete permissions cause missing subscriptions, resource groups, or cost data.
Mitigation: Add startup permission checks, clear guidance on required roles, and actionable error messages that identify the missing access scope.

Risk: Cost data latency or granularity differences may confuse users expecting real-time values.
Mitigation: Label all cost views as last 30 days with refresh timestamp, and include a note that Cost Management data is not real-time.

Risk: API throttling or transient Azure failures degrade user experience.
Mitigation: Implement retry with backoff for transient errors, lightweight caching for repeated requests, and friendly fallback messages with retry options.