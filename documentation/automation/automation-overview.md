# Automation Overview

This document explains what automation does in the CAMARA release process, and what it guarantees.

---

## Why automation exists

Automation serves as a **co-reviewer** that enforces consistency across all repositories:

- **Prevents errors** that manual processes are prone to (wrong version numbers, inconsistent URLs)
- **Ensures compliance** with CAMARA guidelines at every stage
- **Provides repeatability** so that releases can be created and recreated reliably
- **Reduces manual overhead** by handling mechanical tasks automatically

Automation does not replace human judgment. It handles what machines do well (consistency, validation) so humans can focus on what they do well (review, decision-making).

---

## Two automation surfaces

The release workflow has two distinct automation surfaces with different purposes:

### 1. Continuous validation (on `main`)

**When:** Runs on every PR targeting `main`

**Purpose:** Validates that changes meet CAMARA guidelines and that the repository state matches declared intentions.

**What it checks:**
- Schema correctness of metadata files
- API specification compliance with CAMARA design guidelines
- Version format and URL pattern consistency
- Alignment between declared status and actual API readiness
- Dependency declarations

**Outcome:** PRs are blocked if validation fails. Developers receive feedback about what needs to be fixed.

**Key characteristic:** This is *continuous* — it runs on every change, not just during releases.

### 2. Release automation (snapshot-based)

**When:** Triggered via `/create-snapshot` command in the Release Issue

**Purpose:** Creates immutable release snapshots and prepares release artifacts.

**What it does:**
- Validates the repository state before creating a snapshot
- Creates the **snapshot branch** (automation-owned, immutable)
- Creates the **release-review branch** (human-editable)
- Applies mechanical changes (version numbers, URLs) to the snapshot
- Generates `release-metadata.yaml` with actual release parameters
- Opens the Release PR (release-review → snapshot)
- Creates the draft GitHub release after PR merge

**Outcome:** A complete, validated release attempt ready for human review and publication.

**Key characteristic:** This is *on-demand* — it runs only when explicitly triggered via commands, and produces immutable snapshots.

---

## The dual-branch model

Each release attempt uses two branches to separate concerns:

| Branch | Pattern | Content | Owner |
|--------|---------|---------|-------|
| **Snapshot branch** | `release-snapshot/rX.Y-<sha>` | Mechanical changes, metadata | Automation |
| **Release-review branch** | `release-review/rX.Y-<sha>` | CHANGELOG, README | Humans |

**Why two branches?**

- **Mechanical content** (version numbers, URLs, server paths) must be exactly correct. Automation ensures this by making the snapshot branch immutable after creation.
- **Reviewable content** (CHANGELOG descriptions, README updates) requires human judgment. The release-review branch allows edits before merging into the snapshot.

The Release PR merges the release-review branch *into* the snapshot branch. This means:
- The PR diff shows only the content humans should review
- Mechanical fields cannot be accidentally changed via the PR
- Protection is structural, not policy-based

---

## What automation owns vs humans

| Task | Owner | Rationale |
|------|-------|-----------|
| Validating API specifications | Automation | Consistent, repeatable checks |
| Setting version numbers in release | Automation | Prevents manual errors |
| Updating URLs for release | Automation | Mechanical transformation |
| Generating release metadata | Automation | Derived from validated inputs |
| Creating snapshot branches | Automation | Ensures immutability |
| Generating initial CHANGELOG | Automation | Provides starting point |
| Refining CHANGELOG content | Human | Requires judgment about clarity |
| Triggering release attempts | Human | `/create-snapshot` command |
| Deciding when to release | Human | Business and coordination decision |
| Approving the Release PR | Human | Final review checkpoint |
| Publishing the release | Human | Intentional, irreversible action |
| Discarding snapshots | Human | `/discard-snapshot` command |
| Deleting drafts | Human | `/delete-draft` command |

---

## Guarantees

Automation provides these guarantees:

| Guarantee | Description |
|-----------|-------------|
| **Validation before snapshot** | A snapshot is only created if validation passes |
| **Mechanical correctness** | Version numbers and URLs are always correctly formatted |
| **Immutable snapshots** | Once created, snapshot content cannot be accidentally modified |
| **Traceable releases** | Every release records the source commit SHA |
| **Consistent process** | The same process applies to all repositories |

---

## Non-goals

Automation does **not** attempt to:

| Non-goal | Reason |
|----------|--------|
| Replace human review | Judgment calls require human context |
| Auto-publish releases | Publication is intentional and irreversible |
| Modify API logic | Only mechanical transformations are automated |
| Handle all edge cases | Exceptional situations require human intervention |
| Enforce governance rules | Governance is a human responsibility |

---

## How validation and release automation interact

```
Development on main
        │
        ▼
┌─────────────────────┐
│ Continuous          │  ◄── Every PR
│ Validation          │
└─────────────────────┘
        │
        ▼ (validation passes)
┌─────────────────────┐
│ Trigger release     │  ◄── Explicit command
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ Preflight           │  ◄── Validates current HEAD
│ Validation          │
└─────────────────────┘
        │
        ▼ (validation passes)
┌─────────────────────┐
│ Snapshot            │  ◄── Immutable branch
│ Creation            │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ Human Review        │  ◄── Release PR
│ & Approval          │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ Draft Release       │  ◄── After PR merge
│ Creation            │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ Human Publication   │  ◄── Creates tag
└─────────────────────┘
```

---

## What this means for you

**As a developer:**
- Expect CI feedback on every PR
- Address validation errors before merging
- Trust that mechanical release tasks will be handled correctly

**As a maintainer:**
- Trigger releases when the repository is ready
- Review generated artifacts before approving
- Publish when satisfied with the release

**As a release manager:**
- Monitor release status across repositories
- Verify dependencies before coordinating meta-releases
- Trust the process to produce consistent, traceable releases

---

## See also

- [../README.md](../README.md) for documentation index
