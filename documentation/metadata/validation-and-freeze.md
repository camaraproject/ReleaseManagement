# Validation and Freeze Behavior

This document explains how validation works, what gets blocked, and when configuration freezes apply.

---

## Validation overview

CI validation runs at two points:

| Context | When | Purpose |
|---------|------|---------|
| **Continuous validation** | Every PR to `main` | Ensure changes meet CAMARA guidelines |
| **Preflight validation** | `/create-snapshot` command | Verify release readiness before snapshot creation |

Both use the same underlying checks, but with different strictness and consequences.

---

## Continuous validation (on `main`)

### What is checked

| Check | Description |
|-------|-------------|
| Schema validation | `release-plan.yaml` follows the expected schema |
| API file existence | APIs at `alpha` or higher must have corresponding files |
| API compliance | Specifications follow CAMARA design guidelines |
| Version format | `info.version` fields are valid (or `wip`) |
| Status alignment | API statuses match declared `target_release_type` |
| Linting | MegaLinter and Spectral rules pass |

### Blocking vs warnings

| Severity | Effect | Examples |
|----------|--------|----------|
| **Error** | PR blocked until fixed | Invalid schema, missing required file |
| **Warning** | PR allowed, but shown in report | Minor linting issues, recommendations |

Errors must be fixed before merge. Warnings should be addressed but don't block.

### API status validation

APIs are validated according to their declared `target_api_status`:

| Status | Validation level |
|--------|-----------------|
| `draft` | Basic validation only (API file may not exist yet) |
| `alpha` | Full validation for alpha release |
| `rc` | Full validation for release candidate |
| `public` | Full validation for public release |

This allows new APIs to be declared with `draft` status while implementation is still in progress.

---

## Preflight validation (`/create-snapshot`)

When you run `/create-snapshot`, validation runs against the current HEAD of the base branch.

### What is checked (additional)

| Check | Description |
|-------|-------------|
| No `draft` APIs | All APIs must be at least `alpha` |
| Dependencies exist | Declared dependency releases are published |
| No active snapshot | Only one snapshot per release at a time |
| Status/type alignment | API statuses match `target_release_type` |

### Validation outcomes

| Outcome | Effect |
|---------|--------|
| **Pass** | Snapshot is created, Release PR opened |
| **Fail** | No snapshot created, errors reported in Release Issue |

If validation fails, fix the issues on `main` and run `/create-snapshot` again.

---

## Scoped configuration freeze

### What freezes

While a snapshot is active for a release (`rX.Y`), PRs that modify `release-plan.yaml` for that release are blocked.

Specifically, CI blocks PRs that change:
- `target_release_tag` if it matches the active release
- `target_release_type` if a snapshot for that tag exists
- `target_api_status` values for APIs in the active release

### What does NOT freeze

| Item | Frozen? | Reason |
|------|---------|--------|
| API specification content | No | Development continues on `main` |
| Test files | No | Development continues |
| Documentation | No | Development continues |
| `release-plan.yaml` for other releases | No | Only the active release is frozen |

### Why freeze exists

The freeze prevents confusion about which configuration applies to the active snapshot:

- Without freeze: You could change the release plan, but the snapshot still uses the old values
- With freeze: The configuration is locked until the snapshot is resolved (published or discarded)

### Releasing the freeze

The freeze is released when:
- The snapshot is discarded (`/discard-snapshot`)
- The draft is deleted (`/delete-draft`)
- The release is published (configuration becomes historical)

---

## Mutual exclusivity rule

To keep PRs reviewable and changes traceable, this rule is proposed:

### The rule

A PR to `main` may either:
- ✅ Modify `release-plan.yaml` (metadata-only), or
- ✅ Modify other repository content (specs, tests, docs),
- ❌ But NOT both in the same PR

### Why this matters

| Without the rule | With the rule |
|------------------|---------------|
| Status changes hidden in large PRs | Status changes are explicit |
| Hard to review what changed | Clear separation of concerns |
| Risk of coupling fixes with promotions | Fixes before promotion |

### How it works

If a PR modifies both metadata and implementation:
- CI will flag the PR as mixed
- The PR must be split before merging

### Exceptions

The rule applies particularly to status changes. Minor metadata updates (like contact information) may be allowed in mixed PRs depending on repository policy.

---

## Post-public-release locking

After a public release, APIs at the released version are **locked**:

### What locking means

- PRs targeting the just-released public API version are blocked by CI
- You must update `target_api_version` in `release-plan.yaml` before making changes
- This forces explicit planning for the next version

### Why locking exists

Without locking, you could accidentally modify a "released" API without updating version numbers. Locking ensures:

- Every change to a public API is intentional
- Version numbers progress explicitly
- The next release cycle is clearly started

### Releasing the lock

Update `release-plan.yaml` with a new `target_api_version` for the API. This signals that you're starting work toward the next release.

---

## Common validation errors

### "API at draft status cannot be released"

**Cause:** An API with `target_api_status: draft` exists, but `/create-snapshot` requires at least `alpha`.

**Fix:** Promote the API to `alpha` (or higher) if ready, or remove it from the release.

### "Dependency not found"

**Cause:** `release-plan.yaml` declares a dependency release that doesn't exist yet.

**Fix:** Wait for the dependency to be published, or update the dependency version.

### "Status does not match release type"

**Cause:** An API status is lower than what the `target_release_type` requires.

**Fix:** Either promote the API status or change the release type.

### "Configuration frozen for active snapshot"

**Cause:** You're trying to modify `release-plan.yaml` while a snapshot is active.

**Fix:** Discard the snapshot first, or wait until the release is complete.

### "Mixed PR: metadata and implementation"

**Cause:** The PR modifies both `release-plan.yaml` and other files.

**Fix:** Split into separate PRs—one for implementation, one for metadata.

---

## See also

- [../README.md](../README.md) for documentation index
- [../automation/automation-overview.md](../automation/automation-overview.md) for automation behavior
- [release-plan.md](release-plan.md) for what gets validated
- [../automation/failure-and-recovery.md](../automation/failure-and-recovery.md) for recovery paths
