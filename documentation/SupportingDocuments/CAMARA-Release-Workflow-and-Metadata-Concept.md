# CAMARA Release Workflow and Metadata Specification
*Version 0.1*

## Objectives

This workflow concept establishes an automated release process for CAMARA that addresses key challenges in managing multi-repository releases:

**Replace manual wiki-based tracking** with structured, machine-readable metadata files that enable automation, flexible reporting, and consistent status synchronization across repositories.

**Establish clear separation** between development work and release preparation by keeping the `main` branch in a consistent work-in-progress state with version fields as `"wip"`, while using dedicated release branches per (pre-)release for alpha, rc, and public releases.

**Enable structured validation and enforcement** through CI gating on PRs to `main`, replacing limited validation with complete checks for metadata files and CAMARA-specific release guidelines.

**Provide transparent and traceable release preparation** by using dedicated release branches and release preparation PRs with structured approvals, avoiding informal PRs merged directly into `main` that mix version updates, changelog edits, and last-minute changes.

**Support flexible versioning strategy** by keeping CAMARA release numbering (`rX.Y`) distinct from API semantic versioning, with clear metadata-driven version management instead of manual field updates in `main` that must be reset after releases.

**Enable progressive automation** for release artifacts including CHANGELOG generation and API Readiness Checklist validation, reducing manual cross-checks and enabling consistent artifact creation.

The workflow achieves these objectives through:

- Structured **metadata files (in YAML)** as authoritative source for release planning and status
- Dedicated **release branches per (pre-)release** with automated preparation and validation
- **CI enforcement** on PRs to `main` ensuring correctness before merge
- **Branch protection** restricting release branch changes to authorized release managers
- **Release preparation PRs** into release branches for collaborative review
- **Feedback integration** via PRs into `main`, with controlled updates to release branches as necessary

## Terminology

| Term                   | Description |
|------------------------|-------------|
| `meta_release`         | Meta-release label (e.g., `Fall26`) |
| `release_number`       | CAMARA release tag (e.g., `r4.1`). Distinct from API SemVer. |
| `release_readiness`    | Repository release phase: `none` (not ready), `pre-release` (mixed maturity), `pre-release-rc` (rc minimum), `public-release` (all stable), `patch-release` (maintenance). |
| `api_status`           | Per-API status: `planned` (not yet in repo), `unchanged` (no changes from previous release), `alpha`, `rc`, `public`. Extension numbers are auto-calculated. |
| `main_contacts`        | GitHub handles of code owners or maintainers (per API in `release-plan.yaml`). |
| `main` branch          | Development branch. All content is work-in-progress (`version: wip`). |
| Maintenance branch     | Long-lived branch for maintaining older release cycles (e.g., `maintenance-r3`). See Appendix for details. |
| Release branch         | Dedicated release preparation branch per (pre-)release (e.g., `release/r4.1`). |
| Release preparation PR | Pull request against a release branch to finalize or tweak the release content. |

## Metadata File Format

All metadata files are YAML-based and versioned in the repository. They serve as authoritative configuration & release inputs.

### 1. `release-plan.yaml` (on `main`)

Planning metadata owned by codeowners, manually updated and CI-validated. Contains only forward-looking release plans, not historical data.

```yaml
repository:
  meta_release: Fall26  # default as long not eligible or planned for a meta-release: Other
  release_number: r4.1
  release_readiness: pre-release  # Repository ready for pre-release with mixed API maturity

dependencies:
  commonalities_version: r4.2
  identity_consent_management_version: r4.3

apis:
  - name: location-verification
    target_version: 3.2.0
    api_status: rc  # Status type only; extension numbers (e.g., rc.2) are auto-calculated
    main_contacts:
      - githubUser1
      - githubUser2

  - name: location-retrieval
    target_version: 0.5.0
    api_status: rc
    main_contacts:
      - githubUser3

  - name: some-new-location-service
    target_version: 0.1.0
    api_status: alpha
    main_contacts:
      - githubUser4
```

👉 Notes:
- API status progression: `planned` → `alpha` → `rc` → `public` (or `unchanged` for existing APIs)
  - `planned`: API declared in release-plan.yaml but not yet in repository (CI skips validation)
  - `unchanged`: API remains at previous release version, no changes allowed (CI blocks modifications)
  - `alpha`+: API file must exist and pass validation at declared maturity
- Repository release readiness determines what type of release can be created:
  - `none`: No release possible (APIs missing or only planned)
  - `pre-release`: Can release with mixed API maturity (alpha, rc, public)
  - `pre-release-rc`: Requires all APIs at rc or public status (M3 milestone)
  - `public-release`: Requires all APIs at public status
  - `patch-release`: For maintenance/hotfix releases from maintenance branches
