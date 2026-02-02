# How Automation Works

This document explains what the release automation does for you.

**Reading this is optional** — you can complete a release using only [lifecycle.md](../release-process/lifecycle.md).

## What Automation Creates

When you trigger a release, automation creates:

| Artifact | Purpose | You interact with |
|----------|---------|-------------------|
| Snapshot branch | Holds release content | No (protected) |
| Release-review branch | Your editable content | Via Release PR |
| Release PR | Review checkpoint | Review and merge |
| `release-metadata.yaml` | Release record | No (generated) |
| Draft release | Pre-publication | Publish when ready |

## What Automation Guarantees

- **Validation before release:** Snapshots are only created if validation passes
- **Version correctness:** API versions and URLs are set automatically
- **Immutability:** Release content cannot be accidentally modified
- **Traceability:** Every release records its source commit

## What Remains Manual

| Action | Who |
|--------|-----|
| Trigger release (`/create-snapshot`) | Codeowner |
| Review and merge Release PR | Codeowner + Release reviewer |
| Publish draft release | Codeowner |
| Discard or delete if problems found | Codeowner |

## Commands Reference

| Command | Purpose | When allowed |
|---------|---------|--------------|
| `/create-snapshot` | Start release attempt | PLANNED state |
| `/discard-snapshot <reason>` | Abandon attempt | SNAPSHOT ACTIVE state |
| `/delete-draft <reason>` | Delete before publish | DRAFT READY state |

Commands are posted as comments on the Release Issue.

## Release States

| State | Meaning | Label |
|-------|---------|-------|
| PLANNED | Ready to start | `release-state: planned` |
| SNAPSHOT ACTIVE | Release PR exists | `release-state: snapshot-active` |
| DRAFT READY | Draft awaiting publish | `release-state: draft-ready` |
| PUBLISHED | Complete | `release-state: published` |
| CANCELLED | Release no longer planned | `release-state: cancelled` |

If a release is no longer intended, it is cancelled by setting `target_release_type: none` in `release-plan.yaml`. This is outside the normal release flow.

## Branch Model

Each release attempt uses two branches:

- **Snapshot branch** (`release-snapshot/rX.Y-*`): Protected, automation-owned
- **Release-review branch** (`release-review/rX.Y-*`): Editable via Release PR

You never interact with these directly — the Release PR is your interface.

## Source of Truth

The `release-metadata.yaml` file on the snapshot branch is the authoritative record. The Release Issue is a UI and audit trail, not the source of truth.
