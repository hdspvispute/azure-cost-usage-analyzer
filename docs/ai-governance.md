# AI Governance

## Policy Rules
- AI-generated code requires human review before merge.
- No AI-generated change merges without tests.
- Architecture-impacting prompts must include #file context attachments.
- Skills and agents must be updated when implementation patterns change.
- If AI output conflicts with docs/nfr.md, docs/nfr.md is authoritative.
- No sensitive data may be added to prompts or source code.

## Mandatory Review Triggers
- Authentication/security changes
- Deployment workflow changes
- Data handling/logging changes

## Prompt Governance
Reusable prompts must be added to .github/prompt-catalog.md after team review.