- CI validates that API statuses match the declared repository release readiness.

### 2. `release-metadata.yaml` (on release branch)

Generated automatically from the release plan and committed before tagging. Preserved in each release tag, providing complete release history.

```yaml
repository:
  release_number: r4.1
  meta_release: Fall26
  release_date: 2025-11-22  # Actual release date (set at release time)
  status: pre-release
  src_commit_sha: abcd1234efgh5678  # Last commit from main or maintenance branch included in this release
  release_notes: Pre-release for CAMARA Fall26 release cycle.

dependencies:
  commonalities_version: r4.2 (1.2.0-rc.1)
  identity_consent_management_version: r4.3 (1.1.0)

apis:
  - name: location-verification
    version: 3.2.0-rc.2

  - name: location-retrieval
    version: 0.5.0-rc.1

  - name: some-new-location-service
    version: 0.1.0-alpha.1
```

## End-to-End Workflow

### Step 1: Continuous Development on `main`

- All API development related PRs target the `main` branch, with changes validated via MegaLinter and YAML schema checks.
- the `release-plan.yaml` is updated on main to reflect the roadmap and desired targets for the upcoming (pre-)release.
- CI gates validate:
  - Formatting and schema correctness
  - Strict version consistency: info.version format, server URL patterns per CAMARA rules
  - Adherence to CAMARA guidelines based on the declared repository `release_readiness` and `api_status`
  - APIs with status `alpha` or higher must exist and meet validation criteria
  - APIs with status `planned` are skipped (allows declaration before implementation)
  - APIs with status `unchanged` must not be modified (enforces no changes to API or test files)
- CI also raises non-blocking warnings about issues that must be addressed to enable promotion to the next stage (e.g., from `alpha` to `rc`, or `rc` to `public`).
- All validation results are summarized in the CI output and posted as comments in the PR, helping developers stay informed and proactive.

**Rationale:**
- Prevents invalid or incomplete content from entering `main`
- Ensures developers align with repository release readiness expectations early
- Keeps readiness transparent across reviewers, contributors, and release managers
- Allows optional enforcement that metadata updates (e.g., status changes) must be done in dedicated PRs separate from implementation changes

### Step 2: Automated Release Branch Creation

Upon triggering the release (via labeled issue - maintainers+ can trigger by adding `trigger-release` or `trigger-pre-release` label):

- A release branch is created (e.g. `release/r4.1`)
- A script or GitHub Action:
  - Sets exact API versions using `target_version` + auto-calculated suffix (e.g., `-rc.2` based on consecutive numbering across API lifecycle)
  - Enforces CAMARA versioning rules: info.version matches tag, server URLs follow v0.x or vx patterns
  - Writes `release-metadata.yaml`
  - Replaces placeholder markers (e.g., `{{api_version}}`, `{{commonalities_version}}`) in repository files, including updated template text from Commonalities/ICM in second phase
  - Updates external references to point to specific dependency release tags (Note: Cross-repository reference handling, validation, and bundling complexities are addressed in a later implementation phase)
  - Commits consistent/structured CHANGELOG, README, and checklist artifacts

**Rationale:**
- Avoids fragile manual editing of version fields and metadata
- Creates verified, reviewable release state before tag

### Step 3: Review via Release Preparation PRs

Manual review and adjustments happen through Release Preparation PRs into the release branch.

- Release PRs require approval from codeowner(s) and release reviewer(s) (via branch protection).
- Review covers CHANGELOG, README and checklist correctness wrt metadata

If problems are found in API specs or implementation:
- Create PRs against `main`
- Update (or rebase) release branch from `main`
- Regenerate release metadata/artifacts

**Rationale:**
- Keeps release preparation clean, visible, and traceable
- Ensures specification fixes flow through formal code review on `main`

### Step 4: Tag and Generate Release

After approval:

- A tag (e.g., `r4.1`) is created on the release branch
- CI builds and publishes artifacts
- GitHub Release with artifacts is created:
  - OpenAPI bundles (self-contained specs with all external references resolved)
  - Generated documentation
  - Release metadata files

**Rationale:**
- Provides traceable, repeatable state for each tagged release

### Step 5: Post-Release Actions

After release is tagged and published:

#### 5a. Update `main` branch:
- Create a PR back into `main` with:
  - CHANGELOG entry
  - README additions (e.g., new API table rows)
- Do not update any version fields (they stay `"wip"`)

