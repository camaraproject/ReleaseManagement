# Roles and Responsibilities

## Repository Roles

| Role | Permissions |
|------|-------------|
| Codeowner | Update `release-plan.yaml`, trigger releases, publish |
| Maintainer | Contribute to release content, review |
| Contributor | Submit PRs to release-review branch |

## Release Management Roles

| Role | Permissions |
|------|-------------|
| Release reviewer | Approve Release PRs |
| Release manager | Coordinate meta-releases, intervene if blocked |

## Command Permissions

| Command | Who may execute |
|---------|-----------------|
| `/create-snapshot` | Codeowner, Maintainer |
| `/discard-snapshot` | Codeowner, Maintainer, Release Management |
| `/delete-draft` | Codeowner, Maintainer, Release Management |
| Publish release | Codeowner |
