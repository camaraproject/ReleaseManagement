# Terminology

This document defines the key terms and mental models for the CAMARA release system.

## Why terminology matters

The release process involves two distinct versioning systems that are often confused:

- **CAMARA release numbering** (`rX.Y`) — identifies a repository release
- **API semantic versioning** (`X.Y.Z`) — identifies an API version

These are independent. A single repository release can contain multiple APIs at different versions. Understanding this separation is essential.

---

## Core entities

### Repository release vs API version

| Concept | Scope | Example |
|---------|-------|---------|
| **Repository release** | The entire API repository at a point in time | `r4.1` of DeviceLocation |
| **API version** | A single API specification within a repository | `location-verification` at `3.2.0-rc.2` |

A repository may contain multiple APIs. Each release of the repository includes all APIs, potentially at different versions and statuses.

### Release tag vs API SemVer

| Identifier | Format | Purpose |
|------------|--------|---------|
| **Release tag** | `rX.Y` | Git tag marking a repository release |
| **API version** | `X.Y.Z` or `X.Y.Z-status.N` | Semantic version in the OpenAPI `info.version` field |

**Examples:**
- Release tag `r4.1` may contain API version `3.2.0-rc.2`
- Release tag `r4.2` may contain API version `3.2.0` (public)

The release tag increments with each release attempt. The API version follows semantic versioning rules and reflects the API's maturity.

### Release track and meta-release

Repositories declare how they participate in the overall CAMARA release process:

| Field | Values | Meaning |
|-------|--------|---------|
| `release_track` | `none`, `independent`, `meta-release` | How the repository participates in releases |
| `meta_release` | e.g., `Fall26` | Which meta-release cycle (only when track is `meta-release`) |

- **`none`**: No release planned or repository not ready
- **`independent`**: Released outside the meta-release process (for rapid iteration)
- **`meta-release`**: Participates in a coordinated meta-release cycle

### Release type vs API status

These describe readiness at different levels:

| Level | Field | Values |
|-------|-------|--------|
| **Repository** | `target_release_type` | `none`, `pre-release-alpha`, `pre-release-rc`, `public-release`, `maintenance-release` |
| **API** | `target_api_status` | `draft`, `alpha`, `rc`, `public` |

**API status progression:** `draft` → `alpha` → `rc` → `public`

- **`draft`**: API declared but implementation in progress (basic validation only)
- **`alpha`**: API exists and passes validation; ready for initial testing
- **`rc`**: Release candidate; feature-complete and ready for final review
- **`public`**: Production-ready; API is stable

**Relationship:** The repository release type constrains what API statuses are allowed:

| Release type | Allowed API statuses |
|--------------|---------------------|
| `pre-release-alpha` | All APIs at `alpha` or higher |
| `pre-release-rc` | All APIs at `rc` or `public` |
| `public-release` | All APIs at `public` |
| `maintenance-release` | All APIs at `public` (patch versions only) |

### Release Issue

A **Release Issue** is a GitHub issue dedicated to tracking one release (`rX.Y`). It serves as:

- **Trigger surface**: Commands like `/create-snapshot` are issued here
- **UI**: Shows current state, snapshot history, and next steps
- **Audit trail**: Records all release decisions and state changes

Each Release Issue has a state label (`release-state: open`, `release-state: snapshot-active`, etc.) that reflects the current status.

### Release states

The release process follows a clear state model:

| State | Meaning |
|-------|---------|
| **OPEN** | Release Issue exists; no active snapshot |
| **SNAPSHOT ACTIVE** | Snapshot branch exists; Release PR open |
| **DRAFT READY** | Release PR merged; draft release created |
| **PUBLISHED** | Release published; tag `rX.Y` created |
| **CANCELLED** | Issue closed without publication |

### Snapshot vs published release

| Concept | Description |
|---------|-------------|
| **Snapshot** | An immutable, automation-created branch representing a release *attempt* |
| **Published release** | A finalized release with a Git tag (`rX.Y`) |

