
# CAMARA Release Workflow and Metadata Proposal

## Summary of Current Situation and Pain Points

CAMARA currently manages releases with largely manual processes, leading to several challenges that impede automation, traceability, and consistent quality assurance:

- **Manual Release Tracking in Wiki:**  
  Status tracking is maintained manually in an external wiki using page properties tables, which are insufficient for automation or flexible reporting. This causes duplicated effort and scope inconsistency between this tracker and GitHub repositories.

- **Informal Release PRs Merged to Main:**  
  Presently, "release PRs" are manually created and merged into the `main` branch before release, containing version bumps, changelog edits, API readiness checklists, and README updates. This approach risks inconsistency and oversight.

- **Limited CI Enforcement on `main`:**  
  The `main` branch mixes “work in progress” (WIP) development with release information, lacking strong CI gating, allowing inconsistent or incomplete APIs and metadata to merge.

- **Unclear Branching and Metadata Practices:**  
  Development and release metadata are intermingled, leading to manual version resets post-release and error-prone processes.

- **Minimal or Absent Automation for CHANGELOG and API Readiness:**  
  Though some PR template fields exist to aid automation, they are currently unused, causing manual effort to update changelogs and API readiness status.

## Proposed Objectives and Guiding Principles

To improve automation, transparency, and quality, **we are proposing** the following principles for the CAMARA release process:

- **Clearly separate development intent from released state metadata.**  
- **Keep the `main` branch in a consistent "work in progress" (WIP) state** with version fields set to `"wip"`.  
- **Use dedicated release branches per (pre-)release** — a (pre-)release being any release in a release cycle from alpha through rc to public release.  
- **Require mandatory CI gating on PRs into `main`** for guideline compliance and correctness.  
- **Adopt metadata files (in YAML) to represent release planning and snapshots.**  
- **Keep CAMARA release numbering separate and distinct from API semantic versions.**  
- **Apply branch protection rules restricting edits on release branches to release managers.**  
- **Automate creation, updating, and synchronization of release metadata and documentation.**  
- **Use “Release preparation PRs” on release branches as the review mechanism before final release tagging.**  
- **Handle review feedback via issues and PRs into `main`, followed by updates to release branches, including rebasing or repeating release preparation PRs as necessary.**

## Terminology

| Term                   | Meaning and Usage                                                                       |
|------------------------|-----------------------------------------------------------------------------------------|
| `release_number`       | CAMARA release numbering (e.g., `r2.1`) distinguishing releases in a cycle             |
| API semantic version    | Independent semantic version of each API (e.g., `3.0.0`, `0.5.0`)                      |
| `main` branch           | Development branch containing WIP versions and development intent metadata             |
| release branch          | Branch created for each (pre-)release (e.g., `release/r2.1`), holding finalized metadata and release artifacts |
| Release preparation PR  | PR opened *into* a release branch to review and finalize release metadata and artifacts |

## Metadata File Format and Content

All metadata files are written in **YAML** to align with CAMARA’s existing OpenAPI usage and to balance readability with machine parsability.

### 1. `release-plan.yaml`

Located on the `main` branch, this file represents **development intent** for the upcoming (pre-)release and steers CI and tooling.

```yaml

# Planned meta-release (requires that the APIs have at least `alpha" status, otherwise set to "Other")
meta_release_cycle: Fall26

# Release umber of the next planned (pre-)release (starts with r1.1 for new repositories)
release_number: r4.1            

# Release status (`draft`, `alpha`, `rc`, `release`)
# * Determines the set of rules which will be mandatory in PR validations
# * Use `draft` if no release is planned yet - only basic linting and rules are enforced
# * Use `alpha` to be able to create an alpha pre-release (all APIs must have at least `alpha` status as well)
# * Use `rc` to be able to create an release-candidate pre-release (all APIs must have at least `rc` status as well)
# * Use `release` to be able to create a public release (all APIs must have at least `rc` status as well)
release_status: alpha                     
                             
apis:
  - name: location-verification   # api-name, to be used in file-names and server URLs
    target_version: 3.2.0         # Semantic API version (without pre-release suffix, starts with 0.1.0 for new APIs)
    api_status: rc                # Set of rules which should be applied to this API in pull request validations
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

commonalities_version: 1.2.0-rc.1
identity_consent_management_version: 1.1.0
```

### 2. `release-metadata.yaml`

Created and committed on the release branch during the release process, this file captures the **authoritative released state** including pre-release suffixes based on the `status`.

```yaml
release_number: r2.1              # Final released CAMARA release number
meta_release_cycle: Fall25
release_date: 2025-09-14
status: rc                      # Release-wide status at release time

