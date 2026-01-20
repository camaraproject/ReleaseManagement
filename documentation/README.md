# CAMARA Release Management Documentation

This README is the **entry point** to the CAMARA Release Management documentation.
It explains how the release process works, how metadata is used, and where to go depending on what you want to do.

## What this documentation is

This documentation describes the **CAMARA release process** for API repositories, with a focus on:

- a metadata-driven release workflow
- clear separation between development and release preparation
- predictable automation and validation
- safe, repeatable release attempts

The **source of truth** for releases is always the repository itself (metadata files, branches, and tags). This documentation explains *how to work with that system*.

## What this documentation is not

- It is not a step-by-step Git or GitHub tutorial
- It does not replace repository governance or TSC decisions
- It does not describe CI or GitHub Actions implementation details

---

## I want to...

### ...understand the basics

- Understand core terms like *release*, *release tag*, and *API version*
  → [release-process/terminology.md](release-process/terminology.md)

- Get a high-level overview of how releases work in CAMARA
  → [release-process/overview.md](release-process/overview.md)

### ...plan or declare a release

- Understand the release lifecycle from planning to publication
  → [release-process/lifecycle.md](release-process/lifecycle.md)

- Learn about available release types (pre-release, public, maintenance)
  → [release-process/release-types.md](release-process/release-types.md)

- Prepare or update `release-plan.yaml`
  → [metadata/release-plan.md](metadata/release-plan.md)

### ...fix a validation error during planning or development

- Understand why CI validation failed or a PR is blocked on `main`
  → [metadata/validation-and-freeze.md](metadata/validation-and-freeze.md)

### ...understand release automation behavior

- What automation does (and does not do)
  → [automation/automation-overview.md](automation/automation-overview.md)

- How releases are triggered (release issue, commands, entry points)
  → [automation/triggers-and-entry-points.md](automation/triggers-and-entry-points.md)

- How snapshot branches and immutability work
  → [automation/snapshot-and-branch-model.md](automation/snapshot-and-branch-model.md)

- **(Release Management)** How to review the Release PR and publish the draft release
  → [automation/triggers-and-entry-points.md](automation/triggers-and-entry-points.md)

### ...recover from an unsuccessful release attempt

- Understand reasons why a started release attempt needs to be abandoned
  → [automation/snapshot-and-branch-model.md](automation/snapshot-and-branch-model.md)

- Recover safely from an abandoned or unsuccessful release attempt
  → [automation/failure-and-recovery.md](automation/failure-and-recovery.md)

### ...check API readiness

- Understand the readiness model behind API releases
  → [readiness/readiness-model.md](readiness/readiness-model.md)

- Understand the API Readiness Checklist
  → [readiness/api-readiness-checklist.md](readiness/api-readiness-checklist.md)

### ...understand roles and responsibilities

- API repository roles (codeowners, maintainers)
  → [roles/api-repository-roles.md](roles/api-repository-roles.md)

- Release Management Working Group roles
  → [roles/release-management-roles.md](roles/release-management-roles.md)

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

These documents are **deprecated** and replaced by the documentation in this folder. See [deprecated/README.md](deprecated/README.md) for details.

---

## Migration status

- The metadata-driven release process is being rolled out incrementally
- Legacy documents are kept temporarily to avoid breaking links
- Over time, the documents in this folder become the authoritative reference

---

**If you are unsure where to start:**
Start with [release-process/terminology.md](release-process/terminology.md), then [release-process/overview.md](release-process/overview.md).
