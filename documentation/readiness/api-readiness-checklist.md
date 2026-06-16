# API Readiness Checklist

This document defines the release assets that API teams must provide for each release depending on the API(s) status(es), and how readiness is verified during the release process.

## Purpose

Before an API repository can be released, codeowners must ensure that certain assets are in place and meet quality expectations appropriate for the declared target API status. This checklist:

- Defines the required release assets and their expected locations
- Specifies which assets are mandatory (M) or optional (O) per API status
- Clarifies the division of responsibility: **codeowners prepare** the assets, **automation validates** what it can, and **release management reviewers** verify the rest
- Explains how to handle CAMARA Validation results (errors, warnings and hints)

Release readiness is tracked through `release-plan.yaml` configuration, release content preparation as indicated in the Release Issue, and the review checklist in the Release PR.

## Terms

| Term | Source | Values |
|------|--------|--------|
| Release type | `repository.target_release_type` | `pre-release-alpha`, `pre-release-rc`, `public-release`, `maintenance-release` |
| API status | `apis[].target_api_status` | `alpha`, `rc`, `public` |
| Initial public | Derived | API status is `public` and major version is 0 (e.g., v0.5.0) |
| Stable public | Derived | API status is `public` and major version ≥ 1 (e.g., v1.0.0) |

The Release Issue and Release PR embed the readiness matrix as a convenience copy; this document holds the reference source.

## Release Assets

| Nr | Asset | Description | Location | Automated? | What to verify |
|----|-------|-------------|----------|------------|---------------|
| 1 | Release Plan | `release-plan.yaml` updated with target release tag, release type, API versions, statuses, and dependencies | `release-plan.yaml` | Schema validated on PR | Check that API names, versions, statuses, and dependencies match intent |
| 2 | API Definition(s) | One `{api-name}.yaml` per API, following applicable ICM guidelines | `code/API_definitions/` | Spectral linting on PR; file existence checked on `/create-snapshot` | One YAML file per API; Spectral passes |
| 3 | Commonalities compliance | API definitions follow the Commonalities version declared in `release-plan.yaml` dependencies | In API definitions | Partially (Spectral rules cover structure; design guidelines require manual review) | Spectral covers structure; review design guideline adherence manually |
| 4 | API Documentation | API description in the YAML `info.description` field; additional documentation as needed | In YAML `info` section or `documentation/` | Partial (`info.description` presence checked) | `info.description` is present and meaningful |
| 5 | User Stories | At least one user story per API demonstrating the intended use | `documentation/API_documentation/` | No | At least one user story document per API exists |
| 6 | Test Cases (basic) | Sunny day scenarios and main error cases; at least one `.feature` file per API | `code/Test_definitions/` | File existence only | At least one `.feature` file per API with sunny day + main error cases |
| 7 | Test Cases (enhanced) | Rainy day scenarios, edge cases, and error handling coverage | `code/Test_definitions/` | No | Additional scenarios beyond basic: rainy day, edge cases, error handling |
| 8 | API Description | Wiki page with content for external visibility | CAMARA Sub Project Wiki | No | Wiki page is present and up to date |

## Requirements by API Status

The following matrix defines which assets are mandatory (M) or optional (O) for each target API status:

| Nr | Asset | alpha | rc | initial public | stable public |
|----|-------|:-----:|:--:|:--------------:|:------------:|
| 1 | Release Plan | M | M | M | M |
| 2 | API Definition(s) | M | M | M | M |
| 3 | Commonalities compliance | O | M | M | M |
| 4 | API Documentation | M | M | M | M |
| 5 | User Stories | O | O | O | M |
| 6 | Test Cases (basic) | O | M | M | M |
| 7 | Test Cases (enhanced) | O | O | O | M |
| 8 | API Description | O | O | M | M |

**Why this progression:**

- **Alpha**: The API is under active development. Only the API definition and basic documentation are required. Teams are iterating on the design and gathering feedback.
- **Release Candidate (rc)**: The API is feature-complete and ready for implementation testing. Commonalities compliance and basic test cases become mandatory to ensure interoperability.
- **Initial Public**: The API is ready for first implementations by external parties. All API versions in the release are initial (the major version number = 0: 0.y.z). An API Description is required for external visibility.
- **Stable Public**: The API is production-grade, with at least one API version at major version 1 or higher. All assets are mandatory, including enhanced test cases and user stories, to support production deployments.

## Preparing the release content (on main)

Before issuing `/create-snapshot` on the Release Issue, codeowners must verify the following on the `main` branch. All corrections must be made on `main` first — the release branches contain only automated changes and release documentation, not content changes.

- **`release-plan.yaml` content matches intent**: Check that API names, target versions, target statuses, and release type in `release-plan.yaml` are correct
- **Dependency versions are current**: Commonalities and ICM dependency versions in `release-plan.yaml` should reference the latest recommended releases
- **Validation checks pass**: Spectral linting and PR validation must pass on `main` - see below for handling validation results
- **All intended PRs are merged**: Implementation work should be complete on `main`
- **SemVer is correct**: Breaking changes are only allowed in initial versions (v0.x) or new major versions
- **Release assets are provided**: All mandatory assets for the declared target API status(s) are in place (see matrix above)

These items appear as a preparation checklist in the Release Issue while it is in PLANNED state. They are reminders, not automated gates — the codeowner is responsible for verifying them before proceeding.

> **Note**: During development on `main`, API version fields in the YAML definitions must stay as `wip`. The release automation process replaces them with the correct version numbers and applicable extensions during snapshot creation.

### Handling validation results 

Validation results must be handled as early as possible during each release preparation, and no later than before the final rc pre-release:

- Errors MUST be fixed (errors block snapshot creation).
- Warnings MUST be fixed or explicitly deferred by documenting them in one or more issues. The issue(s) must copy the relevant validation summary lines and include the deferral reason(s). For stable APIs, a warning that would require a breaking change while no major version update is planned is a valid deferral reason.
- Hints MUST be checked and MAY be fixed. Hints do not block snapshot creation or Release PR review.

Any warnings remaining in the final rc pre-release must have a valid deferral reason documented and need to be approved by Release Management.

## Release Readiness Reviews

During the Release PR review (SNAPSHOT ACTIVE state), two types of reviewers verify different aspects:

### Codeowner Review

Codeowners verify content accuracy:

- CHANGELOG entries are organized correctly (automation collects entries from merged PRs; codeowners must move them into the correct categories and complete them)
- API version numbers match the intent declared in `release-plan.yaml`
- API definitions are correct and complete for the target status
- Test cases cover the intended API behavior
- Documentation is adequate for the target audience
- Any remaining warnings are documented in one or more issues, with the relevant validation summary lines and deferral reason(s)

### Release Management Review

Release management reviewers verify process compliance:

- CHANGELOG follows the release documentation rules
- Breaking changes are documented and version updates follow SemVer rules
- All mandatory release assets for the declared API(s) status(es) are present as per the checklist
- All remaining warnings have been documented and have acceptable deferral reasons

The Release PR contains a status-specific review checklist that reflects the requirements for the repository's release type.

## See Also

- [Release Process Lifecycle](../release-process/lifecycle.md) — step-by-step release guide
- [How Automation Works](../automation/how-automation-works.md) — what the system does for you
- [Terminology](../release-process/terminology.md) — definitions of key terms
- [release-plan.yaml Reference](../metadata/release-plan.md) — configuration file format
