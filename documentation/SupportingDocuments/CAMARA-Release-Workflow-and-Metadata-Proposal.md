# CAMARA Release Workflow and Metadata Specification  
*Version: Proposal – Concept Phase*

## Summary of Current Situation and Pain Points

CAMARA currently coordinates releases using manual practices across GitHub repositories and external tools (e.g. a Confluence-based tracker), which presents multiple challenges:

- **Manual Release Tracking in Wiki:**  
  Status tracking is maintained manually using wiki pages, which cannot support automation or flexible reporting. Synchronizing scope and status across repositories requires redundant effort and is error-prone.

- **Informal Release PRs Merged into `main`:**  
  Releases rely on manually created PRs that are merged into `main` before tagging. These PRs often include version updates, changelog edits, and last-minute changes, introducing risk and inconsistency.

- **Limited CI Enforcement on `main`:**  
  While MegaLinter is integrated for YAML and Gherkin, there is no structured validation for metadata files or enforcement of CAMARA-specific release guidelines.

- **Unclear Versioning and Branching Strategy:**  
  Metadata and version fields are frequently changed manually in `main` prior to release, only to be reset afterward. Changes made directly in release PRs are hard to trace and review.

- **Minimal Automation for Changelogs and Checklists:**  
  CHANGELOG generation is mostly manual. The API Readiness Checklist is not fully automated and depends on manual cross-checks.

## Proposed Objectives and Guiding Principles

We are proposing the following objectives to modernize and automate the CAMARA release process:

- ✅ Clearly separate development intent (planning) from released state (actual).
- ✅ Keep the `main` branch in a consistent "work in progress" (WIP) state with version fields as `"wip"`.
- ✅ Use dedicated **release branches per (pre-)release** (e.g. for alpha, rc, release).
- ✅ Introduce structured **metadata files (in YAML)** to support automation and CI.
- ✅ Keep CAMARA **release numbering (`rX.Y`)** distinct from API **semantic versioning**.
- ✅ Enforce CI gating on PRs to `main`.
- ✅ Restrict release branch changes to authorized release managers.
- ✅ Automate creation of release branches and generation of release metadata.
- ✅ Use **Release preparation PRs** into release branches for structured approvals.
- ✅ Handle specification or implementation feedback via PRs into `main`, and re-update the release branch as necessary.

## Terminology

| Term                   | Description |
|------------------------|-------------|
| `meta_release`         | Meta-release timeline (e.g., `Fall26`) |
| `release_number`       | CAMARA release identifier within (e.g., `r4.1`). Distinct from API SemVer. |
| `release_status`       | Status of the (planned) (pre-)release: `alpha`, `rc`, or `release`. |
| `api_status`           | Per-API maturity used for gating validations. |
| `main_contacts`        | GitHub handles of code owners or maintainers (per API in `release-plan.yaml`). |
| `main` branch          | Development branch. All content is work-in-progress (`version: wip`). |
| Release branch         | Dedicated release preparation branch per (pre-)release (e.g., `release/r4.1`). |
| Release preparation PR | Pull request against a release branch to finalize or tweak the release content. |

## Metadata File Format

All metadata files are YAML-based and versioned in the repository. They serve as authoritative configuration & release inputs.

### 1. `release-plan.yaml` (on `main`)

Planning metadata owned by codeowners, manually updated and CI-validated.

```yaml
meta_release: Fall26 # default as long not eligible or planned for a meta-release: Other

release_number: r4.1

release_status: alpha  # must be one of: draft, alpha, rc, release

apis:
  - name: location-verification
    target_version: 3.2.0
    api_status: rc
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

👉 Notes:
- All APIs must meet the minimum `api_status` for the current `release_status`.
- `draft` status can't be released 
- APIs below the threshold block tagging (enforced via CI).
- Changes to the file can only be merged into main if the APIs and the repository are fulfilling the intendent status.

### 2. `release-metadata.yaml` (on release branch)

Generated automatically from the release plan and committed before tagging.

```yaml
release_number: r4.1
meta_release: Fall26
release_date: 2025-11-22
status: alpha

