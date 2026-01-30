# CAMARA Release Management Documentation – Proposed Scaffold

This document proposes a **clean, forward-looking documentation scaffold** for the CAMARA Release & Metadata-driven workflow.

It is intended as a **complete alternative structure** to the documentation introduced in PR #360, while explicitly supporting a **migration phase** where legacy documents and incoming links must remain valid.

---

## Design Constraints (Agreed)

The following constraints are explicitly incorporated into the structure:

- **SupportingDocuments/**\*\* stays\*\*

  - It exists in all repositories via the standard template
  - It is not part of the new documentation system
  - Its contents are not restructured or rewritten

- **Existing documents must remain addressable**

  - Many have inbound links (from issues, wikis, presentations)
  - They must either:
    - stay in place unchanged, or
    - be replaced by **document stubs** replacing and pointing to the deprecated document in their new location (the deprecated/ folder).

- **No hard breaks during migration**

  - New documentation coexists with legacy material
  - Deprecation is explicit, not implicit

---

## Proposed Directory Structure

```
ReleaseManagement/documentation/
├── README.md                          # Entry point & routing guide
│
├── release-process/                   # What happens, when, and why
│   ├── terminology.md                 # Key terms & mental models (release vs API version)
│   ├── overview.md
│   ├── lifecycle.md
│   ├── release-types.md
│   ├── maintenance-releases.md
│   └── migration-and-adoption.md
│
├── metadata/                          # Declarative inputs & generated outputs
│   ├── concepts.md
│   ├── release-plan.md
│   ├── release-metadata.md
│   └── validation-and-freeze.md
│
├── readiness/                         # API quality & readiness gates
│   ├── readiness-model.md
│   ├── api-readiness-checklist.md
│   └── status-progression.md
│
├── automation/                        # Automation behavior & guarantees
│   ├── automation-overview.md
│   ├── release-issue-and-commands.md
│   ├── snapshot-and-release-branches.md
│   └── failure-and-recovery.md
│
├── roles/                             # Who does what, and when
│   ├── api-repository-roles.md         # Codeowners, maintainers, contributors
│   └── release-management-roles.md    # Release reviewers & release managers
│
├── deprecated/                        # Superseded documents (link targets)
│   ├── README.md
│   ├── API-Readiness-Checklist.md
│   ├── API_Release_Guidelines.md
│   └── CHANGELOG_TEMPLATE.md
│
└── SupportingDocuments/               # Existing template folder (unchanged)
```

---

## Deprecation & Link-Stability Strategy

### 1. Files that currently exist at top level

For documents that currently live directly under `documentation/`:

- They **must remain reachable at their original paths** during migration
- Two acceptable patterns (choose one policy and apply consistently):

**Option A – Keep file, add deprecation banner**

- File remains where it is
- A short banner at the top states:
  - Document is deprecated
  - Canonical replacement location
  - Date / phase of deprecation

**Option B – Replace with stub redirect**

- Original file is replaced with a short Markdown file
- Content:
  - Deprecation notice
  - Link to old document moved under `deprecated/`

This avoids breaking inbound links while making status explicit.

**Current preference (not final):** use **Option B (stubs)** for link stability and clarity, unless we find a concrete reason to keep full content in-place.

### 2. `deprecated/` folder role

- Acts as the **archive** of superseded material
- Is explicitly linked from the new `README.md`
- Makes deprecation intentional and visible
- Prevents legacy documents from being silently lost

---

## Documentation Philosophy (Reminder)

- One document = one responsibility
- Metadata files are **user interfaces**, not just configuration
- Declarative intent over procedural instructions
- Automation behavior is explained, not reimplemented
- Migration clarity is more important than structural purity

---

## Next Iteration Hooks

Suggested areas for your inline comments:

- Folder naming (`release-process` vs `process`, etc.)
- Whether any documents should be merged or split
- Placement and handling of `API-Readiness-Checklist`
- Whether `deprecated/` should mirror exact filenames or use aliases
- README routing wording and granularity

(We can then iterate section-by-section.)

---

## Per-Document Outlines

The following outlines define **scope, audience, and boundaries** for each proposed document. They are intentionally explicit to avoid overlap and scope creep.

---

### `README.md` (top-level)

**Audience:** Codeowners, maintainers, reviewers, release managers\
**Responsibility:** Single entry point and routing hub

---

## Draft README.md (Sketch)

> This README is the **entry point** to the CAMARA Release Management documentation.\
> It explains how the release process works, how metadata is used, and where to go depending on what you want to do.

### What this documentation is

This documentation describes the **CAMARA release process** for API repositories, with a focus on:

- a metadata-driven release workflow
- clear separation between development and release preparation
- predictable automation and validation
- safe, repeatable release attempts

The **source of truth** for releases is always the repository itself (metadata files, branches, and tags). This documentation explains *how to work with that system*.

### What this documentation is not

- It is not a step-by-step Git or GitHub tutorial
- It does not replace repository governance or TSC decisions
- It does not describe CI or GitHub Actions implementation details

---

## I want to…

### …understand the basics

- Understand core terms like *release*, *release tag*, and *API version*\
  → `release-process/terminology.md`

- Get a high-level overview of how releases work in CAMARA\
  → `release-process/overview.md`

### …plan or declare a release

- Understand the release lifecycle from planning to publication\
  → `release-process/lifecycle.md`

- Learn about available release types (pre-release, public, maintenance)\
  → `release-process/release-types.md`

- Prepare or update `release-plan.yaml`\
  → `metadata/release-plan.md`

### …fix a validation error during planning or development

- Understand why CI validation failed or a PR is blocked on `main`\
  → `metadata/validation-and-freeze.md`



### …understand release automation behavior

- What automation does (and does not do)\
  → `automation/automation-overview.md`

- How releases are triggered (release issue, commands, entry points)\
  → `automation/release-issue-and-commands.md`

- How snapshot branches and immutability work\
  → `automation/snapshot-and-release-branches.md`

- **(Release Management)** How to review the Release PR and publish the draft release\
  → `automation/release-issue-and-commands.md`

### …recover from an unsuccessful release attempt

- Understand reasons why a started release attempt needs to be abandoned\
  → `automation/snapshot-and-release-branches.md`

- Recover safely from an abandoned or unsuccessful release attempt\
  → `automation/failure-and-recovery.md`

### …check API readiness

- Understand the readiness model behind API releases\
  → `readiness/readiness-model.md`

- Understand the API Readiness Checklist\
  → `readiness/api-readiness-checklist.md`

### …understand roles and responsibilities

- API repository roles (codeowners, maintainers)\
  → `roles/api-repository-roles.md`

- Release Management Working Group roles\
  → `roles/release-management-roles.md`

---

## How the pieces fit together

- **Release process** describes *what happens and when*
- **Metadata** describes *declared intent* and *recorded outcomes*
- **Readiness** defines *quality and maturity gates*
- **Automation** enforces rules and produces repeatable release artifacts

These parts are intentionally separated but work together.

---

## Transitional and deprecated documents

During migration, some legacy documents are still present for link stability:

- `API-Readiness-Checklist.md`
- `API_Release_Guidelines.md`
- `CHANGELOG_TEMPLATE.md`

These documents are **deprecated** and replaced by the documentation in this folder. See `deprecated/README.md` for details.

---

## Migration status

- The metadata-driven release process is being rolled out incrementally
- Legacy documents are kept temporarily to avoid breaking links
- Over time, the documents in this folder become the authoritative reference

---

**If you are unsure where to start:**\
Start with `release-process/terminology.md`, then `release-process/overview.md`.

---

**Must NOT cover**

- Release process details
- Metadata field explanations

---

## release-process/

### `terminology.md`

**Audience:** Newcomers, codeowners, maintainers, reviewers\
**Responsibility:** Canonical terminology and mental models for the release system

**Outline**

- Why terminology matters (common confusions)
- Core entities and how they relate
  - Repository release vs API version
  - Release tag (`rX.Y`) vs API SemVer (`X.Y.Z`)
  - Release type vs API status
  - Snapshot / release attempt vs published release
  - `release-plan.yaml` (intent) vs `release-metadata.yaml` (record)
- Naming conventions and examples (minimal)
- “If you remember one thing…” summary

**Must NOT cover**

- Full process walkthrough
- Schema reference or field-by-field definitions

---

### `overview.md`

**Audience:** Codeowners, maintainers\
**Responsibility:** High-level mental model of the release process

**Outline**

- Why CAMARA has a structured release process
- Core principles (separation of concerns, immutability, automation)
- What a “release” means in CAMARA
- How this differs from ad-hoc tagging

**Must NOT cover**

- Step-by-step workflows
- YAML metadata details

---

### `lifecycle.md`

**Audience:** Codeowners, maintainers\
**Responsibility:** Describe the lifecycle of a release from planning to publication

**Outline**

- Development on `main`
- Declaring release intent
- Snapshot / release preparation
- Review and finalization
- Post-release actions

**Must NOT cover**

- Trigger syntax
- CI implementation details

---

### `release-types.md`

**Audience:** Codeowners, release managers\
**Responsibility:** Explain available release types and their intent

**Outline**

- Overview of release types
- Pre-release vs public release
- Maintenance releases
- How release type constrains readiness

**Must NOT cover**

- Validation matrices
- Branching mechanics

---

### `maintenance-releases.md`

**Audience:** Maintainers, release managers\
**Responsibility:** Explain maintenance / patch release model

**Outline**

- What qualifies as a maintenance release
- Maintenance branches vs `main`
- Metadata implications
- When *not* to use maintenance releases

**Must NOT cover**

- CI job details
- Hotfix governance rules

---

### `migration-and-adoption.md`

**Audience:** All roles\
**Responsibility:** Explain coexistence of old and new release processes

**Outline**

- Why migration is phased
- What is authoritative today
- How legacy docs map to new docs
- Expected adoption milestones

**Must NOT cover**

- Historical release timelines

---

## metadata/

### `concepts.md`

**Audience:** Codeowners, reviewers\
**Responsibility:** Explain metadata as declarative release intent

**Outline**

- Metadata as UX, not configuration
- Planning vs generated metadata
- Source-of-truth rules
- Immutability and traceability

**Must NOT cover**

- Field-by-field schema reference

---

### `release-plan.md`

**Audience:** Codeowners\
**Responsibility:** How to use `release-plan.yaml`

**Outline**

- Purpose and ownership
- Repository-level intent
- API-level intent
- Dependencies
- Common mistakes

**Must NOT cover**

- Release creation steps
- Generated values

---

### `release-metadata.md`

**Audience:** Release managers, tooling authors\
**Responsibility:** Explain generated `release-metadata.yaml`

**Outline**

- When and how it is generated
- Relationship to tags and snapshots
- How it is used for reporting and audit

**Must NOT cover**

- Editing instructions

---

### `validation-and-freeze.md`

**Audience:** Codeowners, maintainers\
**Responsibility:** Explain validation, blocking, and freeze behavior

**Outline**

- Validation vs enforcement
- Status compatibility
- Metadata-only vs mixed PRs
- Configuration freeze during release
- Recovery paths

**Must NOT cover**

- CI job names

---

## readiness/

### `readiness-model.md`

**Audience:** Codeowners\
**Responsibility:** Conceptual readiness model

**Outline**

- Why readiness exists
- API status levels
- Repository readiness vs API readiness

**Must NOT cover**

- Checklist details

---

### `api-readiness-checklist.md`

**Audience:** Codeowners, reviewers\
**Responsibility:** Canonical explanation of the checklist

**Outline**

- Purpose of the checklist
- How it maps to statuses
- How it is reviewed

**Must NOT cover**

- Release process explanation

---

### `status-progression.md`

**Audience:** Codeowners\
**Responsibility:** Explain allowed API status transitions

**Outline**

- Draft → Alpha → RC → Public
- Promotion expectations
- Locking behavior after public release

**Must NOT cover**

- CI internals

---

## automation/

### `automation-overview.md`

**Audience:** All roles\
**Responsibility:** Explain what automation does and guarantees

**Outline**

- Automation as co-reviewer (why it exists)
- Two automation workflows
  - Continuous validation for PRs to `main` (planning & development)
  - Release automation for creating and publishing releases (snapshot-based)
- What automation owns vs humans
- Guarantees and non-goals

**Must NOT cover**

- Implementation details

---

### `release-issue-and-commands.md`

**Audience:** Codeowners, maintainers, release managers\
**Responsibility:** Happy-path interaction points for release automation (how humans drive a release)

**Outline**

- Entry points and intent vs state
- Release Issue
  - Purpose (UI + audit trail; not the source of truth)
  - Commands (what they do at a high level)
- Release PR (release preparation PR)
  - What to do in the PR (what is reviewable)
  - Who must approve (release reviewers vs release managers; repo codeowners as needed)
  - Who merges and what merge means (moves snapshot forward; not yet published)
- Draft release publication (final human control point)
  - What “draft” means
  - Who publishes and what checks happen before publish
  - What publish does (creates final tag / public release)

**Must NOT cover**

- State machine internals
- GitHub Actions / CI job naming

---

### `snapshot-and-release-branches.md`

**Audience:** Maintainers, release managers\
**Responsibility:** Explain snapshot branches and immutability

**Outline**

- Snapshot concept
- Branch types and ownership
- Discard and retry model

**Must NOT cover**

- Git tutorials

---

### `failure-and-recovery.md`

**Audience:** Codeowners, maintainers\
**Responsibility:** Safe recovery paths

**Outline**

- Common failure scenarios
- Abandoning and retrying releases
- What *not* to do

**Must NOT cover**

- Governance escalation

---

## roles/

### `api-repository-roles.md`

**Audience:** Codeowners, maintainers\
**Responsibility:** Repository-level responsibilities related to API development and release preparation

**Outline**

- Codeowners vs maintainers (practical reality)
- Write access and responsibility boundaries
- Declaring release intent
- Maintaining `release-plan.yaml`
- Responding to CI validation and blockers

**Must NOT cover**

- Cross-repository coordination
- Meta-release or process governance

---

### `release-management-roles.md`

**Audience:** Release Management Working Group\
**Responsibility:** Roles related to coordinating, reviewing, and steering releases across repositories

**Internal role differentiation**

- *Release reviewers* (GitHub team: `release-management_reviewers`)
- *Release managers* (GitHub team: `release-management_codeowners`)

**Outline**

- Purpose of the Release Management Working Group
- Release reviewers
  - What they review
  - What they do **not** decide
- Release managers
  - Process ownership and coordination
  - Exceptional interventions
- Interaction with API repository roles

**Must NOT cover**

- TSC governance
- Repository-level how-tos


