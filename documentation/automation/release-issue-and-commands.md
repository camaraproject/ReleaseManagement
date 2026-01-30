# Triggers and Entry Points

This document describes how humans interact with release automation: the Release Issue, the Release PR, and publication.

---

## Overview

The release process has three main human interaction points:

1. **Release Issue** — Where you trigger and track the release
2. **Release PR** — Where you review and approve documentation
3. **Draft publication** — Where you make the release permanent

Each serves a distinct purpose. Understanding these entry points helps you navigate the release process confidently.

---

## The Release Issue

### Purpose

The Release Issue is the **user interface** for a release. It serves as:

- The trigger surface for release commands
- An audit trail of all release decisions
- A discussion space for release coordination
- A visible tracker of release progress

**Important:** The Release Issue is *not* the source of truth for release state. The actual state is derived from repository artifacts (branches, tags, releases). The issue reflects and tracks that state.

### What you do here

| Action | How | When |
|--------|-----|------|
| Start a release | Post `/create-snapshot` | When development is complete |
| Abandon an attempt | Post `/discard-snapshot <reason>` | When issues are found during review |
| Delete a draft | Post `/delete-draft <reason>` | When problems are found in draft before publication |
| Track progress | Read the issue comments and labels | Throughout the release |
| Discuss decisions | Comment on the issue | As needed |

### Commands

Commands are posted as comments on the Release Issue. They express your **intent** to take an action.

| Command | What it does | Allowed state |
|---------|--------------|---------------|
| `/create-snapshot` | Validates current HEAD and creates a snapshot if validation passes | OPEN |
| `/discard-snapshot <reason>` | Discards the active snapshot; requires a reason for the audit trail | SNAPSHOT ACTIVE |
| `/delete-draft <reason>` | Deletes a draft release before publication; requires a reason | DRAFT READY |

**Command behavior:**
- Commands only work when the release is in the appropriate state
- Failed commands produce clear error messages explaining why
- Successful commands update the issue with next steps

### Labels

Labels on the Release Issue indicate the current state:

| Label | Meaning |
|-------|---------|
| `release-state: open` | No active snapshot; ready for `/create-snapshot` |
| `release-state: snapshot-active` | Snapshot exists; Release PR under review |
| `release-state: draft-ready` | Release PR merged; draft release awaiting publication |
| `release-state: published` | Release published; issue closed |
| `release-state: cancelled` | Issue closed without publication |

Labels are updated automatically. Do not edit them manually.

### State transitions

The release progresses through states based on commands and events:

```
OPEN ──/create-snapshot──► SNAPSHOT ACTIVE ──merge PR──► DRAFT READY ──publish──► PUBLISHED
  │                              │                            │
  │                              │/discard-snapshot           │/delete-draft
  │                              ▼                            ▼
  │                            OPEN                         OPEN
  │
  └──close issue──► CANCELLED
```

**Terminal states:** PUBLISHED and CANCELLED are final. Once in these states, the release is complete.

---

## The Release PR

### Purpose

The Release PR is where **documentation is reviewed**. It merges the release-review branch (containing reviewable content) into the snapshot branch (containing mechanical changes).

### What is reviewable

The Release PR shows only documentation changes:

| Content | Reviewable | Editable |
|---------|------------|----------|
| CHANGELOG entries | Yes | Yes |
| README updates | Yes | Yes |
| API Readiness Checklist | Yes | Yes |
| API version numbers | No | No (automation-set) |
| Server URLs | No | No (automation-set) |
| `release-metadata.yaml` | No | No (generated) |

This separation is intentional. Mechanical changes are protected by construction—you cannot accidentally modify version numbers in the Release PR.

### What to review

When reviewing the Release PR:

- Verify the CHANGELOG accurately describes what changed
- Check that release notes are clear and complete
- Confirm the readiness checklist reflects actual asset availability
- Ensure README updates are appropriate

### Who approves

The Release PR requires approval from:

| Approver | Responsibility |
|----------|----------------|
| Repository codeowner(s) | Confirm content accuracy |
| Release reviewer(s) | Confirm process compliance |

Both must approve before the PR can be merged.

### What merging means

Merging the Release PR:

- Combines the reviewable content with the mechanical changes
- Triggers creation of a **draft** GitHub release
- Does **not** create the release tag yet

After merge, the release is in "draft ready" state awaiting human publication.

---

## Draft release publication

### What "draft" means

A draft release is a **prepared but unpublished** GitHub release:

- It contains all release artifacts
- It is visible only to repository collaborators
- It has no Git tag yet
- It can be deleted without consequence

The draft is your final opportunity to review before the release becomes permanent.

### What to check before publishing

Before publishing, verify:

- Release notes are accurate and complete
- All expected artifacts are present
- Dependencies (Commonalities, ICM) are published
- The release timing is appropriate

### Who publishes

Publication is performed by a human with appropriate permissions. This is typically:

- A repository maintainer, or
- A release manager

The choice of who publishes may depend on coordination requirements (e.g., for meta-releases).

### What publication does

When you publish:

1. The draft release becomes public
2. A Git tag (`rX.Y`) is created on the snapshot branch
3. The Release Issue is closed with `release-state: published`
4. Post-release cleanup begins

**This action is irreversible.** Once published, the tag exists permanently in Git history.

---

## The happy path

For a typical release:

1. **Trigger:** Post `/create-snapshot` on the Release Issue
2. **Review:** Examine the Release PR, refine documentation if needed
3. **Approve:** Codeowners and release reviewers approve the PR
4. **Merge:** Merge the Release PR
5. **Publish:** Review the draft release and publish it

That's it. Most releases follow this straightforward path.

---

## When things don't go as planned

### Issue found during review

If you find a problem in the API specification:

1. Post `/discard-snapshot <reason>` on the Release Issue
2. Fix the issue with a PR to `main`
3. Post `/create-snapshot` to create a new snapshot

### Issue found after merge but before publication

If you find a problem in the draft release:

1. Post `/delete-draft <reason>` on the Release Issue
2. Fix the issue with a PR to `main`
3. Post `/create-snapshot` to start fresh

### Multiple attempts

Creating multiple snapshots for the same release is normal. Each attempt gets a unique identifier. Previous attempts are recorded in the Release Issue for reference.

---

## Summary

| Entry Point | Purpose | Key Action |
|-------------|---------|------------|
| Release Issue | Trigger and track releases | Post commands |
| Release PR | Review documentation | Approve and merge |
| Draft publication | Finalize the release | Publish |

Each entry point has clear responsibilities. Automation handles the mechanical work; you make the decisions.

---

## See also

- [../README.md](../README.md) for documentation index
