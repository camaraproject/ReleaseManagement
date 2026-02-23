# CAMARA Release Workflow and Metadata Specification
*Version 0.1*

## Objectives

This concept document establishes an automated release process for CAMARA that addresses key challenges in managing multi-repository releases:

**Replace manual wiki-based tracking** with structured, machine-readable metadata files that enable automation, flexible reporting, and consistent status synchronization across repositories.

**Establish clear separation** between development work and release preparation by keeping the `main` branch in a consistent work-in-progress state with version fields as `"wip"`, while using dedicated snapshot branches per release attempt for alpha, rc, and public releases.

**Enable structured validation and enforcement** through CI gating on PRs to `main`, replacing limited validation with complete checks for metadata files and CAMARA-specific release guidelines.

**Provide transparent and traceable release preparation** by using dedicated snapshot branches and Release PRs with structured approvals, avoiding informal PRs merged directly into `main` that mix version updates, changelog edits, and last-minute changes.

**Support flexible versioning strategy** by keeping CAMARA release numbering (`rX.Y`) distinct from API semantic versioning, with clear metadata-driven version management instead of manual field updates in `main` that must be reset after releases.

**Enable progressive automation** for release artifacts including CHANGELOG generation and API Readiness validation (via CI), reducing manual cross-checks and enabling consistent artifact creation.

The process achieves these objectives through:

- Structured **metadata files (in YAML)** as authoritative source for release planning and status
- Dedicated **Release Issue** to track release attempts, provide a command surface, and provide information on release state progress (replacing the manual Wiki-based release tracker)
- Dedicated **snapshot branches per release attempt** with automated preparation and validation
- **CI enforcement** on PRs to `main` ensuring correctness before merge
- **Branch protection** restricting snapshot branch changes to automation only
- **Release-review branch** for collaborative documentation review, merged into snapshot via Release PR
- **Feedback integration** via PRs into `main`; discard snapshot and create new one after fixes

## Terminology

| Term                   | Description |
|------------------------|-------------|
| `release_track`        | Release track determining how repository participates: `independent` (outside meta-release, default), `meta-release` (participating in meta-release). |
| `meta_release`         | Meta-release label (e.g., `Sync26`). Only used when `release_track` is `meta-release`. |
| `target_release_tag`   | Target CAMARA release tag this release should have (e.g., `r4.1`). Distinct from API SemVer. |
| `target_release_type`  | Codeowner-declared release type for next release, validated by CI: `none` (not ready), `pre-release-alpha` (requires all APIs at alpha+), `pre-release-rc` (requires all APIs at rc+), `public-release` (requires all APIs public), `maintenance-release` (maintenance). |
| `target_api_status`    | Per-API target status for next release: `draft` (declared, basic validation), `alpha`, `rc`, `public`. Extension numbers are auto-calculated. |
| `main_contacts`        | GitHub handles of code owners or maintainers (per API in `release-plan.yaml`). |
| `main` branch          | Development branch. All content is work-in-progress (`version: wip`). |
| Maintenance branch     | Long-lived branch for maintaining older release cycles (e.g., `maintenance-r3`). See Appendix for details. |
| Snapshot branch        | Automation-owned branch per release attempt (e.g., `release-snapshot/r4.1-abc1234`). Contains mechanical changes. |
| Release-review branch          | Human-editable branch for reviewable content (e.g., `release-review/r4.1-abc1234`). Codeowners commit directly; others submit PRs from forks. Eventually merged into snapshot branch via Release PR. |
| Release PR              | Pull request from release-review branch to snapshot branch to finalize documentation. |
| Release Issue           | Workflow-managed GitHub issue for a release (rX.Y). Tracks release attempts and provides the command surface. Reflects release intent declared in `release-plan.yaml`. |

## Metadata File Format

All metadata files are YAML-based and versioned in the repository. They serve as authoritative configuration & release inputs.

### 1. `release-plan.yaml` (on `main`)

Planning metadata owned by codeowners, manually updated and CI-validated. Contains only forward-looking release plans, not historical data.

