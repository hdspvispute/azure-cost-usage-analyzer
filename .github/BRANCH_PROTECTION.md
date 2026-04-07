# Branch Protection Guidance

Apply these settings to main branch in repository settings.

## Required Rules
- Require a pull request before merging
- Require approvals: at least 1
- Dismiss stale reviews when new commits are pushed
- Require conversation resolution before merge
- Require status checks to pass before merging
- Restrict direct pushes to main
- Require linear history (optional, recommended)

## Required Status Checks
- CI / test
- Context Guard / validate-context

## Recommended Admin Settings
- Include administrators in branch protection
- Restrict who can push to matching branches

## Notes
- CODEOWNERS enforces ownership-based reviewer routing.
- Use squash merge only for clean history.
