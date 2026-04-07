# Governance

## Scope
Define controls for architecture, quality, AI usage, documentation, and release readiness.

## Roles and Responsibilities
- Product owner: scope and outcome approval
- Architect: architecture and context integrity
- Builder: implementation quality
- QA owner: testing and NFR checks
- Release owner: deployment and rollback readiness

## Required Quality Gates
- CI green
- Required docs/context updated for behavior changes
- Owner approvals per docs/ownership.md
- NFR-impact changes reviewed by QA

## Review Cadence
- Weekly: incidents and failed deployments
- Monthly: docs/context/skills/agents drift review
- Quarterly: architecture and security posture review
