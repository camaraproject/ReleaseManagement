# Snapshot and Branch Model

This document explains how CAMARA uses snapshots and branches to create safe, repeatable releases.

---

## Core concept

A **snapshot** is an immutable, point-in-time representation of a release attempt. It captures:

- The exact source commit from `main` (or maintenance branch)
- Mechanical changes (version numbers, URLs) applied by automation
- Release metadata recording the release configuration

Snapshots are **cheap to create and discard**. Multiple attempts for the same release number (`rX.Y`) are normal and expected.

---

## The dual-branch model

Each release attempt creates two branches:

### Snapshot branch

| Aspect | Details |
|--------|---------|
| **Pattern** | `release-snapshot/rX.Y-<shortsha>` |
| **Example** | `release-snapshot/r4.1-abc1234` |
| **Owner** | Automation |
| **Editable** | No — immutable after creation |
| **Content** | API specs with versions, URLs, `release-metadata.yaml` |
| **Lifecycle** | Created → deleted on discard → deleted after tag creation |

The snapshot branch is the authoritative record of what will be released. It contains:

- API specification files with final version numbers and URLs
- `release-metadata.yaml` with the source commit SHA and release parameters

No human edits are allowed. This ensures mechanical correctness by construction.

### Release-review branch

| Aspect | Details |
|--------|---------|
| **Pattern** | `release-review/rX.Y-<shortsha>` |
| **Example** | `release-review/r4.1-abc1234` |
| **Owner** | Humans (codeowners) |
| **Editable** | Yes |
| **Content** | CHANGELOG, README, documentation |
| **Lifecycle** | Created → merged via Release PR → kept for reference |

The release-review branch contains content that requires human judgment:

- CHANGELOG descriptions (may need refinement)
- README updates (may need additional context)

Codeowners can commit directly; maintainers and contributors submit PRs from forks.

---

## Branch naming

SHA-based naming enables multiple attempts per release:

```
release-snapshot/r4.1-abc1234   ← First attempt
release-snapshot/r4.1-def5678   ← Second attempt (after discard)
release-snapshot/r4.1-ghi9012   ← Third attempt
```

Only one snapshot can be active at a time for a given release number. The SHA suffix:

- Provides unique identification for each attempt
- Links the snapshot to its source commit
- Allows clear history tracking in the Release Issue

---

## Snapshot lifecycle

### Normal flow

```
1. /create-snapshot
   │
   ├── Validation passes
   │
   ├── Create release-snapshot/rX.Y-<sha>
   │   └── Commit: versions, URLs, release-metadata.yaml
   │
   ├── Create release-review/rX.Y-<sha>
   │   └── Commit: CHANGELOG, README
   │
   └── Open Release PR (review → snapshot)

2. Human review
   │
   └── Refine CHANGELOG on release-review branch

3. Merge Release PR
   │
   └── Review content merged into snapshot

4. Draft release created
   │
   └── release_date set in metadata

5. Human publishes
   │
   ├── Tag rX.Y created
   │
   └── Snapshot branch deleted (tag preserves content)
```

### Discard flow

When issues are found during review:

```
1. Problem discovered in snapshot

2. /discard-snapshot <reason>
   │
   ├── Release PR closed (not merged)
   │
   ├── Snapshot branch deleted
   │
   └── Release-review branch kept for reference

3. State returns to OPEN

4. Fix issues on main via normal PRs

5. /create-snapshot
   │
   └── New snapshot branch created from updated HEAD
```

### Delete-draft flow

When issues are found after Release PR merge:

```
1. Problem discovered in draft release

2. /delete-draft <reason>
   │
   ├── Draft release deleted
   │
   ├── Snapshot branch deleted
   │
   └── Release-review branch kept for reference

3. State returns to OPEN

4. Fix issues, then /create-snapshot again
```

---

## Immutability principle

The snapshot branch is immutable after creation because:

1. **Version accuracy**: Mechanical fields must exactly match the source commit
2. **Reproducibility**: The snapshot represents a specific state of the repository
3. **Audit trail**: The source commit SHA is fixed at snapshot creation

If changes are needed to API specifications:

- Fix them on `main`
- Discard the current snapshot
- Create a new snapshot from the updated `main`

This model eliminates the complexity of forward-merging or cherry-picking into release branches.

---

## Why discard is not failure

Discarding a snapshot is **normal and expected**:

| Reason to discard | Outcome |
|-------------------|---------|
| Bug found in API spec | Fix on main, create new snapshot |
| Missing test file | Add to main, create new snapshot |
| Wrong dependency declared | Update plan, create new snapshot |
| Timing issue (dependency not published) | Wait, then create new snapshot |

The cost of discarding is minimal:

- No code is lost (changes go to `main`)
- Release-review work is preserved (branch kept for reference)
- The Release Issue tracks all attempts

---

## Maintenance branches

For maintenance releases, the same model applies but starting from a maintenance branch:

```
maintenance-r3 (at xyz7890)
       ↓
/create-snapshot
       ↓
release-snapshot/r3.4-xyz7890
       ↓
(same flow as above)
       ↓
tag: r3.4
```

The maintenance branch (`maintenance-rX`) is a long-lived branch for patching older releases. Snapshot branches are still temporary, per-attempt artifacts.

---

## Branch protection

| Branch type | Protection |
|-------------|------------|
| `main` | Standard PR review requirements |
| `maintenance-rX` | Standard PR review requirements |
| `release-snapshot/*` | Automation-only write access |
| `release-review/*` | Codeowner write access |

The snapshot branch protection ensures that mechanical content cannot be accidentally modified.

---

## Post-release cleanup

After a release is published:

| Artifact | Action |
|----------|--------|
| Snapshot branch | Deleted (tag preserves content) |
| Release-review branch | Kept for reference (can be deleted manually) |
| Release tag (`rX.Y`) | Permanent |
| `src/X.Y` tag on main | Created as reference marker |

---

## See also

- [../README.md](../README.md) for documentation index
- [automation-overview.md](automation-overview.md) for automation behavior
- [release-issue-and-commands.md](release-issue-and-commands.md) for commands
- [failure-and-recovery.md](failure-and-recovery.md) for recovery scenarios
