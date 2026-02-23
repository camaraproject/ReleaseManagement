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
| Draft release | Pre-publication | Review, then publish |
| Post-release sync PR | Syncs CHANGELOG and README to `main` | Review and merge |

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
| Trigger release publication (`/publish-release --confirm rX.Y`) | Codeowner |
| Merge post-release sync PR | Codeowner |
| Reset attempt (`/discard-snapshot` or `/delete-draft`) | Codeowner |

## Commands Reference

| Command | Purpose | When allowed |
|---------|---------|--------------|
| `/create-snapshot` | Start release attempt | PLANNED state |
| `/discard-snapshot <reason>` | Abandon attempt | SNAPSHOT ACTIVE state |
| `/delete-draft <reason>` | Delete before publish | DRAFT READY state |
| `/publish-release --confirm rX.Y` | Publish the release | DRAFT READY state |

Commands are posted as comments on the Release Issue.

## Release States

| State | Meaning | Label |
|-------|---------|-------|
| PLANNED | Ready to start | `release-state: planned` |
| SNAPSHOT ACTIVE | Release PR exists | `release-state: snapshot-active` |
| DRAFT READY | Draft awaiting publish | `release-state: draft-ready` |
| PUBLISHED | Complete | `release-state: published` |
| NOT PLANNED | Release no longer planned | `release-state: not-planned` |

To mark a release as not planned, a codeowner sets `target_release_type: none` in `release-plan.yaml`.

## Branch Model

Each release attempt uses two branches:

- **Snapshot branch** (`release-snapshot/rX.Y-*`): Protected, automation-owned
- **Release-review branch** (`release-review/rX.Y-*`): Editable via Release PR

You never interact with these directly — the Release PR is your interface.

## Reference Tags

After publication, automation creates a `source/rX.Y` tag on `main` pointing to the source commit. This is a convenience pointer for creating maintenance branches or comparing releases. This tag does not need any actions from codeowners or reviewers.
The authoritative source commit is `src_commit_sha` in `release-metadata.yaml`.```

## Source of Truth

The `release-metadata.yaml` file on the snapshot branch is the authoritative record. The Release Issue is a UI and audit trail, not the source of truth.