apis:
  - name: location-verification
    version: 3.0.0-rc.1          # Semantic API version combined with pre-release suffix

  - name: location-retrieval
    version: 0.5.0-rc.1

  - name: geofencing-subscriptions
    version: 0.5.0-rc.1

commonalities_version: 1.2.0-rc.1
identity_consent_management_version: 1.1.0
commit_sha: abc1234def5678
release_notes: Stable release candidate for CAMARA Fall25.
```

**Note:** The `release-metadata.yaml` does *not* include `main_contacts`, as contact responsibility is tracked per-API in the planning file.

## Branching and Workflow Overview

### 1. Development on `main`

- All ongoing development merges into `main` branch with `version: wip` and `release-plan.yaml` updated with intended API versions and `release_number` for the next (pre-)release.
- PRs to `main` are subject to CI gates including file format linting, CAMARA guideline validation, tests, and YAML schema validation for metadata files.
- Development teams manage `release-plan.yaml` and API code concurrently.

**Benefits:**
- Keeps `main` stable and consistent, avoiding accidental release.
- Provides a single source of truth for development intent.
- Prevents integration of invalid or inconsistent API changes.

### 2. Automated Creation of Release Branch per (Pre-)Release

- When ready to prepare a (pre-)release, automation creates a release branch from `main`. E.g., `release/r2.1`.
- Automation replaces placeholders (`wip`) with finalized `release_number`, API versions (applying suffixes like `-rc.1` per `status`), and generates the `release-metadata.yaml`.
- Additional release-specific files, e.g., changelogs and API readiness checklists, are prepared and committed in this branch.

**Benefits:**
- Isolates release artifact generation from ongoing development.
- Enables human and automated review before release.
- Prevents accidental contamination of `main`.

### 3. Review and Refinement via Release Preparation PRs

- Contributors open **Release preparation PRs** targeting the release branch for manual review tweaks (e.g., changelog edits).
- Only release managers (enforced via branch protection) can merge these PRs.
- Review comments and change requests on release content from any stakeholders are handled by:

  - Creating **issues** and corresponding **PRs into `main`** for fixes or updates.
  - After merging fixes into `main`, the release branch is updated (rebased or merged).
  - Release preparation PRs are updated, rebased, or recreated as necessary to reflect the latest main branch changes.
  - Release managers iterate through the review cycle until approval.

**Benefits:**
- Clear, controlled review process with auditable history.
- Separates development fixes from release branch content.
- Avoids unreviewed or uncontrolled changes on release branches.

### 4. Release Tagging and Publication

- After Release preparation PRs are merged and the release branch is finalized, the release manager or automation creates a release tag on the release branch.
- Builds, artifact publishing, and documentation releases are triggered for the tagged release.
- The release branch remains available until the release is published and stable.

**Benefits:**
- Creates an immutable release record.
- Supports traceability from release tag to exact source and metadata.
- Limits release triggering to controlled, reviewed states.

### 5. Post-release Synchronization Back to `main`

- Automation opens a **post-release PR** from the release branch into `main` with selective updates:
  - Changelog entries
  - README release notes or metadata visibility updates
- These PRs exclude version bumps in API or release version fields—keeping `main` versions as `wip`.
- Code owners review and merge these PRs to keep documentation consistent.

**Benefits:**
- Keeps `main` documentation current without compromising development intent state.
- Avoids manual duplicate updating and errors.
- Supports ongoing development cycles succeeding the release.

### 6. Maintenance Branches for Post-Release Fixes

- If post-release fixes or patches are needed:
  - Maintenance branches (e.g., `maintenance/r2.x`) are created.
  - These branches follow a similar guarded workflow as release branches.
- This approach cleanly separates emergency fixes from new development and releases.

## Summary of Benefits

| Aspect                               | Benefit                                                                                                  |
|------------------------------------|----------------------------------------------------------------------------------------------------------|
| Clear Separation of Development and Release States | Avoids accidental release and mixing of WIP with finalized versions.                                      |
| Consistent and Familiar YAML Metadata | Simplifies automation and review, aligned with existing CAMARA tooling.                                    |
| Controlled Review via Release Preparation PRs | Restricts release changes to qualified release managers while allowing wider collaboration on `main`.     |
| Automated CI Gating on `main` | Ensures high quality and guideline compliance before merging any development or metadata changes.             |
| Traceable and Immutable Release Records | Maintains complete provenance with tagged releases on dedicated branches.                                 |
| Flexible Yet Controlled Sync Back to Main | Documentation stays updated without disturbing ongoing development.                                       |
| Alignment with CAMARA Versioning Schemes | Clear distinction between release numbering (`rX.Y`) and API semantic versions reduces confusion.          |
| Scalable Branching Model | Supports multiple (pre-)releases and maintenance efficiently without clutter or risk.                            |
