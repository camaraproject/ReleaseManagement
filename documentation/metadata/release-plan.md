# The `release-plan.yaml` File

This document explains how to use `release-plan.yaml` to declare your release intentions.

## Purpose

The `release-plan.yaml` file declares your **intent** for the next release. It is edited by codeowners on `main` and validated automatically.


## Structure

```yaml
repository:
  release_track: meta-release
  meta_release: Sync26
  target_release_tag: r4.1
  target_release_type: pre-release-rc

dependencies:
  commonalities_release: r4.2
  identity_consent_management_release: r4.3

apis:
  - api_name: location-verification
    target_api_version: 3.2.0
    target_api_status: rc
    main_contacts:
      - githubUser1
```

## Repository-Level Fields

| Field | Description |
|-------|-------------|
| `release_track` | `independent` (default) or `meta-release` |
| `meta_release` | Meta-release cycle (e.g., `Sync26`) — required if track is `meta-release` |
| `target_release_tag` | Release tag (e.g., `r4.1`) |
| `target_release_type` | `none` (no release planned), `pre-release-alpha`, `pre-release-rc`, `public-release`, `maintenance-release` |


## API-Level Fields

| Field | Description |
|-------|-------------|
| `api_name` | API identifier in kebab-case (e.g., `location-verification`) |
| `target_api_version` | Base semantic version (e.g., `3.2.0`) — extensions calculated automatically |
| `target_api_status` | `draft`, `alpha`, `rc`, or `public` |
| `main_contacts` | GitHub usernames responsible for this API |

## Dependencies

```yaml
dependencies:
  commonalities_release: r4.2
  identity_consent_management_release: r4.3
```

Use **release tags** (e.g., `r4.2`), not documentation versions.

## Common Mistakes

| Mistake | Correct |
|---------|---------|
| `target_release_tag: 3.2.0` | `target_release_tag: r4.1` (use release tag, not API version) |
| `target_api_version: 3.2.0-rc.2` | `target_api_version: 3.2.0` (no pre-release extension) |
| `commonalities_release: 1.2.0` | `commonalities_release: r4.2` (use release tag) |

## When to Update

- Starting a new release cycle
- Adding a new API
- Changing release type (alpha → RC → public)
- After a public release (to unlock APIs for next version)

**Note:** While a snapshot is active, changes to `release-plan.yaml` for that release are blocked.

## Full Schema Reference (Optional)

For the complete, machine-readable definition of `release-plan.yaml`, including validation rules and constraints, see the full JSON schema:

→ [`release-plan.schema.yaml`](../../artifacts/metadata-schemas/schemas/release-plan-schema.yaml)

