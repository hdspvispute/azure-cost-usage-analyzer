# Ownership Matrix

| Artifact | Primary Owner | Backup Owner |
|---|---|---|
| docs/requirements.md | Product Owner | Architect |
| docs/architecture.md | Architect | Builder |
| docs/nfr.md | QA Owner | Architect |
| docs/decisions.md | Architect | Product Owner |
| context/app_context.json | Architect | Builder |
| .github/prompt-catalog.md | Architect | QA Owner |
| .github/copilot-instructions.md | Architect | Builder |
| skills/*/SKILL.md | Architect | Domain Owner |
| .github/agents/*.agent.md | Architect | QA Owner |

## Policy
PRs changing owned artifacts must include at least one owner review.
