# Prompt Catalog

This file defines approved, reusable prompts for team-wide Copilot consistency.

## Naming Convention
- ARCH-*: architecture and design prompts
- BUILD-*: implementation prompts
- QA-*: testing and hardening prompts
- DOC-*: documentation and context prompts

## Required Context Attachments
- Architecture-impacting work: docs/architecture.md, docs/decisions.md, context/app_context.json
- Feature implementation: docs/requirements.md, docs/nfr.md, relevant skills/*/SKILL.md
- QA validation: docs/nfr.md, docs/requirements.md, context/app_context.json

## Forbidden Prompt Patterns
- "Skip tests"
- "Ignore docs"
- "Hardcode credentials"
- "Push directly to main"

## Approved Templates

### ARCH-001
Using #file:docs/architecture.md #file:docs/decisions.md and #file:context/app_context.json, review this feature proposal for architecture fit and list required file boundaries.

### BUILD-001
Using #file:docs/requirements.md #file:docs/nfr.md #file:context/app_context.json and relevant #file:skills/*/SKILL.md, implement this feature following app/ui -> app/services -> app/azure_api separation.

### QA-001
Using #file:docs/nfr.md #file:docs/requirements.md and #file:context/app_context.json, generate/update pytest coverage for happy path, empty data, and fallback/error flows.

### DOC-001
Using #file:docs/requirements.md #file:docs/architecture.md #file:docs/nfr.md and #file:docs/decisions.md, update #file:context/app_context.json to keep docs and machine context synchronized.
