# Change Management

## Change Lifecycle
1. Raise issue/change request
2. Classify impact (low/medium/high)
3. Update docs/context as needed
4. Implement via PR
5. Execute QA and NFR validation
6. Approve and release
7. Record decision/update in docs/decisions.md

## Change Classes
- Low: minor fixes, no architecture impact
- Medium: feature behavior change, docs/context updates required
- High: architecture/security/performance changes; architect and QA approval required

## Release Checklist
- [ ] CI green
- [ ] Tests green
- [ ] NFR-impact reviewed
- [ ] docs/context synchronized
- [ ] Rollback plan documented