```yaml
repository:
  release_track: meta-release  # independent or meta-release
  meta_release: Sync26  # Only when release_track is meta-release
  target_release_tag: r4.1
  target_release_type: pre-release-alpha  # Repository ready for pre-release with mixed API status

dependencies:
  commonalities_release: r4.2
  identity_consent_management_release: r4.3

apis:
  - api_name: location-verification
    target_api_version: 3.2.0
    target_api_status: rc  # Status type only; extension numbers (e.g., rc.2) are auto-calculated
    main_contacts:
      - githubUser1
      - githubUser2

  - api_name: location-retrieval
    target_api_version: 0.5.0
    target_api_status: rc
    main_contacts:
      - githubUser3

  - api_name: some-new-location-service
    target_api_version: 0.1.0
    target_api_status: alpha
    main_contacts:
      - githubUser4
```

👉 Notes:
- Target API status progression: `draft` → `alpha` → `rc` → `public`
  - `draft`: API declared in release-plan.yaml but implementation in progress (basic CI validation)
  - `alpha`+: API file must exist and pass validation at declared status level
  - APIs targeting a version already released as public are automatically locked by CI
- Repository target release type determines what type of release can be created:
  - `none`: No release planned or not ready yet
  - `pre-release-alpha`: All APIs at alpha or higher (rc or public) (mix of alpha/rc/public allowed)
  - `pre-release-rc`: Requires all APIs at rc or public status (e.g., M3 milestone for meta-releases)
  - `public-release`: Requires all APIs at public status
  - `maintenance-release`: For maintenance/hotfix releases from maintenance branches
- CI validates that target API statuses match the declared repository target release type.

### 2. `release-metadata.yaml` (on snapshot branch)

Generated automatically from the release plan and committed to the snapshot branch. Serves as the authoritative source of truth for the release attempt. Preserved in each release tag, providing complete release history. Exploitable for release reporting.

```yaml
repository:
  repository_name: DeviceLocation
  release_tag: r4.1
  release_date: 2025-11-22T14:30:00Z  # Actual release date and time in ISO 8601 format (UTC)
  release_type: pre-release-alpha
  src_commit_sha: abcd1234efgh5678  # Last commit from main or maintenance branch included in this release
  release_notes: Pre-release for CAMARA Sync26 release cycle.

dependencies:
  commonalities_release: r4.2 (1.2.0-rc.1)
  identity_consent_management_release: r4.3 (1.1.0)

apis:
  - api_name: location-verification
    api_version: 3.2.0-rc.2
    api_title: "Location Verification"

  - api_name: location-retrieval
    api_version: 0.5.0-rc.1
    api_title: "Location Retrieval"

  - api_name: some-new-location-service
    api_version: 0.1.0-alpha.1
    api_title: "Some New Location Service"
```

## End-to-End Process

### Step 1: Continuous Development on `main`

- All API development related PRs target the `main` branch, with changes validated via MegaLinter and YAML schema checks.
- the `release-plan.yaml` is updated on main to reflect the roadmap and desired targets for the upcoming (pre-)release.
- CI gates validate:
  - Formatting and schema correctness
  - Strict version consistency: info.version format, server URL patterns per CAMARA rules
  - Adherence to CAMARA guidelines based on the declared repository `target_release_type` and `target_api_status`
  - APIs with target status `alpha` or higher must exist and meet validation criteria
  - APIs with target status `draft` receive basic validation (allows declaration while implementation in progress)
  - APIs targeting a version already released as public are locked (CI blocks modifications)
- CI also raises non-blocking warnings about issues that must be addressed to enable promotion to the next stage (e.g., from `alpha` to `rc`, or `rc` to `public`).
- All validation results are summarized in the CI output and posted as comments in the PR, helping developers stay informed and proactive.

**Rationale:**
- Prevents invalid or incomplete content from entering `main`
- Ensures developers align with repository release readiness expectations early
- Keeps readiness transparent across reviewers, contributors, and release managers
- Allows optional enforcement that metadata updates (e.g., status changes) must be done in dedicated PRs separate from implementation changes

### Step 2: Automated Snapshot Creation

When snapshot creation is initiated (via `/create-snapshot` command in the Release Issue):

