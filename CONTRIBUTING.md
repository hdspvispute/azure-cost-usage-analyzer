# Contributing

## Branch Strategy
- main: protected, production-ready only
- feature/*: new features
- fix/*: bug fixes
- chore/*: maintenance and non-functional updates

## Pull Request Requirements
- PR references a related issue/task
- CI checks pass
- At least one reviewer approval
- Update docs/context when behavior changes
- Add or update tests for service/business logic changes
- Include rollback notes for risky changes

## Merge Policy
- Squash merge only
- No direct push to main
- Resolve all review comments before merge

## Documentation and Context Policy
If a PR changes behavior, update at least one of:
- docs/*
- context/app_context.json
- skills/*/SKILL.md
- .github/agents/*.agent.md

## Security and Quality Rules
- Never hardcode credentials or secrets
- Use DefaultAzureCredential patterns defined in skills/azure-auth/SKILL.md
- Keep architecture boundaries: app/ui -> app/services -> app/azure_api
- Do not merge failing tests

## Local Validation Before PR
1. Run unit tests: pytest -q
2. Run static compile check: python -m compileall app
3. Confirm changed docs/context are synchronized