Multiple snapshots may be created for the same release number. Discarding a snapshot and creating a new one is normal—it is not a failure. Only publication creates the final tag.

### Discard vs delete

| Action | Command | When |
|--------|---------|------|
| **Discard** | `/discard-snapshot <reason>` | Abandon active snapshot (before Release PR merge) |
| **Delete** | `/delete-draft <reason>` | Delete draft release (after Release PR merge, before publication) |

Both actions return the release to the OPEN state, allowing a fresh `/create-snapshot`.

### `release-plan.yaml` vs `release-metadata.yaml`

| File | Location | Purpose | Edited by |
|------|----------|---------|-----------|
| `release-plan.yaml` | `main` branch | Declares **intent** for the next release | Codeowners (manual) |
| `release-metadata.yaml` | Snapshot branch | Records **actual** release parameters | Automation (generated) |

**Think of it this way:**
- `release-plan.yaml` is what you *want* to release
- `release-metadata.yaml` is what you *actually* released

### Main contacts

Each API in `release-plan.yaml` lists **main contacts** — the GitHub handles of people responsible for that API. This replaces distributed CODEOWNERS patterns with explicit per-API accountability.

---

## Dual-branch model

Each release attempt uses **two branches**:

| Branch | Pattern | Content | Editable |
|--------|---------|---------|----------|
| **Snapshot branch** | `release-snapshot/rX.Y-<sha>` | Mechanical changes (versions, URLs, metadata) | No (automation-owned) |
| **Release-review branch** | `release-review/rX.Y-<sha>` | Documentation (CHANGELOG, README) | Yes (human-owned) |

The **Release PR** merges the release-review branch *into* the snapshot branch. This separation ensures:

- Mechanical fields cannot be accidentally corrupted
- Documentation review focuses on what humans should edit
- The PR diff shows only reviewable content

---

## Commands

Users control the release process via slash commands in the Release Issue:

| Command | Purpose | State requirement |
|---------|---------|-------------------|
| `/create-snapshot` | Validate HEAD, create branches and Release PR | Must be in OPEN state |
| `/discard-snapshot <reason>` | Abandon active snapshot | Must be in SNAPSHOT ACTIVE state |
| `/delete-draft <reason>` | Delete draft before publication | Must be in DRAFT READY state |

Commands express **intent**. Labels on the Release Issue express **state** (system-managed, not user-set).

---

## Naming conventions

| Entity | Pattern | Example |
|--------|---------|---------|
| Release tag | `rX.Y` | `r4.1`, `r5.3` |
| Snapshot branch | `release-snapshot/rX.Y-<shortsha>` | `release-snapshot/r4.1-abc1234` |
| Release-review branch | `release-review/rX.Y-<shortsha>` | `release-review/r4.1-abc1234` |
| Maintenance branch | `maintenance-rX` | `maintenance-r3` |
| API version (alpha) | `X.Y.Z-alpha.N` | `0.5.0-alpha.1` |
| API version (rc) | `X.Y.Z-rc.N` | `3.2.0-rc.2` |
| API version (public) | `X.Y.Z` | `1.0.0` |

---

## Common confusions

| Confusion | Clarification |
|-----------|---------------|
| "Release r4.1 means API version 4.1" | No. Release tags and API versions are independent numbering systems. |
| "The snapshot branch is the release" | No. The snapshot is an *attempt*. Only publication creates the release. |
| "I edit release-metadata.yaml to plan my release" | No. Edit `release-plan.yaml` on `main`. The metadata file is generated. |
| "Discarding a snapshot means we failed" | No. Multiple attempts are normal. The snapshot model makes retries cheap. |

---

## If you remember one thing...

> **Release tags (`rX.Y`) identify repository releases. API versions (`X.Y.Z`) identify API maturity. They are separate numbering systems that progress independently.**

---

## See also

- [../README.md](../README.md) for documentation index
