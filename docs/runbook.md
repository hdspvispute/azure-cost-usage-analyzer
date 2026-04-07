# Runbook

## Service Overview
Azure Cost & Usage Analyzer (ACUA) is a Streamlit app that provides cost and usage visibility for selected Azure subscriptions/resource groups.

## Local Run Instructions
1. Create and activate venv.
2. Install dependencies with requirements.txt.
3. Run az login.
4. Start app: streamlit run app/main.py.

## Deployment Process
Deployments are triggered via GitHub Actions on merge to main using OIDC authentication.

## Monitoring and Logs
- Review Streamlit logs for runtime errors.
- Review GitHub Actions logs for CI/CD failures.
- Review Azure Container Apps revision logs for production issues.

## Known Failure Modes
- Azure auth unavailable.
- No subscriptions returned.
- Cost API returns empty/delayed data.
- ACR push/deploy pipeline failures.

## Recovery Steps
1. Verify Azure auth and RBAC.
2. Confirm subscription/resource-group visibility.
3. Trigger refresh from Azure and inspect logs.
4. Roll back to prior known-good revision if deployment regresses.

## Escalation Matrix
- Sev-1: Release owner + architect immediately.
- Sev-2: Feature owner + QA owner within business hours.
- Sev-3: Backlog with owner assignment in next sprint.
