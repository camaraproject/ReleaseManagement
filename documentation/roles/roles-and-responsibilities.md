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
| `/create-snapshot` | Codeowner (or write permission) |
| `/discard-snapshot` | Codeowner (or write permission) |
| `/delete-draft` | Codeowner (or write permission) |
| `/publish-release` | Codeowner only (write permission + CODEOWNERS file membership) |