#### 5b. For public releases only:
- Auto-update `release-plan.yaml`: Set all APIs to `unchanged` status
- Forces explicit planning for next release cycle
- Prevents unintended changes to stable APIs

#### 5c. Tag reference point on `main`:
- Create tag `src/X.Y` (e.g., `src/4.1`) on main at branch point
- Marks commit for potential maintenance branch creation
- Reference for comparing API changes in next release
- Note: This is NOT a release tag, just a reference marker

**Rationale:**
- Provides visibility into releases without disrupting ongoing work-in-progress development state in `main`
- Establishes clear reference points for maintenance branch creation and change comparison
- Enforces explicit planning for next release cycle after public releases

### Step 6: Maintenance and Patch Releases

For critical fixes and security patches on older release cycles:

- **Maintenance branches** (`maintenance-r3`) are created from the last commit included in that release cycle
- Patches are developed and tested on the maintenance branch
- Set `release_readiness: patch-release` in the maintenance branch's `release-plan.yaml`
- Follow steps 2-5 above, but create release branch from maintenance branch instead of `main`
- Patch releases (r3.4, r3.5) contain only bug fixes, no new features

See Appendix for detailed branching diagrams and maintenance strategy.

## Summary of Benefits

| Area                   | Benefits                                                                                     |
|------------------------|----------------------------------------------------------------------------------------------|
| Separation of concerns | `main` can always be integrated or reworked — no release state mixed in                     |
| Consistent metadata    | Metadata is parseable, validatable, and source-of-truth for release tooling                 |
| Flexible compliance    | Pre-release vs public release phases are enforced via repository `release_readiness` and `api_status` |
| CI-friendly            | No fragile manual checks — all validations declarative, structural, and branch-aware        |
| Collaborative review   | All critical changes reviewed like any other PR                                              |
| Traceable results      | Tag, commit SHA, and metadata captured in release snapshot                                  |
| Minimal backporting    | Minor fixes flow through `main` and regenerate the release — auto-tidy                     |
| Reusable tooling       | YAML format + GitHub workflows = universal scripting, readable for both devs and CI         |

## Migration Timeline (Work in Progress)

### Fall25 (In Progress)
- Complete releases with current process
- Post-release: Generate and attach `release-metadata.yaml` as release artifacts (can be added after release)

### Spring26 (October 2025 - March 2026)
- All repositories add `release-plan.yaml` with their planning e.g. for Fall26 (based on pre-populated file)
- Auto-generate meta-release overview tables from YAML files
- Wiki tracker pages deprecated (no longer maintained)
- **Parallel operation**: Manual and automated release process (selected repositories as early adopters)
- **Ambition**: Spring26 M4 milestone automated for all participating API repositories

### Fall26 (April 2026)
- Full automation implementation
- Wiki completely deprecated
- Mandatory adoption for all repositories

## Next Steps (Optional)

- [ ] Define a YAML schema for `release-plan.yaml` and `release-metadata.yaml`
- [ ] Add GitHub Actions for metadata validation, release branch preparation, and post-release syncing
- [ ] Enforce CODEOWNERS and team-based protections on branches
- [ ] Plan and implement CHANGELOG automation as a separate phase
- [ ] Revisit content of checklist and implement automated updates where possible
- [ ] Consider attaching `release-metadata.yaml` additionally as release artifact for efficient reporting

## Appendix: Metadata Status and Dependency Update Strategy

### ❗ The Problem

In the current CAMARA workflow, we risk repeating the problems caused by "monolithic" release PRs — where contributors update `release-plan.yaml` to promote an API (e.g., from `planned` to `rc`) and simultaneously attempt to fix all blocking issues in the same PR. These PRs are hard to review, difficult to verify, and blur responsibility between status declaration and implementation compliance.

Worse, when deadlines are near, this approach encourages rush patches and discourages proper code review.

### Proposed Strategy: Separate Metadata from Implementation Changes

To avoid reintroducing this problem, the following strategy is proposed and can be enforced by CI:

#### 1. **Mutual Exclusivity Rule**  
A pull request to `main` may either:
- ✅ Modify metadata (e.g., `release-plan.yaml`), or
- ✅ Modify other repository content (OpenAPI specs, test files, descriptions, etc.),  
but ❌ not both.

This applies particularly to:
- Status changes in repository `release_readiness` or per-API `api_status`
- Dependency updates, such as upgrading `commonalities_version`

#### 2. **CI Validation of Metadata-only PRs**

- If a PR modifies status or dependencies:
  - CI will run validation against the target status
  - Block the PR if issues remain for that status