- Validation runs against current HEAD before any branches are created
- A snapshot branch is created (e.g., `release-snapshot/r4.1-abc1234`) with SHA-based naming
- A release-review branch is created from the snapshot branch (e.g., `release-review/r4.1-abc1234`)
- A script or GitHub Action:
  - Sets exact API versions using `target_api_version` + auto-calculated extension (e.g., `-rc.2` based on consecutive numbering across API lifecycle)
  - Enforces CAMARA versioning rules: info.version follows API SemVer patterns, server URLs follow v0.x or vx patterns
  - Writes `release-metadata.yaml` to the snapshot branch (source of truth for release parameters)
  - Commits mechanical changes (versions, URLs) to snapshot branch
  - Commits automated updates as reviewable content (CHANGELOG, README) to release-review branch
  - Opens a Release PR from release-review branch to snapshot branch

**Rationale:**
- Avoids fragile manual editing of version fields and metadata
- Creates verified, reviewable release state before tag
- Separates mechanical changes (protected) from reviewable content (editable)

> **Detailed Design**: See [CAMARA-Release-Creation-Detailed-Design.md](CAMARA-Release-Creation-Detailed-Design.md) for comprehensive design including state model, command set, and bot interaction patterns.

### Step 3: Documentation Review and Release PR

Manual review and adjustments happen through the Release PR (from release-review branch to snapshot branch).

- Release PRs require approval from at least one codeowner AND at least one Release Management reviewer (enforced via branch protection on snapshot branches).
- Review covers CHANGELOG and README correctness wrt metadata
- CHANGELOG.md entries may be refined on the release-review branch (codeowners commit directly; maintainers/contributors via PRs from forks)
- Mechanical changes on the snapshot branch are protected and cannot be edited

**If problems are found in API specs or implementation (immutable snapshots):**
- Create PRs against `main` to fix the issues
- **Discard** the active snapshot via `/discard-snapshot <reason>` command
- **Retrigger** snapshot creation via `/create-snapshot` from updated `main`
- This ensures snapshot remains immutable and src_commit_sha is accurate
- Discarding snapshots is normal and expected — not a failure

**Rationale:**
- Keeps release preparation clean, visible, and traceable
- Ensures specification fixes flow through formal code review on `main`
- Immutable snapshots simplify validation and prevent drift

### Step 4: Draft and Publish Release

The release finalization follows a two-phase process:

#### Phase 1: Snapshot Creation and Review (during PR review)

1. Automation creates snapshot branch from main/maintenance HEAD (Step 2)
2. `release-metadata.yaml` on snapshot branch contains:
   - `src_commit_sha`: SHA from base branch at snapshot creation
   - Other fields derived from `release-plan.yaml`
3. Release PR is created for review (release-review branch → snapshot branch)
4. **Important - Immutable snapshot (MVP implementation)**:
   - Snapshot branch content is immutable after creation
   - Reviewable content (CHANGELOG) is on the release-review branch
   - If API corrections needed: discard snapshot, fix main, create new snapshot

#### Phase 2: Draft Creation and Publication (after PR merge)

After approval and Release PR merge to snapshot branch:

1. Automation creates draft GitHub Release (no tag yet)
2. Populates final metadata:
   - `release_date`: Current UTC timestamp
3. Codeowner reviews draft release (description from CHANGELOG, assets)
4. **Codeowner publishes** via `/publish-release --confirm <tag>` → creates git tag (e.g., `r4.1`)
5. CI builds and publishes artifacts
6. GitHub Release with artifacts is finalized:
   - Bundled OpenAPI specifications (later phase)
   - Generated documentation
   - Release metadata files

**Note:** Tag `rX.Y` is only created at final publication, not after PR merge. This provides a codeowner checkpoint before publication.

**Rationale:**
- Provides traceable, repeatable state for each tagged release
- Two-phase approach ensures metadata reflects actual release state
- Codeowner checkpoint prevents accidental publication
- Immutable snapshots simplify validation and prevent drift

### Step 5: Post-Release Actions

After release is tagged and published:

#### 5a. Update `main` branch (automated PR, human approval):
- Automation creates a PR back into `main` with:
  - CHANGELOG entry
  - README additions (e.g., new API table rows)
