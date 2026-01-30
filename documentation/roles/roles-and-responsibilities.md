# Roles and Responsibilities

## Repository Roles

| Role | Permissions |
|------|-------------|
| Codeowner | Update `release-plan.yaml` via pull requests, trigger releases, publish |
| Maintainer | Contribute to and review release content |
| Contributor | Submit PRs for release-review content |

## Release Management Roles

| Role | Permissions |
|------|-------------|
| Release reviewer | Approve Release PRs |
| Release manager | Coordinate meta-releases, intervene if blocked |

## Command Permissions

| Command | Who may execute |
|---------|----------------|
| `/create-snapshot` | Codeowner |
| `/discard-snapshot` | Codeowner, Release manager |
| `/delete-draft` | Codeowner, Release manager |
| Publish release | Codeowner |
