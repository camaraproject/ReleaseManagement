# CAMARA Automated Release Workflow - Implementation Plan

## Table of Contents
- [Overview](#overview)
- [Key Design Decisions](#key-design-decisions)
- [Timeline Alignment](#timeline-alignment)
- [Phase 1: Concept & Preparation](#phase-1-concept--preparation-nov---dec-10-2025)
- [Phase 2: Mass Rollout](#phase-2-mass-rollout-dec-2025---jan-15-2026)
- [Phase 3: Validation Framework](#phase-3-validation-framework-jan-2026-4-5-weeks)
- [Phase 4: Release Automation](#phase-4-release-automation-jan-feb-2026-6-weeks)
- [Phase 5: Release Operations](#phase-5-release-operations-march-2026-8-10-weeks)
- [Phase 6: Maintenance](#phase-6-maintenance-spring26---fall26)
- [Validation Architecture](#validation-architecture)
- [Repository Changes Required](#repository-changes-required)
- [Implementation Issues](#implementation-issues-sub-issues-to-191)
- [Open Questions & Risk Areas](#open-questions--risk-areas)
- [Critical Files](#critical-files)

## Overview

This document provides a phased implementation plan for automating the CAMARA release workflow as defined in [CAMARA-Release-Workflow-and-Metadata-Concept.md](https://github.com/camaraproject/ReleaseManagement/blob/main/documentation/SupportingDocuments/CAMARA-Release-Workflow-and-Metadata-Concept.md).

**Implementation Timeline**: November 2025 → Fall 2026 (6 phases)
**Target Repositories**: camaraproject/tooling, camaraproject/ReleaseManagement
**Scope**: Replace manual wiki-based release process with metadata-driven automation

## Key Design Decisions

1. **Mass Rollout Strategy**: Automated campaign to migrate all ~61 repositories by Jan 15 (replacing wiki trackers)
2. **Minimal Initial Validation**: Use lightweight validation for rollout (Schema + Existence + Consistency); full framework follows
3. **Replace monolithic validator**: New modular architecture with Spectral + custom validators
4. **Direct linter integration**: Use YAML-lint, Spectral, Gherkin-lint directly (not MegaLinter wrapper)
5. **Defer complex dependencies**: Cross-API $ref resolution postponed to later phase (separate concept needed)
6. **Severity matrix**: error/warning/info/hint with context-aware enforcement

## Timeline Alignment

| Milestone | Date | Phase Deliverable |
|-----------|------|-------------------|
| **All Hands Call** | Dec 10, 2025 | Present release-plan.yaml concept |
| **Spring26 M1** | Dec 15, 2025 | Phase 1 complete, Phase 2 (Mass Rollout) started |
| **Fall26 M0 (Kick-off)** | Mid-Jan 2026 | Phase 2 complete (adoption) + Phase 3 started |
| **Spring26 M3** | Jan 31, 2026 | Phase 3 complete (validation framework stable) |
| **Spring26 M4** | Mar 31, 2026 | Phase 4 functional (release automation) |
| **Fall26 M1** | Apr 30, 2026 | Phase 5 complete (post-release workflows) |
| **Fall26 M3 (RC)** | Jun 15, 2026 | Phase 6 complete (maintenance workflows) |
| **Fall26 M4 (Public)** | Sep 30, 2026 | Mandatory adoption |

---

## Phase 1: Concept & Preparation (Nov - Dec 10 2025)
**Status**: Completed
**Deliverables**:
- Concept definition (`CAMARA-Release-Workflow-and-Metadata-Concept.md`)
- Schema definitions (Release Plan, Release Metadata)
- Agreement on Mass Rollout Strategy
- Presentation Materials (for Dec 10 All Hands Call)


#### 1.1 Metadata Schemas (Finalized)
**Location**: `camaraproject/ReleaseManagement/artifacts/metadata-schemas`

- `release-plan-schema.yaml` - Structure for planning metadata on main
- `release-metadata-schema.yaml` - Structure for generated release metadata

**Key Fields in release-plan.yaml**:
```yaml
repository:
  release_track: "meta-release" # none|sandbox|meta-release
  meta_release: "Fall26"  # Required if release_track is meta-release, omit otherwise
  release_tag: "r4.1"
  release_readiness: "pre-release-alpha"  # none|pre-release-alpha|pre-release-rc|public-release|patch-release

dependencies:
  commonalities_release: "r3.4"  # Concrete Commonalities release (not meta-release reference)
  identity_consent_management_release: "r3.4"  # Concrete ICM release
  # Rationale: APIs decide when ready to validate against newest Commonalities
  # Meta-release reference would cause uncontrolled updates

apis:
  - api_name: "location-verification"
    target_version: "3.2.0"  # SemVer base (extension auto-calculated)
    api_status: "rc"  # draft|alpha|rc|public
    main_contacts: ["githubUser1", "githubUser2"]
```

**Rationale**: Schema must be well-designed from start; repositories will adopt this format immediately.

**Schema Validation**:
- **Strategy**: Initial centralized validation included in PR workflow (see Phase 3)
- As soon as possible: integrated into CI validation (Phase 3)

#### 1.2 Presentation Materials
**For All Hands Call (Dec 10)**:
- Concept overview slides
- Demo: release-plan.yaml example
- Benefits: automated tracking, wiki deprecation
- Timeline and participation requirements

## Phase 2: Mass Rollout (Dec 2025 - Jan 15 2026)

### Objectives
1. Get `release-plan.yaml` added to all ~61 repositories using automated campaign
2. Replace wiki tracker with Release Progress Tracker (immediate value)

### Deliverables

#### 2.1 Adoption Package
**Location**: `camaraproject/ReleaseManagement/documentation/`

**Contents**:
- Pre-populated `release-plan.yaml` template for each repository
- Migration guide for converting wiki tracker to YAML
- **Delivery Method**: Delivered via automated PR to each repository (see Mass Rollout Campaign)
- **Validation**: Integrated into central `pr-validation` workflow

#### 2.2 Release Progress Tracker Integration
**Location**: `camaraproject/project-administration` (workflow and data) -> `camaraproject/camaraproject.github.io` (viewer)

**Integration Point**: Meta-release aggregator already planned in project-administration as "Release Progress Tracker"

**Immediate Value**: Replaces manual wiki tracker API tables as soon as repositories add `release-plan.yaml`

**Goal**: Mass Rollout to all ~61 repositories (43 released + 18 new) by Jan 15 (Fall26 M0 target). Replaces wiki tracker completely.

#### 2.3 Mass Rollout Campaign (NEW)
**Location**: `camaraproject/project-administration/campaigns/`

**Activities**:
- Scripted generation of `release-plan.yaml` from `releases-master.yaml`
- Automated PR creation across all ~61 repositories using existing campaign tooling (reusing actions from existing campaigns)
- Minimal validation ("Sanity Check") before merge:
    - Reuse `scripts/validate-release-plan.py` (from metadata-schemas)
    - Schema validation, file existence, and basic consistency
    - **Note**: Complements (does not replace) existing MegaLinter checks. Does not yet enable strict status-based validation differentiation.
- **Review Strategy**:
    - Standard Repos (No Spring26 tracker): Fast-track/Auto-merge
    - Complex Repos (With Spring26 tracker): Manual review required to ensure alignment
    - Edge case will be supported by ReleaseManagement

#### 2.4 Wiki Integration (Moved from Phase 5)
**Note**: Wiki remains for extensive documentation and meta-release pages (timeline, etc.)

**Actions**:
- Embed Release Progress Tracker into wiki via iframe (from camaraproject.github.io)
- Deprecate manual API tracker tables in wiki
- Update documentation references



### Success Criteria
- [ ] **Metadata schemas finalized and documented** (CRITICAL - blocks everything)
- [ ] **Concept presented at All Hands Call (Dec 10)**
- [ ] **Release Progress Tracker fetching release-plan.yaml files** (CRITICAL for wiki replacement)
- [ ] **All ~61 repositories have added release-plan.yaml** (complete wiki replacement)
- [ ] **Wiki API tracker tables deprecated with iframe to camaraproject.github.io**

---

## Phase 3: Validation Framework (Jan 2026, 4-5 weeks)

### Objectives
Build CI validation foundation on `main` with placeholder enforcement (C1 workflow). Must be stable by end-January for early adoption in Spring26 and for start of Fall26.

### Deliverables

#### 3.1 Validation Configuration Framework
**Location**: `camaraproject/tooling/validation/config/validation-rules.yaml`

Machine-readable validation rules inspired by [compliance-checks.yaml](https://github.com/hdamker/project-administration/blob/feat/repository-compliance-requirements-51/workflows/repository-compliance/config/compliance-checks.yaml):

```yaml
version: 1
metadata:
  description: CAMARA release validation rules
  severities: [error, warning, info, hint]
  contexts: [main_pr, release_branch, metadata_only_pr]

rule_groups:
  placeholder-validation:
    applies_to: [main_pr]
    rules:
      - id: info-version-wip
        severity: error
        validator: spectral
        message: "info.version must be 'wip' on main branch"

  api-status-coherence:
    applies_to: [main_pr]
    rules:
      - id: unchanged-api-not-modified
        severity: error
        validator: custom
        script: check-unchanged-apis.py
```

**Key Features**:
- Severity levels drive enforcement (error blocks PR)
- Context-aware rules (different checks for main vs release branches)
- Extensible configuration format (requires translation into Spectral rules and validation scripts)

**Validation Rules Schema**:
**Location**: `camaraproject/ReleaseManagement/schemas/validation-rules-schema.yaml`

#### 3.2 Enhanced Spectral Rules
**Location**: `camaraproject/tooling/linting/config/.spectral.yaml`

Extend existing [.spectral.yaml](https://github.com/camaraproject/tooling/blob/main/linting/config/.spectral.yaml) with:
- Placeholder validation rules (info.version must be "wip" on main)
- Server URL pattern enforcement (must contain placeholders on main)
- Branch-aware checks using custom functions

#### 3.3 Custom Validators
**Location**: `camaraproject/tooling/validation/validators/`

Python scripts for cross-file validation:
- `check-unchanged-apis.py` - Ensure unchanged APIs have no modifications
- `check-readiness-matrix.py` - Validate repository readiness vs API statuses
- `check-pr-mutual-exclusivity.py` - Block PRs changing both metadata and implementation
- `check-dependency-refs.py` - Validate Commonalities/ICM reference format
- `validate-status-promotion.py` - Check if status promotion is valid
- `check-test-alignment.py` - Validate test files exist for APIs

**Note**: This is an example list. Actual validators will be defined based on validation requirements analysis.

**Rationale**: Spectral operates on individual files; cross-file checks need custom code.

#### 3.4 PR Validation Workflow (C1) - Structure
**Location**: `camaraproject/tooling/.github/workflows/pr-validation-main.yml`

**Note**: This defines the validation workflow structure. Existing repositories already have `.github/workflows/pr-validation.yml` calling `camaraproject/tooling` reusable workflows (currently v0). Migration requires bumping to v1 for repositories adopting the new process.

Direct linter integration (no MegaLinter):

```yaml
jobs:
  metadata-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate release-plan.yaml
        run: |
          npm install -g ajv-cli
          ajv validate -s schemas/release-plan-schema.yaml -d release-plan.yaml

  yaml-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ibiqlik/action-yamllint@v3
        with:
          config_file: .yamllint.yml

  spectral-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: stoplight/spectral-action@latest
        with:
          file_glob: 'code/API_definitions/*.yaml'
          spectral_ruleset: 'https://raw.githubusercontent.com/camaraproject/tooling/main/linting/config/.spectral.yaml'

  gherkin-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          npm install -g gherkin-lint
          gherkin-lint code/Test_definitions/*.feature

  custom-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run custom validators
        run: |
          npm ci
          node validation/run-validators.js --context main_pr

  validation-summary:
    needs: [metadata-validation, yaml-lint, spectral-lint, gherkin-lint, custom-validation]
    runs-on: ubuntu-latest
    steps:
      - name: Aggregate results and post PR comment
        run: node validation/post-summary.js
```

**Performance Target**: < 3 minutes total

### Success Criteria
- [ ] Validation configuration format defined and schema validated
- [ ] Spectral rules extended with placeholder validation rules (exact number TBD)
- [ ] Custom validators implemented and tested (exact number based on requirements analysis)
- [ ] CI workflow (v1) runs successfully on test repository
- [ ] Performance target met (< 3 minutes)
- [ ] **Stable and ready for Fall26 cycle start (end-January)**

---

## Phase 4: Release Automation (Jan-Feb 2026, 6 weeks)

### Objectives
Implement automated release branch generation (C2 workflow). Target: functional by Feb 28 for Spring26 M4 public releases.

### Deliverables

#### 4.1 Version Calculator
**Location**: `camaraproject/tooling/scripts/calculate-versions.js`

Algorithm:
1. Fetch all release tags for repository via GitHub API
2. Parse `release-metadata.yaml` from each release
3. For each API, count previous extensions with same `target_version`
4. Increment counter (e.g., `3.2.0-rc.2` if `3.2.0-rc.1` exists)

**Edge Cases**:
- First release: Start at `-alpha.1` or `-rc.1`
- Version bump: Reset counter
- Skipped extensions: Continue sequence

#### 4.2 Dependency Resolver
**Location**: `camaraproject/tooling/scripts/resolve-dependencies.js`

Resolves concrete Commonalities/ICM release references to exact versions:
1. Read release reference (e.g., `r3.4`) from `release-plan.yaml`
2. Fetch specified Commonalities/ICM release from GitHub
3. Parse `release-metadata.yaml` from dependency releases
4. Format as `"rX.Y (semver)"` (e.g., `"r3.4 (1.2.0-rc.1)"`)

#### 4.3 Placeholder Replacement Engine
**Location**: `camaraproject/tooling/scripts/replace-placeholders.js`

Context-aware replacement:
- `info.version: "wip"` → `info.version: "3.2.0-rc.2"`
- `{{api_version}}` → `3.2.0-rc.2`
- `{{commonalities_release}}` → `1.2.0-rc.1`
- `{apiRoot}/api-name/vwip` → `{apiRoot}/api-name/v3` (or `/v0.5` for initial)
- `x-camara-commonalities: wip` → `x-camara-commonalities: 1.2.0-rc.1`

**Test Suite**: Comprehensive coverage of all placeholder patterns in YAML, markdown, URLs

#### 4.4 CHANGELOG Generator
**Location**: `camaraproject/tooling/scripts/generate-changelog.js`

Template-based approach:
1. Extract commits since last release using git log
2. Group by API (parse file paths)
3. Generate structured markdown with placeholders for manual refinement
4. Allow manual editing before release

**Quality**: Auto-generation creates baseline; manual refinement adds context.

#### 4.5 API Readiness Checklist Generator
**Location**: `camaraproject/tooling/scripts/generate-checklist.js`

Automated validation of 13 checklist items (example categorization):
- **Fully automated**: Items 1,4,5,7,10,11 (file existence, naming conventions)
- **Partially automated**: Items 2,3,8 (version checks, guidelines compliance)
- **Manual only**: Items 6,9,12,13 (user stories, test results, certification)

**Note**: Exact automation capabilities will be determined during implementation based on validation requirements analysis.

Output: Markdown checklist with Y/N/tbd status

#### 4.6 Release Branch Generator Workflow (C2)
**Location**: `camaraproject/tooling/.github/workflows/release-branch-generator.yml`

**Trigger**: Issue labeled `trigger-release` or `trigger-pre-release`

**Orchestration**:
1. Validate trigger permissions (maintainers only)
2. Create `release/rX.Y` branch from `main`
3. Run version calculator and dependency resolver
4. Replace all placeholders
5. Generate `release-metadata.yaml`
6. Generate CHANGELOG section
7. Generate API Readiness Checklists
8. Update README release information
9. Commit all changes
10. Create Release Preparation PR to release branch

**Reusable Workflow**: API repositories call this workflow from their own repos

### Success Criteria
- [ ] Version calculation tested on 3+ repositories with complex history
- [ ] Dependency resolution handles concrete release references
- [ ] Placeholder replacement handles all identified patterns correctly (comprehensive test coverage)
- [ ] CHANGELOG generation produces usable baseline
- [ ] Checklist validation runs and generates accurate Y/N/tbd status
- [ ] **End-to-end release branch creation tested on 2-3 early adopter repos by Feb 28**

---

## Phase 5: Release Operations (March 2026, 8-10 weeks)

### Objectives
Complete C1-C4 workflow; ensure Release Progress Tracker is fully featured.

### Deliverables

#### 5.1 Post-Release Workflow (C4)
**Location**: `camaraproject/tooling/.github/workflows/post-release-actions.yml`

**Jobs**:
1. **create-release-tag** - Git tag `rX.Y` on release branch HEAD
2. **publish-github-release** - GitHub Release with:
   - OpenAPI bundles (all $ref resolved)
   - `release-metadata.yaml`
   - CHANGELOG section
3. **create-src-tag** - `src/X.Y` tag on main at branch point (for maintenance reference)
4. **create-sync-pr** - PR to main with:
   - CHANGELOG entry (new section at top)
   - README release information update
   - For public releases: Update `release-plan.yaml` (set APIs to `unchanged`)
   - Note: Version fields remain placeholders (`info.version: "wip"`)
5. **trigger-release-progress-tracker** - Update Release Progress Tracker dashboard

**Key Feature**: Selective sync (only CHANGELOG/README, not version fields)

**Risk Mitigation**: Initially can be done manually (copy from released tag, create manual PR). Automate progressively.

#### 5.2 Release Progress Tracker Enhancements
**Reference**: [camaraproject/project-administration#38](https://github.com/camaraproject/project-administration/issues/38)

**Note**: Basic Release Progress Tracker already operational from Phase 2

**Phase 5 Enhancements**:
- Real-time status updates (triggered by release-plan.yaml changes)
- Drill-down views per API with detailed checklist status
- Historical trend analysis
- API dependency graph visualization
- Export to JSON/CSV for tooling integration

### Success Criteria
- [ ] Post-release workflow tested end-to-end (manual initially, automated progressively)
- [ ] Release Progress Tracker enhanced with real-time updates
- [ ] Zero critical issues blocking releases
- [ ] Community satisfaction > 80% (survey early adopter teams)

---

## Phase 6: Maintenance (Spring26 - Fall26)

### Objectives
Support maintenance branch releases (C5 workflow).

### Deliverables

#### 6.1 Maintenance Branch Workflow (C5)
**Enhancement**: Extend C2-C4 workflows for maintenance branches

**Prerequisites**:
- Maintenance branch exists (e.g., `maintenance-r3`)
- `release-plan.yaml` has `release_readiness: patch-release`
- Only patch version changes allowed

**Differences**:
- Release branch created from maintenance branch (not main)
- Version validation: patch-only (X.Y.Z → X.Y.Z+n)
- Sync PR goes to maintenance branch
- Optional backport PR to main

### Success Criteria
- [ ] Maintenance releases fully automated
- [ ] Tested on 2-3 repositories requiring patches
- [ ] Documentation complete

---

## Validation Architecture

### Architecture Principles

**1. Direct Linter Integration** (not MegaLinter wrapper)
- **YAML validation**: yamllint + JSON Schema validation (ajv-cli)
- **OpenAPI validation**: Spectral with CAMARA rules
- **Gherkin validation**: gherkin-lint
- **Custom checks**: Node.js scripts for cross-file validation

**Rationale**: Simpler, faster, more maintainable than MegaLinter wrapper

**2. Severity Matrix**

| Severity | Enforcement | Example |
|----------|------------|---------|
| **error** | Blocks PR merge | `info.version` not "wip" on main |
| **warning** | Must fix before release | Missing test file |
| **info** | FYI | API status transition detected |
| **hint** | Suggestion | Consider more descriptive operationId |

**3. Context-Aware Validation**

Rules vary by:
- **Branch**: main vs release branch
- **release_readiness**: Different checks for alpha vs public
- **api_status**: More strict for rc/public than alpha
- **PR type**: Metadata-only vs implementation PRs

### Validator Components

**Spectral Rules** ([.spectral.yaml](https://github.com/camaraproject/tooling/blob/main/linting/config/.spectral.yaml)):
- Extended with placeholder validation
- Branch-aware checks via custom functions
- 40+ existing CAMARA rules + 10+ new rules

**Custom Validators** (Node.js):
- Framework: `validation/validators/base-validator.js`
- Individual validators: 6+ scripts for cross-file checks
- Orchestrator: `validation/run-validators.js`

**Configuration** (`validation-rules.yaml`):
- Machine-readable rule definitions
- Severity matrix per rule per context
- Extensible configuration format (requires translation into Spectral rules and validation scripts)

### Migration from Monolithic Validator

**Current**: [api_review_validator_v0_6.py](https://github.com/camaraproject/tooling/blob/main/scripts/api_review_validator_v0_6.py) (2,732 lines)

**Note**: This validator was never used in CI, only triggered manually. It is effectively already deprecated.

**Strategy**:
1. **Analysis** (Phase 3): Catalog all 50+ checks, map to new architecture
2. **Reference only**: Use as reference for validation logic

**Check Migration Map**:
- YAML schema → JSON Schema + yamllint
- OpenAPI structure → Spectral rules
- Version patterns → Spectral + custom validators
- CHANGELOG/README → Custom validators
- Cross-file consistency → Custom validators
- Test alignment → Custom validators

---

## Repository Changes Required

### Workflow Updates
**Existing file**: `.github/workflows/pr-validation.yml`

**Change**: Bump from v0 to v1 for repositories adopting new process
- Current: Calls `camaraproject/tooling` reusable workflows v0
- New: Calls `camaraproject/tooling` reusable workflows v1 (with new validation)

### New Files
1. **release-plan.yaml** (root) - Planning metadata

### Branch Protection Updates

**Main branch**:
- Require PR reviews (1 approval)
- Require CODEOWNERS approval
- Required status checks: metadata-validation, yaml-lint, spectral-lint, gherkin-lint, custom-validation

**Release branches** (`release/*`):
- Require PR reviews (2 approvals)
- Require review from release-management_maintainers team
- Restrict push to maintainers + github-actions

---

## Implementation Issues (Sub-issues to #191)

### Phase 1: Concept & Preparation
- **#191.1** Design and implement metadata schemas (ReleaseManagement, L) **[PRIORITY]**


### Phase 2: Mass Rollout
- **#191.2** Create repository adoption package and pre-populated templates (ReleaseManagement, M) **[PRIORITY]**
- **#191.3** Integrate with Release Progress Tracker (project-administration, coordination with #38) **[PRIORITY]**
- **#191.4** Roll out release-plan.yaml to all ~61 repositories (project-administration campaign) **[PRIORITY]**

### Phase 3: Validation Framework
- **#191.5** Define validation rules configuration format (ReleaseManagement, M)
- **#191.6** Implement Spectral rulesets for release-plan.yaml (ReleaseManagement, M)
- **#191.7** Implement custom validator for logic checks (ReleaseManagement, L)
- **#191.8** Integrate validaton into PR workflow (project-administration, M)

### Phase 4: Release Automation
- **#191.9** Implement version calculator (ReleaseManagement, L)
- **#191.10** Implement changelog generator (ReleaseManagement, XL)
- **#191.11** Create release branch automation workflow (project-administration, L)

### Phase 5: Release Operations
- **#191.12** Post-release verification workflow (project-administration, M)
- **#191.13** Enhance Release Progress Tracker with real-time updates (project-administration, M)

### Phase 6: Maintenance & Hardening
- **#191.14** Monitor early adopter releases and fix bugs (ReleaseManagement, L)
- **#191.15** Maintenance branch workflow C5 (tooling, M)

### Deferred topics
- **#191.16** Cross-repository dependency resolution (ReleaseManagement, XL) - Initially manual, automate progressively
- **#191.18** Operational excellence and monitoring (tooling/ReleaseManagement, M)

**Complexity**: S=1-3 days, M=1-2 weeks, L=2-4 weeks, XL=4-8 weeks

### Critical Dependencies
- **#191.1** (Schemas) blocks #191.2 (Templates) and #191.3 (Tracker)
- **#191.2** (Templates) blocks #191.4 (Rollout)
- **#191.3** (Tracker) blocks Wiki Deprecation
- **#191.4** (Rollout) depends on #191.1 - #191.3
- #191.7 depends on #191.5, #191.6 (validators need config format)
- #191.8 depends on #191.6, #191.7 (workflow needs validators)
- #191.11 depends on #191.9, #191.10 (replacement needs version/dependency data)
- #191.13 depends on #191.12 (tracker enhancements)
- #191.14 depends on #191.1-13 (monitoring after operations)
- #191.15 depends on #191.11 (maintenance extends automation)
- #191.17 depends on all previous (mandatory adoption after everything stable)

---

## Open Questions & Risk Areas

### Technical Challenges Requiring POC

1. **Spectral cross-file limitations** → Use custom validators (Phase 3)
2. **Version extension numbering** → Test on real repos (Phase 4)
3. **CHANGELOG generation quality** → Template + manual refinement (Phase 4)
4. **Placeholder pattern complexity** → Comprehensive test suite (Phase 4)

### Governance Decisions Needed

1. **Mandatory adoption timeline** → Fall26 (aggressive, recommended) - Decide by end of Phase 2
2. **Release trigger permissions** → Maintainers + release management - Decide by Phase 4 start
3. **CHANGELOG editing policy** → Auto-generate + manual refinement - Decide by Phase 4 start
4. **Metadata PR mutual exclusivity** → Conditional enforcement - Decide by Phase 2 completion

### Integration Points

1. **Wiki integration** → Phase 2 embed Release Progress Tracker via iframe, deprecate manual tables
2. **Release Progress Tracker** → Phase 2 basic aggregator, Phase 5 real-time enhancements
3. **Checklist automation scope** → Auto items 1,4,5,7,10,11; manual 6,9,12,13

### Deferred Topics Requiring Separate Concepts

1. **Cross-API dependency validation** - $ref resolution across repositories
2. **Bundle generation** - Resolving all $ref for release artifacts
3. **Full dependency graph validation** - Complex validation requiring separate design

### Performance Targets

1. **CI validation**: < 3 minutes (mitigation: parallel jobs, caching)
2. **Release branch generation**: < 10 minutes (mitigation: matrix strategy, optimization)

### Migration Risks

1. **Resistance** → Training, support, value proposition, success stories
2. **Edge cases** → Early adopter testing, issue tracker, escape hatch
3. **Dependencies** → Error handling, retry logic, monitoring
4. **Tight timeline** → Aggressive Dec 15 deadline for Phase 1A; mitigation: focus on essentials, defer enhancements

---

## Critical Files

**Concept Documents**:
- [CAMARA-Release-Workflow-and-Metadata-Concept.md](https://github.com/camaraproject/ReleaseManagement/blob/main/documentation/SupportingDocuments/CAMARA-Release-Workflow-and-Metadata-Concept.md)
- [CAMARA_Release_Process_coverage_of_fall_25.md](https://github.com/camaraproject/ReleaseManagement/blob/main/documentation/SupportingDocuments/CAMARA_Release_Process_coverage_of_fall_25.md)

**Existing Infrastructure**:
- [.spectral.yaml](https://github.com/camaraproject/tooling/blob/main/linting/config/.spectral.yaml) - Extend with new rules
- [api_review_validator_v0_6.py](https://github.com/camaraproject/tooling/blob/main/scripts/api_review_validator_v0_6.py) - Reference for validation logic (deprecated, never used in CI)
- [API-Readiness-Checklist.md](https://github.com/camaraproject/ReleaseManagement/blob/main/documentation/API-Readiness-Checklist.md) - Automate checklist items
- [compliance-checks.yaml](https://github.com/hdamker/project-administration/blob/feat/repository-compliance-requirements-51/workflows/repository-compliance/config/compliance-checks.yaml) - Inspiration for validation config

**Related Issues**:
- [project-administration#38](https://github.com/camaraproject/project-administration/issues/38) - Release Progress Tracker

**Standards**:
- [API_Release_Guidelines.md](https://github.com/camaraproject/ReleaseManagement/blob/main/documentation/API_Release_Guidelines.md) - Current process to replace
- [CAMARA-API-Design-Guide.md](https://github.com/camaraproject/Commonalities/blob/main/documentation/CAMARA-API-Design-Guide.md) - Validation requirements