- Do not update any version fields (they stay `"wip"`)

#### 5b. For public releases only:
- PRs on main targeting the just-released public version are automatically locked by CI
- Any modification to these APIs will be blocked until the target_api_version and other fields are updated in the release-plan.
- Forces explicit planning for next release cycle

#### 5c. Tag reference point on `main`:
- Create tag `source/rX.Y` (e.g., `source/r4.1`) on main at branch point
- Marks commit for potential maintenance branch creation
- Reference for comparing API changes in next release
- Note: This is NOT a release tag, just a reference marker

#### 5d. Cleanup snapshot and release-review branches (optional):
- Snapshot branches (e.g., `release-snapshot/r4.1-abc1234`) are temporary scaffolding
- Release-review branches (e.g., `release-review/r4.1-abc1234`) may be kept for reference
- The git tag preserves the release permanently
- Snapshot branches can be deleted after tag creation

**Rationale:**
- Provides visibility into releases without disrupting ongoing work-in-progress development state in `main`
- Establishes clear reference points for maintenance branch creation and change comparison
- Enforces explicit planning for next release cycle after public releases

### Step 6: Maintenance and Patch Releases

For critical fixes and security patches on older release cycles:

- **Maintenance branches** (`maintenance-r3`) are created from the last commit included in that release cycle
- Patches are developed and tested on the maintenance branch
- Set `target_release_type: maintenance-release` in the maintenance branch's `release-plan.yaml`
- Follow steps 2-5 above, but create snapshot from maintenance branch instead of `main`
- Maintenance releases (r3.4, r3.5) contain only bug fixes, no new features

See Appendix for detailed branching diagrams and maintenance strategy.

## Summary of Benefits

| Area                   | Benefits                                                                                     |
|------------------------|----------------------------------------------------------------------------------------------|
| Separation of concerns | `main` can always be integrated or reworked — no release state mixed in                     |
| Consistent metadata    | Metadata is parseable, validatable, and source-of-truth for release tooling                 |
| Flexible compliance    | Pre-release vs public release phases are enforced via repository `target_release_type` and `target_api_status` |
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
- All repositories add `release-plan.yaml` with their planning e.g. for Sync26 (based on pre-populated file)
- Auto-generate meta-release overview tables from YAML files
- Wiki tracker pages deprecated (no longer maintained)
- **Parallel operation**: Manual and automated release process (selected repositories as early adopters)
- **Ambition**: Spring26 M4 milestone automated for all participating API repositories

### Sync26 (April 2026)
- Full automation implementation
- Wiki completely deprecated
- Mandatory adoption for all repositories

## Next Steps (Optional)

- [x] Define a YAML schema for `release-plan.yaml` and `release-metadata.yaml` (see `artifacts/metadata-schemas/`)
- [ ] Add GitHub Actions for metadata validation, snapshot creation, and post-release syncing
- [ ] Enforce CODEOWNERS and team-based protections on branches
- [ ] Plan and implement CHANGELOG automation as a separate phase
- [ ] Design Release Issue template with readiness attestation checklist (replaces per-API checklist files)
- [ ] Consider attaching `release-metadata.yaml` additionally as release artifact for efficient reporting

## Appendix: Metadata Status and Dependency Update Strategy

### ❗ The Problem

As in the current CAMARA release process, we risk repeating the problems caused by "monolithic" release PRs — where contributors update `release-plan.yaml` to promote an API (e.g., from `draft` to `rc`) and simultaneously attempt to fix all blocking issues in the same PR. These PRs are hard to review, difficult to verify, and blur responsibility between status declaration and implementation compliance.

Worse, when deadlines are near, this approach encourages rush patches and discourages proper code review.

### Proposed Strategy: Separate Metadata from Implementation Changes

To avoid reintroducing this problem, the following strategy is proposed and can be enforced by CI:

#### 1. **Mutual Exclusivity Rule**  
A pull request to `main` may either:
- ✅ Modify metadata (e.g., `release-plan.yaml`), or
- ✅ Modify other repository content (OpenAPI specs, test files, descriptions, etc.),  
but ❌ not both.

