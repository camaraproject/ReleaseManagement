# Failure and Recovery

This document explains how to recover from problems encountered during the release process.

---

## Key principle

**Discarding and retrying is normal.**

The snapshot model is designed so that:
- Creating a new snapshot is cheap
- Discarding a snapshot loses no work
- Multiple attempts per release are expected

When something goes wrong, the answer is usually: discard, fix, retry.

---

## Recovery by state

### From SNAPSHOT ACTIVE

**Situation:** A snapshot exists and the Release PR is open, but you found a problem.

**Recovery:**

```
1. Post `/discard-snapshot <reason>` in the Release Issue
   ↓
2. State returns to OPEN
   ↓
3. Fix the issue via PR to `main`
   ↓
4. Post `/create-snapshot` to create a new snapshot
```

**What happens when you discard:**
- The snapshot branch is deleted
- The Release PR is closed (not merged)
- The release-review branch is kept for reference
- The Release Issue records the discard reason

### From DRAFT READY

**Situation:** The Release PR was merged and a draft release exists, but you found a problem before publishing.

**Recovery:**

```
1. Post `/delete-draft <reason>` in the Release Issue
   ↓
2. State returns to OPEN
   ↓
3. Fix the issue via PR to `main`
   ↓
4. Post `/create-snapshot` to create a new snapshot
```

**What happens when you delete-draft:**
- The draft GitHub release is deleted
- The snapshot branch is deleted
- The release-review branch is kept for reference
- The Release Issue records the delete reason

### From OPEN (validation failed)

**Situation:** You ran `/create-snapshot` but validation failed.

**Recovery:**

```
1. Read the validation errors in the bot response
   ↓
2. Fix the issues via PR to `main`
   ↓
3. Post `/create-snapshot` again
```

No discard is needed—no snapshot was created.

### From CANCELLED (accidental)

**Situation:** Someone accidentally closed the Release Issue while in OPEN state.

**Recovery:**

1. Manually reopen the issue in GitHub
2. Manually replace label `release-state: cancelled` with `release-state: open`

This is deliberately manual to avoid automation complexity.

---

## Common failure scenarios

### API specification bug found during review

**Symptom:** Reviewers notice a bug in the API definition.

**Recovery:**
1. `/discard-snapshot Bug found in location-verification error response`
2. Create PR to `main` fixing the bug
3. After merge, `/create-snapshot`

### Missing test file

**Symptom:** Validation fails because a required test file is missing.

**Recovery:**
1. No discard needed (snapshot wasn't created)
2. Create PR to `main` adding the test file
3. After merge, `/create-snapshot`

### Dependency not published yet

**Symptom:** Validation fails because a declared dependency release doesn't exist.

**Recovery:**
1. No discard needed
2. Either:
   - Wait for the dependency to be published, then `/create-snapshot`
   - Update `release-plan.yaml` to use a different dependency version

### Wrong release type declared

**Symptom:** CI validation fails because API statuses don't match release type.

**Recovery:**
1. If snapshot exists: `/discard-snapshot Wrong release type declared`
2. Update `release-plan.yaml` with correct `target_release_type`
3. `/create-snapshot`

### Problem found in draft release

**Symptom:** After Release PR merge, you notice an issue in the draft artifacts.

**Recovery:**
1. `/delete-draft Critical issue in generated CHANGELOG`
2. Fix the issue on `main`
3. `/create-snapshot`

### Release timing issue

**Symptom:** You created a snapshot but need to delay publication.

**Options:**
- Simply wait—the draft can remain unpublished
- If fixes accumulated on `main` that you want to include: `/discard-snapshot Including latest fixes` then `/create-snapshot` from updated main

---

## What NOT to do

### Do not manually edit snapshot branches

The snapshot branch is automation-owned. If you need to change something:
- Discard the snapshot
- Fix on `main`
- Create a new snapshot

### Do not close the Release Issue while work is active

The Release Issue is the trigger surface for commands. Closing it while a snapshot or draft exists will cause automation to reopen it.

### Do not merge the Release PR if you have concerns

Once merged, you need `/delete-draft` to recover. If you have concerns, address them first.

### Do not try to "fix forward" on the snapshot

The snapshot is immutable for a reason. Changes to API specifications must go through `main`.

---

## Terminal states

### PUBLISHED

Once published, the release is permanent:
- The Git tag cannot be easily removed
- The GitHub release is public
- The Release Issue is closed

If a published release has problems:
- Do NOT try to "unpublish" or delete the tag
- Create a new release (patch version) with the fix
- Communicate clearly about the issue

### CANCELLED

A cancelled release is one where the issue was closed without publication:
- No snapshot was active at the time
- No draft release existed
- The release was intentionally or accidentally abandoned

To start a new attempt after cancellation, either:
- Manually recover the issue (see "From CANCELLED" above)
- Create a new Release Issue

---

## When to ask for help

Contact the Release Management team if:
- Automation is unresponsive
- Labels or state seem incorrect
- You need to do something not covered here
- A published release has critical issues

---

## Summary

| State | Problem | Command | Then |
|-------|---------|---------|------|
| OPEN | Validation failed | (none needed) | Fix on main, retry |
| SNAPSHOT ACTIVE | Issue found | `/discard-snapshot <reason>` | Fix on main, retry |
| DRAFT READY | Issue found | `/delete-draft <reason>` | Fix on main, retry |
| PUBLISHED | Issue found | (cannot undo) | Create patch release |
| CANCELLED | Accidental | (manual reopen) | Retry |

---

## See also

- [release-issue-and-commands.md](release-issue-and-commands.md) for command details
- [snapshot-and-release-branches.md](snapshot-and-release-branches.md) for branch behavior
- [lifecycle.md](../release-process/lifecycle.md) for the normal flow