apis:
  - name: location-verification
    version: 3.2.0-alpha.1

  - name: location-retrieval
    version: 0.5.0-alpha.1

  - name: some-new-location-service
    version: 0.1.0-alpha.1

commonalities_version: 1.2.0-rc.1
identity_consent_management_version: 1.1.0
commit_sha: abcd1234efgh5678
release_notes: Initial alpha release for CAMARA Fall26 release cycle.
```

## End-to-End Workflow

### Step 1: Continuous Development on `main`

- All PRs target `main`, with changes validated via MegaLinter and YAML schema checks.
- `release-plan.yaml` defines the roadmap and desired targets.
- CI gates validate:
  - Formatting and schemas
  - Guideline adherence (based on `release_status` & `api_status`)
  - Status progression rules (e.g. `rc` requires all APIs are `rc` or better)

✅ Benefits:
- Prevents bad content landing in `main`
- Ensures only appropriate changes are prepared for promotion

### Step 2: Automated Release Branch Creation

Upon triggering the release (e.g., via GitHub issue or label):

- A release branch is created (e.g. `release/r4.1`)
- A script or GitHub Action:
  - Sets exact API versions using `target_version` + derived suffix (`-rc.1`, etc.)
  - Writes `release-metadata.yaml`
  - Replaces all `wip` markers in metadata
  - Commits consistent/structured changelog, README, and checklist artifacts

✅ Benefits:
- Avoids fragile manual editing
- Creates trusted, reviewable release state before tag

### Step 3: Review via Release Preparation PRs

Manual review and adjustments happen through “release preparation PRs” into the release branch.

- Only release managers can merge to release branches (via branch protection).
- Review covers CHANGELOG, checklist, metadata correctness.

If problems are found in API specs or implementation:
- Create PRs against `main`
- Update (or rebase) release branch from `main`
- Regenerate release metadata/artifacts

✅ Benefits:
- Keeps the actual release clean, visible, and traceable
- Ensures specification fixes flow through formal code review

### Step 4: Tag and Generate Release

After approval:

- A tag (e.g., `r4.1`) is created on the release branch
- CI builds and publishes artifacts
- GitHub Release, OpenAPI bundles, and documentation are generated

✅ Benefits:
- Fully traceable, repeatable state for each tagged release

### Step 5: Post-Release PR into `main`

To keep `main` updated with useful release info (but not version numbers):

- Create a PR back into `main` with:
  - CHANGELOG entry
  - README additions (e.g., new API table rows)

Do not update:
- Any version fields (they stay `"wip"`)

✅ Benefits:
- Bridges visibility, avoids disrupting ongoing WIP development state

## Summary of Benefits

| Area                   | Benefits                                                                                     |
|------------------------|----------------------------------------------------------------------------------------------|
| Separation of concerns | `main` can always be integrated or reworked — no release state mixed in                     |
| Consistent metadata    | Metadata is parseable, validatable, and source-of-truth for release tooling                 |
| Flexible compliance    | Pre-release vs public release phases are enforced via `release_status`/`api_status`         |
| CI-friendly            | No fragile manual checks — all validations declarative, structural, and branch-aware        |
| Collaborative review   | All critical changes reviewed like any other PR                                              |
| Traceable results      | Tag, commit SHA, and metadata captured in release snapshot                                  |
| Minimal backporting    | Minor fixes flow through `main` and regenerate the release — auto-tidy                     |
| Reusable tooling       | YAML format + GitHub workflows = universal scripting, readable for both devs and CI         |

## Next Steps (Optional)

- [ ] Define a YAML schema for `release-plan.yaml` and `release-metadata.yaml`
- [ ] Add GitHub Actions for metadata validation, release branch preparation, and post-release syncing
- [ ] Enforce CODEOWNERS and team-based protections on branches
- [ ] Plan and implement CHANGELOG automation as a separate phase