This applies particularly to:
- Status changes in repository `target_release_type` or per-API `target_api_status`
- Dependency updates, such as upgrading `commonalities_release`

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

### Developer Process Example

1. Developer merges a PR that corrects a missing test file for an API.
2. Once CI passes and no blocking issues remain, they open a small metadata-only PR updating the `target_api_status` from `alpha` to `rc`.
3. CI detects the change, runs combined checks, and approves if valid.

This enforces discipline, validates correctness, and maintains oversight — without compromising developer agility.

## Appendix: Branching Strategy Clarification

### Understanding Git Branches and Tags

For those newer to Git, here's how branches and tags relate in the CAMARA release process:

- **Branch**: A movable pointer to commits, used for ongoing work
- **Tag**: A permanent marker on a specific commit, used to mark releases
- **Snapshot branch**: A temporary, automation-owned branch for preparing a specific release attempt
- **Release-review branch**: A temporary branch for reviewable content, merged into the snapshot branch
- **Maintenance branch**: A long-lived branch for maintaining older releases (e.g., `maintenance-r3`)

### Snapshot Branch Lifecycle

Each release attempt gets its own **temporary** snapshot branch (SHA-based naming allows multiple attempts):

1. **Creation**: Snapshot branch `release-snapshot/r4.1-abc1234` is created from `main` (or `maintenance-rX` for patches)
2. **Preparation**: Automation sets versions, updates metadata on snapshot branch; creates release-review branch for CHANGELOG
3. **Review**: Release PR merges reviewable content from release-review branch into snapshot branch
4. **Draft**: After PR merge, draft release is created
5. **Publication**: Codeowner publishes → tag `r4.1` is created
6. **Deletion**: After tagging, snapshot branch is deleted (the tag preserves the release)

```
main ────┬──[src/4.1]──────┬──[src/4.2]──────────► (ongoing development)
         │                 │
         └─release-snapshot/r4.1-abc1234    └─release-snapshot/r4.2-def5678
              ↓                                    ↓
            tag:r4.1                             tag:r4.2
```

### Maintenance Branches

For maintaining older release cycles after new major releases:

```
main ──────┬────────────────────────────► r5.x development
           │
           └─maintenance-r3─────┬──────► r3.x maintenance (r3.4, r3.5...)
                                 │
                                 └─release-snapshot/r3.4-xyz7890
                                      ↓
                                    tag:r3.4
```

**Creation strategy**:
- Created from the last commit on `main` that was included in the release cycle to maintain
- Named `maintenance-rX` where X is the release cycle (e.g., r3 for r3.1, r3.2, r3.3...)
- Used for maintenance releases (r3.4, r3.5) containing API bug fixes
- New API minor versions go into new release cycles on `main`

**Important**: Maintenance branches are tied to **release cycles** (r3.x), not API versions. A maintenance branch can produce r3.4, r3.5 etc., each potentially containing different patch versions of the APIs.

### Updating Snapshots from Main (future feature)

> **Note:** This section describes a forward-merge approach that is **deferred for future consideration**.
> The MVP implementation uses immutable snapshots (see Step 4 above).
> If corrections are needed during release preparation, the snapshot is discarded and a new one is created from updated main.
> This approach may be reconsidered based on operational experience.

During release preparation, if critical fixes are needed:

1. **Fix in main**: Create PR to `main` with the fix
2. **Discard and recreate**: Use `/discard-snapshot` then `/create-snapshot` to create new snapshot from updated main

Alternative approaches (future consideration):
- Cherry-pick specific commits from `main` to snapshot branch
- Forward-merge `main` into snapshot branch

### Post-Release PR Explained

After a release is tagged, several actions occur:

```
main ────┬──[src/4.1]──────────[PR: selective updates]───►
         │                           ↑
         └─release-snapshot/r4.1-abc1234───────────┘
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

**3. For public releases**: PRs targeting the just-released public version on main are automatically locked by CI (any modification blocked until `target_api_version` is updated)

**Purpose**: Makes release information visible in the default branch without disrupting ongoing development, provides reference point for maintenance branches, and ensures explicit planning for next cycle.

