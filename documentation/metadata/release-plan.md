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

seeded_from:
  repository: QualityOnDemand
  release_tag: r4.1
  apis:
    - api_name: qos-profiles
      seeded_api_version: 1.2.0-rc.3
      last_rc_api_version: 1.2.0-rc.3
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

## Seeded From (Repository Splits)

When one or more APIs move into a new repository from an existing one (a repo split), the new
repository's pre-release version chain continues where the predecessor left off — it does not
restart at `-rc.1`/`-alpha.1`. Declare this once, by hand, as a pinned fact:

```yaml
seeded_from:
  repository: QualityOnDemand
  release_tag: r4.1
  apis:
    - api_name: qos-profiles
      seeded_api_version: 1.2.0-rc.3
      last_rc_api_version: 1.2.0-rc.3
```

| Field | Description |
|-------|-------------|
| `repository` | Predecessor repository name. Provenance only. |
| `release_tag` | Predecessor repository release_tag the seed was taken from. Provenance only. |
| `apis[].api_name` | API name, matching an entry in the top-level `apis` list |
| `apis[].seeded_api_version` | The API's full version at the seed tag. Documentation only — not read by version calculation |
| `apis[].last_rc_api_version` | Last published rc version in the predecessor's URL-version namespace. Read by Release Automation to calculate the next rc extension number. Omit if there was no prior rc |
| `apis[].last_alpha_api_version` | Same as `last_rc_api_version`, for the alpha status |

This is a one-time, hand-declared fact, not a live lookup against the predecessor repository —
after this repository's own first release for an API, its own history takes over and the seed
becomes inert. Omit `seeded_from` entirely for repositories that are not seeded from a split.

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

