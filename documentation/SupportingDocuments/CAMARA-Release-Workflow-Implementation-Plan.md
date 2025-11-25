# CAMARA Automated Release Workflow - Implementation Plan

## Overview

This document provides a phased implementation plan for automating the CAMARA release workflow as defined in [CAMARA-Release-Workflow-and-Metadata-Concept.md](https://github.com/camaraproject/ReleaseManagement/blob/main/documentation/SupportingDocuments/CAMARA-Release-Workflow-and-Metadata-Concept.md).

**Implementation Timeline**: November 2025 → Fall 2026 (5 phases)
**Target Repositories**: camaraproject/tooling, camaraproject/ReleaseManagement
**Scope**: Replace manual wiki-based release process with metadata-driven automation

## Key Design Decisions

1. **Aggressive adoption strategy**: All participating Spring26 repositories migrate (limited early adopter set)
2. **Replace monolithic validator**: New modular architecture with Spectral + custom validators
3. **Direct linter integration**: Use YAML-lint, Spectral, Gherkin-lint directly (not MegaLinter wrapper)
4. **Defer complex dependencies**: Cross-API $ref resolution postponed to later phase (separate concept needed)
5. **Severity matrix**: error/warning/info/hint with context-aware enforcement

## Timeline Alignment

| Milestone | Date | Phase Deliverable |
|-----------|------|-------------------|
| **All Hands Call** | Dec 10, 2025 | Present release-plan.yaml concept |
| **Spring26 M1** | Dec 15, 2025 | Phase 1A complete (metadata schemas + adoption) |
| **Fall26 cycle start** | Mid-Jan 2026 | Phase 1B complete (validation framework stable) |
| **Spring26 M3** | Jan 31, 2026 | First early adopters create releases with new process (Phase 2 functional) |
| **Spring26 M4** | Mar 2026 | Phase 3 rollout to 10-15 early adopter repositories |
| **Fall26** | Sep-Oct 2026 | Phases 4-5 complete, mandatory adoption |

---

## Phase 1A: Metadata Foundation (Nov-Dec 2025, 3 weeks)

### Objectives
1. Define metadata schemas and get repositories using `release-plan.yaml`
2. Replace wiki tracker with Release Progress Tracker (immediate value)
3. Present to community in All Hands Call (Dec 10)

### Deliverables

#### 1A.1 Metadata Schemas (PRIORITY)
**Location**: `camaraproject/ReleaseManagement/schemas/`

- `release-plan-schema.yaml` - Structure for planning metadata on main
- `release-metadata-schema.yaml` - Structure for generated release metadata

**Key Fields in release-plan.yaml**:
```yaml
repository:
  meta_release: "Fall26"  # or "Other"
  release_number: "r4.1"
  release_readiness: "pre-release"  # none|pre-release|pre-release-rc|public-release|patch-release

dependencies:
  commonalities_version: "r3.4"  # Concrete Commonalities release (not meta-release reference)
  identity_consent_management_version: "r3.4"  # Concrete ICM release
  # Rationale: APIs decide when ready to validate against newest Commonalities
  # Meta-release reference would cause uncontrolled updates

apis:
  - name: "location-verification"
    target_version: "3.2.0"  # SemVer base (extension auto-calculated)
    api_status: "rc"  # planned|unchanged|alpha|rc|public
    main_contacts: ["githubUser1", "githubUser2"]
```

**Rationale**: Schema must be well-designed from start; repositories will adopt this format immediately.

**Schema Validation**:
- Initially manual: API codeowners create release-plan.yaml PR, request review from release management team
- As soon as possible: integrated into CI validation (Phase 1B)

#### 1A.2 Release Progress Tracker Integration
**Reference**: [camaraproject/project-administration#38](https://github.com/camaraproject/project-administration/issues/38)

**Integration Point**: Meta-release aggregator already planned in project-administration as "Release Progress Tracker"

**Immediate Value**: Replaces manual wiki tracker API tables as soon as repositories add `release-plan.yaml`

#### 1A.3 Repository Adoption Package (PRIORITY)
**Location**: `camaraproject/ReleaseManagement/documentation/`

**Contents**:
- Pre-populated `release-plan.yaml` template for each repository
- Migration guide for converting wiki tracker to YAML
- Instructions for adding file to repository
- Schema validation tool (local testing before commit)

**Goal**: Get 20+ repositories to add `release-plan.yaml` by Dec 15 (Spring26 M1)

#### 1A.4 Presentation Materials
**For All Hands Call (Dec 10)**:
- Concept overview slides
- Demo: release-plan.yaml example
- Benefits: automated tracking, wiki deprecation
- Timeline and participation requirements

### Success Criteria
- [ ] **Metadata schemas finalized and documented** (CRITICAL - blocks everything)
- [ ] **Release Progress Tracker fetching release-plan.yaml files** (CRITICAL - immediate wiki replacement)
- [ ] **20+ repositories have added release-plan.yaml** (enables wiki deprecation)
- [ ] **Concept presented at All Hands Call (Dec 10)**
- [ ] **Wiki API tracker tables deprecated with iframe to camaraproject.github.io**

---

## Phase 1B: Validation Framework (Dec 2025 - Jan 2026, 4-5 weeks)

### Objectives
Build CI validation foundation on `main` with placeholder enforcement (C1 workflow). Must be stable by mid-January for Fall26 cycle start.

### Deliverables

#### 1B.1 Validation Configuration Framework
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
        script: check-unchanged-apis.js
```

**Key Features**:
- Severity levels drive enforcement (error blocks PR)
- Context-aware rules (different checks for main vs release branches)
- Extensible configuration format (requires translation into Spectral rules and validation scripts)

**Validation Rules Schema**:
**Location**: `camaraproject/ReleaseManagement/schemas/validation-rules-schema.yaml`

#### 1B.2 Enhanced Spectral Rules
**Location**: `camaraproject/tooling/linting/config/.spectral.yaml`

Extend existing [.spectral.yaml](https://github.com/camaraproject/tooling/blob/main/linting/config/.spectral.yaml) with:
- Placeholder validation rules (info.version must be "wip" on main)
- Server URL pattern enforcement (must contain placeholders on main)
- Branch-aware checks using custom functions

#### 1B.3 Custom Validators
**Location**: `camaraproject/tooling/validation/validators/`

Node.js scripts for cross-file validation:
- `check-unchanged-apis.js` - Ensure unchanged APIs have no modifications
- `check-readiness-matrix.js` - Validate repository readiness vs API statuses
- `check-pr-mutual-exclusivity.js` - Block PRs changing both metadata and implementation
- `check-dependency-refs.js` - Validate Commonalities/ICM reference format
- `validate-status-promotion.js` - Check if status promotion is valid
- `check-test-alignment.js` - Validate test files exist for APIs

**Rationale**: Spectral operates on individual files; cross-file checks need custom code.

#### 1B.4 PR Validation Workflow (C1) - Structure
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
- [ ] Spectral rules extended with 5+ placeholder validation rules
- [ ] 6 custom validators implemented and tested
- [ ] CI workflow (v1) runs successfully on test repository
- [ ] Performance target met (< 3 minutes)
- [ ] **Stable and ready for Fall26 cycle start (mid-January)**

---

## Phase 2: Release Automation (Jan-Feb 2026, 6-8 weeks)

### Objectives
Implement automated release branch generation (C2 workflow). First early adopters must be able to create releases by Spring26 M3 (Jan 31).

### Deliverables

#### 2.1 Version Calculator
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

#### 2.2 Dependency Resolver
**Location**: `camaraproject/tooling/scripts/resolve-dependencies.js`

Resolves concrete Commonalities/ICM release references to exact versions:
1. Read release reference (e.g., `r3.4`) from `release-plan.yaml`
2. Fetch specified Commonalities/ICM release from GitHub
3. Parse `release-metadata.yaml` from dependency releases
4. Format as `"rX.Y (semver)"` (e.g., `"r3.4 (1.2.0-rc.1)"`)

#### 2.3 Placeholder Replacement Engine
**Location**: `camaraproject/tooling/scripts/replace-placeholders.js`

Context-aware replacement:
- `info.version: "wip"` → `info.version: "3.2.0-rc.2"`
- `{{api_version}}` → `3.2.0-rc.2`
- `{{commonalities_version}}` → `1.2.0-rc.1`
- `{apiRoot}/api-name/vwip` → `{apiRoot}/api-name/v3` (or `/v0.5` for initial)
- `x-camara-commonalities: wip` → `x-camara-commonalities: 1.2.0-rc.1`

**Test Suite**: Comprehensive coverage of all placeholder patterns in YAML, markdown, URLs

#### 2.4 CHANGELOG Generator
**Location**: `camaraproject/tooling/scripts/generate-changelog.js`

Template-based approach:
1. Extract commits since last release using git log
2. Group by API (parse file paths)
3. Generate structured markdown with placeholders for manual refinement
4. Allow manual editing before release

**Quality**: Auto-generation creates baseline; manual refinement adds context.

#### 2.5 API Readiness Checklist Generator
**Location**: `camaraproject/tooling/scripts/generate-checklist.js`

Automated validation of 13 checklist items:
- **Fully automated**: Items 1,4,5,7,10,11 (file existence, naming conventions)
- **Partially automated**: Items 2,3,8 (version checks, guidelines compliance)
- **Manual only**: Items 6,9,12,13 (user stories, test results, certification)

Output: Markdown checklist with Y/N/tbd status

#### 2.6 Release Branch Generator Workflow (C2)
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
- [ ] Placeholder replacement handles all patterns correctly (100+ test cases)
- [ ] CHANGELOG generation produces usable baseline
- [ ] Checklist validation runs and generates accurate Y/N/tbd status
- [ ] **End-to-end release branch creation tested on 2-3 early adopter repos by Spring26 M3 (Jan 31)**

---

## Phase 3: Full Rollout (Mar-Apr 2026, 8-10 weeks)

### Objectives
Complete C1-C4 workflow; migrate 10-15 early adopter repositories.

### Deliverables

#### 3.1 Post-Release Workflow (C4)
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

#### 3.2 Release Progress Tracker Enhancements
**Reference**: [camaraproject/project-administration#38](https://github.com/camaraproject/project-administration/issues/38)

**Note**: Basic Release Progress Tracker already operational from Phase 1A

**Phase 3 Enhancements**:
- Real-time status updates (triggered by release-plan.yaml changes)
- Drill-down views per API with detailed checklist status
- Historical trend analysis
- API dependency graph visualization
- Export to JSON/CSV for tooling integration

#### 3.3 Migration Tooling & Documentation
**Location**: `camaraproject/ReleaseManagement/documentation/`

**Migration Guide**:
- Pre-populated `release-plan.yaml` template
- Step-by-step migration checklist
- Workflow setup instructions (bump pr-validation.yml from v0 to v1)
- Branch protection configuration
- Training materials

**Migration Script**:
- Generates initial `release-plan.yaml` from existing repository state
- Validates repository structure
- Tests workflow in fork

#### 3.4 Early Adopter Repository Migrations
**Target**: 10-15 repositories (volunteers from Spring26 participants)

**Per-Repository Tasks**:
1. Create `release-plan.yaml` from template
2. Bump PR validation workflow from v0 to v1
3. Configure branch protection (if needed)
4. Test in fork
5. Train maintainers
6. Go live
7. First release with automation
8. Collect feedback

**Support**: Dedicated Slack channel, office hours, rapid issue resolution

#### 3.5 Wiki Integration
**Note**: Wiki remains for extensive documentation and meta-release pages (timeline, etc.)

**Phase 3 Actions**:
- Embed Release Progress Tracker into wiki via iframe (from camaraproject.github.io)
- Deprecate manual API tracker tables in wiki
- Update documentation references

### Success Criteria
- [ ] Post-release workflow tested end-to-end (manual initially, automated progressively)
- [ ] Release Progress Tracker enhanced with real-time updates
- [ ] Migration guide complete and validated
- [ ] 10-15 early adopter repositories migrated successfully
- [ ] Zero critical issues blocking releases
- [ ] Wiki API tables replaced with iframe to Release Progress Tracker
- [ ] Community satisfaction > 80% (survey early adopter teams)

---

## Phase 4: Maintenance Workflow (May-Jun 2026, 4-6 weeks)

### Objectives
Support maintenance branch releases (C5 workflow).

### Deliverables

#### 4.1 Maintenance Branch Workflow (C5)
**Enhancement**: Extend C2-C4 workflows for maintenance branches

**Prerequisites**:
- Maintenance branch exists (e.g., `maintenance-r3`)
- `release-plan.yaml` has `release_readiness: patch-release`
- Only patch version changes allowed

**Differences**:
- Release branch created from maintenance branch (not main)
- Version validation: patch-only (X.Y.Z → X.Y.Z+n)
- No `src/` tag creation
- Sync PR goes to maintenance branch
- Optional backport PR to main

### Success Criteria
- [ ] Maintenance releases fully automated
- [ ] Tested on 2-3 repositories requiring patches
- [ ] Documentation complete

---

## Phase 5: Production Hardening (Jul-Sep 2026, 8-10 weeks)

### Objectives
Mandatory adoption; operational excellence; preparation for Fall26.

### Deliverables

#### 5.1 Mandatory Adoption Rollout
**Target**: All participating repositories using automated workflow by Fall26

**Activities**:
- Deadline enforcement
- Migration support for remaining repositories
- Escalation path for blockers

#### 5.2 Operational Excellence
**Deliverables**:
- Monitoring dashboards (workflow success rate, duration)
- SLA metrics (95% success rate, < 10 min release branch generation)
- Incident response runbooks
- Rollback procedures
- Quarterly review process

### Success Criteria
- [ ] All participating repositories using automated workflow
- [ ] Manual process completely deprecated
- [ ] SLA metrics met for 1 quarter
- [ ] Zero critical incidents
- [ ] Operational runbooks complete

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
1. **Analysis** (Phase 1B): Catalog all 50+ checks, map to new architecture
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

### Phase 1A: Metadata Foundation
- **#191.1** Design and implement metadata schemas (ReleaseManagement, L) **[PRIORITY]**
- **#191.2** Integrate with Release Progress Tracker (project-administration, coordination with #38) **[PRIORITY]**
- **#191.3** Create repository adoption package and pre-populated templates (ReleaseManagement, M) **[PRIORITY]**
- **#191.4** Roll out release-plan.yaml to 20+ repositories (multiple repos, coordination) **[PRIORITY]**

### Phase 1B: Validation Framework
- **#191.5** Define validation rules configuration format (ReleaseManagement, M)
- **#191.6** Extend Spectral rules for placeholder validation (tooling, L)
- **#191.7** Implement custom validators framework + 6 validators (tooling, XL)
- **#191.8** Create PR validation workflow C1 v1 (tooling, L)

### Phase 2: Release Automation
- **#191.9** Implement version calculator (tooling, L)
- **#191.10** Implement dependency resolver (tooling, M)
- **#191.11** Implement placeholder replacement engine (tooling, L)
- **#191.12** Implement CHANGELOG generator (tooling, M)
- **#191.13** Implement release branch generator workflow C2 (tooling, XL)

### Phase 3: Full Rollout
- **#191.14** Implement post-release workflow C4 (tooling, L) - Initially manual, automate progressively
- **#191.15** Enhance Release Progress Tracker with real-time updates (project-administration, M)
- **#191.16** Migration tooling and documentation (ReleaseManagement, M)
- **#191.17** Early adopter repository migrations (multiple repos, 10-15 × L)

### Phase 4: Maintenance Workflow
- **#191.18** Maintenance branch workflow C5 (tooling, M)

### Phase 5: Production Hardening
- **#191.19** Mandatory adoption rollout (ReleaseManagement, coordination)
- **#191.20** Operational excellence and monitoring (tooling/ReleaseManagement, M)

**Complexity**: S=1-3 days, M=1-2 weeks, L=2-4 weeks, XL=4-8 weeks

### Critical Dependencies
- **#191.2 depends on #191.1** (tracker needs schemas)
- **#191.3 depends on #191.1** (templates need schemas)
- **#191.4 depends on #191.1, #191.2, #191.3** (rollout needs schemas, tracker, templates)
- #191.7 depends on #191.5, #191.6 (validators need config format)
- #191.8 depends on #191.6, #191.7 (workflow needs validators)
- #191.11 depends on #191.9, #191.10 (replacement needs version/dependency data)
- #191.13 depends on #191.9-12 (orchestrates all automation)
- #191.14 depends on #191.13 (post-release follows release creation)
- #191.16 depends on #191.1-15 (documentation after infrastructure ready)
- #191.17 depends on #191.1-16 (migrations need everything ready)
- #191.18 depends on #191.13, #191.14 (extends release workflows)
- #191.19 depends on all previous (mandatory adoption after everything stable)

---

## Open Questions & Risk Areas

### Technical Challenges Requiring POC

1. **Spectral cross-file limitations** → Use custom validators (Phase 1B week 2-3)
2. **Version extension numbering** → Test on real repos (Phase 2 week 1-2)
3. **CHANGELOG generation quality** → Template + manual refinement (Phase 2 week 3-4)
4. **Placeholder pattern complexity** → Comprehensive test suite (Phase 2 week 2-3)

### Governance Decisions Needed

1. **Mandatory adoption timeline** → Fall26 (aggressive, recommended) - Decide by end of Phase 1A
2. **Release trigger permissions** → Maintainers + release management - Decide by Phase 2 start
3. **CHANGELOG editing policy** → Auto-generate + manual refinement - Decide by Phase 2 start
4. **Metadata PR mutual exclusivity** → Conditional enforcement - Decide by Phase 1B completion

### Integration Points

1. **Wiki integration** → Phase 1A embed Release Progress Tracker via iframe, Phase 3 deprecate manual tables
2. **Release Progress Tracker** → Phase 1A basic aggregator, Phase 3 real-time enhancements
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
- [CAMARA_Release_Rrocess_coverage_o_fall_25.md](https://github.com/camaraproject/ReleaseManagement/blob/main/documentation/SupportingDocuments/CAMARA_Release_Rrocess_coverage_o_fall_25.md)

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

---

## Next Steps

1. **Review and approve** this plan with Release Management team
2. **Create Phase 1A issues** (#191.1-4) in ReleaseManagement and project-administration repos
3. **Assign ownership** and establish timeline toward Dec 10 presentation
4. **Begin Phase 1A development** (Nov 25 - Dec 15):
   - Design and implement metadata schemas
   - Integrate with Release Progress Tracker
   - Create adoption package
   - Roll out to 20+ repositories
   - Prepare All Hands Call presentation

**Target**: Phase 1A by Dec 15, Phase 1B by mid-Jan, Phase 2 functional by Jan 31 (Spring26 M3), Phase 3 by Spring26 M4, Phases 4-5 by Fall26.
