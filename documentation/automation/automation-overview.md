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

**When:** Triggered explicitly when creating a release

**Purpose:** Creates immutable release snapshots and prepares release artifacts.

**What it does:**
- Validates the repository state before creating a snapshot
- Creates snapshot and release-review branches
- Applies mechanical changes (version numbers, URLs) to the snapshot
- Generates `release-metadata.yaml` with actual release parameters
- Opens the Release PR
- Creates the draft GitHub release after PR merge

**Outcome:** A complete, validated release attempt ready for human review and publication.

**Key characteristic:** This is *on-demand* — it runs only when explicitly triggered, and produces immutable snapshots.

---

## What automation owns vs humans

| Task | Owner | Rationale |
|------|-------|-----------|
| Validating API specifications | Automation | Consistent, repeatable checks |
| Setting version numbers in release | Automation | Prevents manual errors |
| Updating URLs for release | Automation | Mechanical transformation |
| Generating release metadata | Automation | Derived from validated inputs |
| Creating snapshot branches | Automation | Ensures immutability |
| Reviewing CHANGELOG content | Human | Requires judgment about clarity |
| Deciding when to release | Human | Business and coordination decision |
| Approving the Release PR | Human | Final review checkpoint |
| Publishing the release | Human | Intentional, irreversible action |

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