- The validation report will:
  - List blocking issues
  - Warn about any errors that must be resolved first
  - Recommend raising separate PRs for specification/test fixes

#### 3. **CI Enforcement Conditions**

| PR Type                  | Allowed to change           | Validation Conditions                                    |
|--------------------------|-----------------------------|----------------------------------------------------------|
| Metadata-only PR         | `release-plan.yaml` only     | Must have no blocking issues for target statuses/versions |
| Specification/test PR    | All files except metadata    | CI checks correctness of content; PR passes independently |
| Mixed PR (both types)    | ❌ Blocked                    | Will be rejected — must be split before proceeding        |

### ✅ Benefits

- Improved reviewability: Each PR is focused and reviewable on its own merit
- Clear accountability: Metadata changes are explicit declarations of readiness
- Reduced risk: No status promotions can be hidden inside technical change PRs
- Reinforces proper sequencing: Implementation improvements come before status upgrades

### Developer Workflow Example

1. Developer merges a PR that corrects a missing test file for an API.
2. Once CI passes and no blocking issues remain, they open a small metadata-only PR updating the `api_status` from `alpha` to `rc`.
3. CI detects the change, runs combined checks, and approves if valid.

This enforces discipline, validates correctness, and maintains oversight — without compromising developer agility.

## Appendix: Branching Strategy Clarification

### Understanding Git Branches and Tags

For those newer to Git, here's how branches and tags relate in the CAMARA release workflow:

- **Branch**: A movable pointer to commits, used for ongoing work
- **Tag**: A permanent marker on a specific commit, used to mark releases
- **Release branch**: A temporary branch created from `main` for preparing a specific release
- **Maintenance branch**: A long-lived branch for maintaining older release cycles

### Release Branch Lifecycle

Each release (e.g., r4.1, r4.2) gets its own **temporary** branch:

1. **Creation**: Branch `release/r4.1` is created from `main` (or `maintenance-rX` for patches)
2. **Preparation**: Automation sets versions, updates metadata, creates CHANGELOG
3. **Review**: Release preparation PRs can adjust content on this branch
4. **Tagging**: Once approved, the branch HEAD is tagged with `r4.1`
5. **Deletion**: After tagging, the branch is deleted (the tag preserves the release)

```
main ────┬──[src/4.1]──────┬──[src/4.2]──────────► (ongoing development)
         │                 │
         └─release/r4.1    └─release/r4.2
              ↓                  ↓
            tag:r4.1          tag:r4.2
```

### Maintenance Branches

For maintaining older release cycles after new major releases:

```
main ──────┬────────────────────────────► r5.x development
           │
           └─maintenance-r3─────┬──────► r3.x maintenance (r3.4, r3.5...)
                                 │
                                 └─release/r3.4
                                      ↓
                                    tag:r3.4
```

**Creation strategy**:
- Created from the last commit on `main` that was included in the release cycle to maintain
- Named `maintenance-rX` where X is the release cycle (e.g., r3 for r3.1, r3.2, r3.3...)
- Used for patch releases (r3.4, r3.5) containing API bug fixes
- New API minor versions go into new release cycles on `main`

**Important**: Maintenance branches are tied to **release cycles** (r3.x), not API versions. A maintenance branch can produce r3.4, r3.5 etc., each potentially containing different patch versions of the APIs.

### Updating Release Branch from Main

During release preparation, if critical fixes are needed:

1. **Fix in main**: Create PR to `main` with the fix
2. **Update release branch**: Either:
   - Cherry-pick specific commits from `main` to release branch
   - Merge `main` into release branch (if many changes)
   - Rebase release branch on `main` (cleanest history)

```
main ────┬───[fix]───────┬──────► 
         │               │
         └─release/r4.1──┴──────► (updated with fix)
```

### Post-Release PR Explained

After a release is tagged, several actions occur:

```
main ────┬──[src/4.1]──────────[PR: selective updates]───► 
         │                           ↑
         └─release/r4.1─────────────┘
                    ↓
                  tag:r4.1
```

**1. Tag reference point**: `src/4.1` tag is created on main where the release branched off

**2. Selective PR back to main** (cherry-picked):
- CHANGELOG entries for the release
- README updates with latest stable version links

**What does NOT get merged**:
- API version changes (placeholders like `{{api_version}}` remain unchanged)
- Server URL changes (keep placeholder format)
- Release-specific metadata

**3. For public releases**: Update `release-plan.yaml` to set all APIs to `unchanged`

**Purpose**: Makes release information visible in the default branch without disrupting ongoing development, provides reference point for maintenance branches, and ensures explicit planning for next cycle.

