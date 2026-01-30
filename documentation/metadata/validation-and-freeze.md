# Validation and Freeze Behavior

This document explains what validation checks apply and when changes are blocked.

## Validation Points

| Context | When | Purpose |
|---------|------|---------|
| **Continuous validation** | Every PR to `main` | Ensure changes meet CAMARA guidelines |
| **Preflight validation** | `/create-snapshot` | Verify release readiness |

## What Is Checked

| Check | Description |
|-------|-------------|
| Schema validation | `release-plan.yaml` follows expected schema |
| API file existence | APIs at `alpha` or higher must have files |
| API compliance | Specifications follow CAMARA design guidelines |
| Version format | `info.version` fields are valid (or `wip`) |
| Status alignment | API statuses match declared `target_release_type` |
| Linting | MegaLinter and Spectral rules pass |

## Preflight-Only Checks

| Check | Description |
|-------|-------------|
| No `draft` APIs | All APIs must be at least `alpha` |
| Dependencies exist | Declared dependency releases are published |
| No active snapshot | Only one snapshot per release at a time |

## Configuration Freeze

While a snapshot is active, changes to `release-plan.yaml` for that release are blocked.

**Frozen:** `target_release_tag`, `target_release_type`, `target_api_status` for the active release

**Not frozen:** API specification content, test files, documentation, configuration for other releases

**Released when:** Snapshot is discarded, draft is deleted, or release is published

## Post-Public-Release Lock

After a public release, APIs at the released version are locked. You must update `target_api_version` in `release-plan.yaml` before making changes.

## Common Validation Errors

| Error | Fix |
|-------|-----|
| "API at draft status cannot be released" | Promote API to `alpha` or higher |
| "Dependency not found" | Wait for dependency or update version |
| "Status does not match release type" | Promote API status or change release type |
| "Configuration frozen for active snapshot" | Discard snapshot first |
| "Mixed PR: metadata and implementation" | Split into separate PRs |
