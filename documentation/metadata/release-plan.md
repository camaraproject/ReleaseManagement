# The `release-plan.yaml` File

This document explains how to use `release-plan.yaml` to declare your release intentions.

---

## Purpose

The `release-plan.yaml` file declares your **intent** for the next release:

- What release tag you are targeting
- What type of release it will be
- What status each API will have
- What dependencies you require

This file is the input to release automation. It answers: "What do you want to release, and what state should it be in?"

---

## Ownership

| Aspect | Details |
|--------|---------|
| **Location** | Root of the repository on the `main` branch |
| **Edited by** | Codeowners (manually) |
| **Validated by** | CI (automatically) |

Codeowners are responsible for keeping this file accurate and up to date. CI validates that declared intentions match actual repository state.

---

## Structure overview

```yaml
repository:
  release_track: meta-release
  meta_release: Fall26
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

  - api_name: location-retrieval
    target_api_version: 0.5.0
    target_api_status: alpha
    main_contacts:
      - githubUser2
```

---

## Repository-level intent

The `repository` section declares overall release intentions:

### `release_track`

How the repository participates in CAMARA releases:

| Value | Meaning |
|-------|---------|
| `none` | No release planned |
| `independent` | Releasing outside the meta-release cycle |
| `meta-release` | Participating in a CAMARA meta-release |

### `meta_release`

The meta-release label (e.g., `Fall26`, `Spring27`). Required when `release_track` is `meta-release`.

### `target_release_tag`

The release tag this release will have (e.g., `r4.1`). This is the CAMARA release number, not the API version.

### `target_release_type`

The type of release being prepared:

| Value | Meaning | API status requirement |
|-------|---------|----------------------|
| `none` | Not ready to release | — |
| `pre-release-alpha` | Alpha pre-release | All APIs at `alpha` or higher |
| `pre-release-rc` | Release candidate | All APIs at `rc` or `public` |
| `public-release` | Public release | All APIs at `public` |
| `maintenance-release` | Maintenance/patch release | All APIs at `public` |

---

## API-level intent

The `apis` section declares intentions for each API in the repository:

### `api_name`

The API identifier in kebab-case (e.g., `location-verification`). This determines the expected filename.

### `target_api_version`

The semantic version for this release (e.g., `3.2.0`). This is the base version only—pre-release extensions like `-rc.2` are calculated automatically.

### `target_api_status`

The maturity status this API will have:

| Status | Meaning | Validation level |
|--------|---------|------------------|
| `draft` | Declared but not yet implemented | Basic validation |
| `alpha` | Early implementation for feedback | Alpha-level validation |
| `rc` | Release candidate, feature-complete | RC-level validation |
| `public` | Public release | Full validation |

Status progression: `draft` → `alpha` → `rc` → `public`

### `main_contacts`

GitHub usernames of the people responsible for this API.

---

## Dependencies

The `dependencies` section declares required releases from other repositories:

```yaml
dependencies:
  commonalities_release: r4.2
  identity_consent_management_release: r4.3
```

These specify the **release tags** (not documentation versions) of Commonalities and Identity & Consent Management that this release depends on.

CI validates that declared dependencies exist and are published before allowing release creation.

---

## Common mistakes

### Confusing release tag with API version

**Wrong:** Setting `target_release_tag: 3.2.0`
**Right:** Setting `target_release_tag: r4.1`

The release tag is the CAMARA release number (`rX.Y`), not the API semantic version.

### Including pre-release extension in target version

**Wrong:** Setting `target_api_version: 3.2.0-rc.2`
**Right:** Setting `target_api_version: 3.2.0`

Pre-release extensions are calculated automatically. Declare only the base version.

### Setting status higher than actual readiness

If you declare `target_api_status: rc` but the API doesn't pass RC validation, CI will block your PR. The declared status must match actual readiness.

### Forgetting to update after a public release

After a public release, the released API version is locked. You must update `target_api_version` before making changes, or CI will block modifications.

### Using documentation versions in dependencies

**Wrong:** `commonalities_release: 1.2.0`
**Right:** `commonalities_release: r4.2`

Dependencies use release tags, not documentation versions.

---

## When to update

Update `release-plan.yaml` when:

- Starting a new release cycle
- Changing the target release type (e.g., moving from alpha to RC)
- Adding a new API to the repository
- Changing API status declarations
- Updating dependencies
- After a public release (to unlock APIs for the next version)

### Scoped configuration freeze

While a snapshot is active for a release (`rX.Y`), PRs that modify `release-plan.yaml` for that release are blocked. This prevents confusion about which configuration applies to the active snapshot.

Development continues normally on `main`—only the release scope and intent are frozen. To change the release configuration, first discard the active snapshot with `/discard-snapshot`.

---

## Relationship to `release-metadata.yaml`

| File | Purpose | Location | Edited by |
|------|---------|----------|-----------|
| `release-plan.yaml` | Declares intent | `main` branch | Codeowners |
| `release-metadata.yaml` | Records actual release | Snapshot branch | Automation |

You edit `release-plan.yaml` to declare what you want. Automation generates `release-metadata.yaml` with what actually happened.

For details on the generated metadata, see [release-metadata.md](release-metadata.md).

---

## See also

- [../README.md](../README.md) for documentation index
