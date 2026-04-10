# Commonalities Consumption and Bundling Design

> **Scope:** Design proposal for consuming `CAMARA_common.yaml` and similar shared schemas in CAMARA API repositories, including validation, synchronization, reviewer visibility, and release-time bundling.
>
> **Related discussion:** [Commonalities issue #577](https://github.com/camaraproject/Commonalities/issues/577)

---

## Executive Summary

Several CAMARA API repositories need a supported way to consume shared schemas from `CAMARA_common.yaml` without copy-paste. This became urgent after recent Commonalities schema updates, including OWASP-related changes, because repeated manual copying into API repositories does not scale and destroys provenance.

This proposal recommends:

1. **Controlled local copy on `main`:** API repositories consume Commonalities schemas through a local cached copy, referenced via relative `$ref`.
2. **`release-plan.yaml` as source of truth:** `dependencies.commonalities_release` defines the intended Commonalities dependency.
3. **CI-managed synchronization:** the local cached Commonalities file is treated as cache, not as a manually maintained source file.
4. **Source-only `main`, bundled release artifacts:** bundled API definitions are not committed on `main`, but are generated for PR review and committed on snapshot/release branches and tags.
5. **In-place replacement:** source files and bundled files occupy the same path (`code/API_definitions/api-name.yaml`). On `main` the file may contain external `$ref` to `common/` or `modules/`; on snapshot/release branches these are replaced with the referenced content. There is no separate source or output directory.

This design aligns Commonalities consumption with the release automation concepts already introduced for CAMARA release preparation.

---

## 1. Motivation and Problem Statement

Section 2.1 of the CAMARA API Design Guide points to `CAMARA_common.yaml` as a shared source of common schemas, but does not define a standard consumption model. In practice this has led to:

- copy-paste of shared schemas into API repositories
- unclear provenance of consumed Commonalities content
- avoidable maintenance effort whenever Commonalities evolves
- inconsistent tooling support across repositories

The immediate pressure is increased by recent updates in `CAMARA_common.yaml`, where API repositories should be able to adopt shared schema changes without re-solving the same problem by local duplication.

---

## 2. Design Goals

The solution should provide:

- **Traceability:** the exact Commonalities release used by an API repository must be identifiable
- **Tooling compatibility:** source files must work with standard OpenAPI tooling and local development workflows
- **Reviewer visibility:** codeowners must be able to inspect the effective API impact, including changes caused by shared schema updates
- **Release artifact quality:** published releases must expose complete standalone API definitions
- **Identical layout across branches:** the repository structure does not change between `main` and release branches — only file content changes (source → bundled). Tools and processes that operate on `code/API_definitions/` work the same way regardless of branch.
- **Low contributor friction:** the model should remain understandable and practical for normal API repository contributors

---

## 3. Repository Model on `main`

API repositories should adopt a controlled local copy model with a canonical layout:

```text
code/
  API_definitions/   # source API definitions
  common/            # local cached copy of CAMARA_common.yaml
  modules/           # optional project-local reusable schemas
```

Rules on `main`:

- API source files reference Commonalities content via relative `$ref` into `code/common/`
- project-local reusable schemas may be placed in `code/modules/` and also referenced via relative `$ref`
- remote URL-based `$ref` are not used for normative schema consumption
- bundled standalone API definitions are not committed on `main`

### 3.1 Source of Truth

`release-plan.yaml.dependencies.commonalities_release` is the authoritative declaration of the intended Commonalities dependency.

The local `code/common/CAMARA_common.yaml` file is only a cache of that declaration. It is not a manually curated source.

### 3.2 Cache Ownership

Manual edits to `code/common/CAMARA_common.yaml` are not supported. The cache is expected to be synchronized by automation.

---

## 4. Dependency Synchronization Model

The synchronization mechanism should be permanent, not a one-time migration helper.

Supported triggers:

- automatic trigger after relevant `release-plan.yaml` changes
- manual trigger to re-sync `code/common/CAMARA_common.yaml` later if required

Expected behavior:

- synchronization is idempotent
- if no change is needed, no PR is created
- the synchronization result is surfaced through a normal PR
- snapshot creation validates that the cache is exactly in sync with the declared dependency

This follows an already established principle in CAMARA release discussions:

- `release-plan.yaml` defines the intended target
- PR validation on `main` reports what still needs to change before a release can be created
- the final hard block occurs at snapshot creation time

An out-of-sync Commonalities cache is therefore expected to be:

- **a warning on `main`**
- **a blocker for snapshot creation**

---

## 5. Bundling Decision

Bundled API definitions should **not** be committed on `main`.

Instead:

- `main` keeps source files only (containing `$ref` to `common/` and `modules/`)
- PR workflows generate bundled artifacts and bundled diffs for reviewer visibility
- release automation replaces external `$ref` with the referenced content in place on snapshot/release branches and tags — the file path (`code/API_definitions/api-name.yaml`) stays the same

### 5.1 Rationale

Committing generated bundled files on `main` would:

- pollute PRs and git history with generator output
- increase merge conflicts
- obscure the real source-level changes
- create a risk that contributors start editing generated files directly

Keeping source only on `main` preserves a clean development model while still allowing reviewers and consumers to see the complete API through generated outputs.

---

## 6. Reviewer Visibility and Diff Priorities

The issue discussion highlighted that codeowners want to see the effective API changes, especially when `CAMARA_common.yaml` changes. That need is valid, but it does not require committing bundled files on `main`.

PR workflows should therefore provide review surfaces in the following priority order:

1. **Source diff**
   The normal git diff remains the primary review surface.

2. **Bundled artifact**
   The fully bundled API for the PR head should be uploaded as an artifact for each affected API.

3. **Bundled diff**
   A diff between the bundled API from the PR base and the bundled API from the PR head should be generated for affected APIs.

4. **Optional API-aware summary**
   A compact semantic summary of changes in paths, operations, schemas, responses, and examples may be added later.

This gives reviewers the complete effective API view without polluting `main`.

---

## 7. Validation Policy

Validation should depend on the operational context.

### 7.1 PR Validation on `main`

Purpose:

- validate declared intent
- provide early feedback
- allow merge of planned-but-not-yet-releaseable states

Behavior:

- invalid configuration remains blocking
- most release-readiness issues are warnings
- out-of-sync `code/common/CAMARA_common.yaml` is a warning, not a blocker
- warning messages should point to the expected sync PR or manual sync trigger

Mental model:

- `release-plan.yaml` defines the target state
- PR validation indicates what still needs to be changed before a release snapshot can be created

### 7.2 Validation Before Snapshot Creation

Purpose:

- ensure the exact source commit intended for release is ready

Behavior:

- previously tolerated release-readiness warnings become blockers unless explicitly allowed
- local source references must resolve
- `code/common/CAMARA_common.yaml` must exactly match the declared `commonalities_release`
- APIs intended for release must pass the stricter release profile

Mental model:

- the last PR before snapshot creation should be green
- technically, snapshot creation still re-validates the exact source commit

### 7.3 Snapshot/Release Artifact Validation

Purpose:

- validate the bundled release artifact rather than the editable source state

Behavior:

- bundled API definitions must validate as standalone artifacts
- release metadata and dependency provenance must be correct
- release branches and tags expose consumer-facing artifacts, not editable source structure

---

## 8. Commonalities Content Expectations

`CAMARA_common.yaml` must be directly consumable via `$ref` without preprocessing. This requires two changes on the Commonalities side, which can be addressed independently:

### 8.1 Placeholder Removal

`CAMARA_common.yaml` currently contains placeholder patterns (`{{SPECIFIC_CODE}}`, `{{field}}`) inside Generic error response schemas and examples. These make the file unparseable as a `$ref` target because the placeholder values are not valid OpenAPI content.

The recommended approach is to **comment out** placeholder-containing lines rather than delete them:

- Commented lines are ignored by YAML parsers, bundling tools, and Spectral
- The placeholders remain visible as human-readable documentation, showing API teams where to add API-specific content
- The Generic error responses retain their common error codes (e.g., `INVALID_ARGUMENT`, `NOT_FOUND`) as valid enum values
- The change is minimal — approximately 30 lines across the file

This makes `CAMARA_common.yaml` immediately consumable without requiring structural refactoring.

### 8.2 API-Specific Error Code Extension

APIs need a way to add their own error codes beyond the common ones provided by the Generic responses. This is a separate concern from placeholder removal — it does not need to be solved before `CAMARA_common.yaml` becomes consumable.

Possible extension mechanisms include `allOf` composition, property overrides, or defining API-specific responses that reference only the shared `ErrorInfo` schema. The right approach may vary by API pattern and can be worked out incrementally as APIs adopt the `$ref` model.

Example/template API source files should demonstrate the recommended extension pattern once it is established.

---

## 9. Relationship to Release Automation

The current release automation direction already provides part of the required model:

- `release-plan.yaml` already carries `dependencies.commonalities_release`
- release-state derivation already exposes that dependency
- release automation already resolves the semantic Commonalities version
- release metadata already records dependency provenance
- source-commit traceability already exists through `src_commit_sha` and `source/rX.Y` reference tags

The main missing pieces are:

- synchronization of the local Commonalities cache
- bundling/dereferencing of API source files during snapshot creation
- PR-time generation of bundled review artifacts and bundled diffs

### 9.1 Release Branch Strategy

The release process applies in-place replacement (see executive summary, point 5):

- on `main`, `code/API_definitions/api-name.yaml` is the source file which may contain external `$ref` to `common/` or `modules/`
- on snapshot/release branches, the same file at the same path is replaced with the standalone bundled version
- the `common/` and `modules/` directories are removed from the snapshot branch since their content is now embedded in the bundled files

This follows the same pattern as the existing release automation transformer, which replaces `info.version` and server URLs in place on the snapshot branch. No separate output directory is created.

This keeps the familiar filename in all contexts while maintaining a clean source model on `main`.

---

## 10. Bridge Strategy Before Validation Framework v1

A broader `validation-framework-v1` is expected to take time. It should eventually provide:

- one shared validation core
- context-specific profiles
- a common findings model for hints, warnings, and errors
- multiple reporting surfaces
- replacement of MegaLinter-based validation

Before that is ready, a minimal bridge can still enable the Commonalities consumption model.

### 10.1 Minimal Bridge Scope

Short-term work should:

- keep `pr_validation v0` mostly intact
- introduce narrow pilot support for repositories adopting the local Commonalities model
- add synchronization support for `code/common/CAMARA_common.yaml`
- add strict pre-snapshot validation and bundling into release automation

This allows early adoption for pilot repositories without waiting for the complete validation rewrite.

### 10.2 Tooling Ref Consistency

If pilot repositories use non-`v0` refs of `camaraproject/tooling`, each reusable workflow must be internally consistent with its own tooling ref.

This is especially relevant for PR validation:

- changing only the caller ref is not sufficient if the workflow still hardcodes internal calls to `@v0`
- pilot behavior should therefore resolve its internal actions, scripts, and configuration from the same tooling ref

This matters for cooperation between PR validation and release automation during the pilot phase.

---

## 11. Recommended Phased Plan

### Phase 1: Decision and Pilot Preparation

- confirm the controlled local copy model
- confirm source-only `main` plus bundled release artifacts
- align Commonalities on direct consumability of shared content
- select pilot repositories

### Phase 2: Pilot Implementation

- implement sync PR generation for `code/common/CAMARA_common.yaml`
- generate bundled artifacts and bundled diffs in PR workflows
- add strict pre-snapshot validation and bundling to release automation

### Phase 3: Generalization

- introduce the shared validation core in validation framework v1
- replace MegaLinter-centered PR validation
- roll the model out across API repositories

---

## 12. Decisions Requested

1. Confirm the controlled local copy model as the standard way to consume Commonalities schemas.
2. Confirm that bundled API definitions are not committed on `main`.
3. Confirm that PR workflows must provide bundled artifacts and bundled diffs for reviewer visibility.
4. Confirm that an out-of-sync Commonalities cache is a warning on `main`, but a blocker for snapshot creation.
5. Confirm that Commonalities should evolve `CAMARA_common.yaml` toward direct consumability without placeholders.

---

## 13. Expected Follow-Up Artifacts

The expected follow-up artifacts around this design are:

- a summary comment in [Commonalities issue #577](https://github.com/camaraproject/Commonalities/issues/577) linking to this design and the ReleaseManagement discussion
- a ReleaseManagement enhancement issue that serves as the umbrella for implementation work
- implementation issues in tooling, Commonalities, and pilot API repositories linked back to that umbrella
