# CAMARA Release Metadata Schemas

This directory contains JSON Schema definitions for CAMARA release metadata files.

## Overview

CAMARA uses two structured metadata files to manage releases:

- **release-plan.yaml** - Planning metadata on the main branch, updated by codeowner with validated PRs
- **release-metadata.yaml** - Generated metadata on release branches, created automatically during release preparation

These schemas enable automation, validation, and consistent release tracking across all CAMARA repositories.

## Authoritative Specification

The complete specification is documented in:

[CAMARA-Release-Workflow-and-Metadata-Concept.md](../../documentation/SupportingDocuments/CAMARA-Release-Workflow-and-Metadata-Concept.md)

This document defines the metadata structure, workflow, and all field meanings. The schemas in this directory implement that specification.

## File Structure

```
metadata-schemas/
├── schemas/
│   ├── release-plan-schema.yaml      # JSON Schema for planning metadata
│   └── release-metadata-schema.yaml  # JSON Schema for generated metadata
├── examples/
│   ├── 01-new-repo-sandbox.yaml
│   ├── 02-multi-api-mixed-status.yaml
│   ├── 03-rc-preparation.yaml
│   ├── 04-maintenance-release.yaml
│   └── 05-generated-release-metadata.yaml
└── README.md
```

## Schema Files

### release-plan-schema.yaml

Defines the structure for `release-plan.yaml` files maintained on the main branch.

**Key fields:**
- `repository.release_track` - Release track (independent, meta-release)
- `repository.meta_release` - Meta-release label (Sync26, Signal27), required when release_track is "meta-release"
- `repository.target_release_tag` - CAMARA release tag this release should have (e.g., r4.1), must be the next available number in the release cycle or rN+1.1 for start of new release cycle
- `repository.target_release_type` - Declared release type, validated by CI against API statuses (none, pre-release-alpha, pre-release-rc, public-release, maintenance-release)
- `dependencies` - Dependencies on Commonalities and ICM releases
- `apis[]` - Array of APIs with api_name, target_api_version and target_api_status

**Target API status values:** `draft`, `alpha`, `rc`, `public`

**Important:** API `target_api_version` contains only base semantic version (X.Y.Z), version extensions are auto-calculated during release.

### release-metadata-schema.yaml

Defines the structure for `release-metadata.yaml` files generated on release branches.

**Key differences from release-plan:**
- Generated fields added directly in `repository` section:
  - `release_date` - Actual release date and time in ISO 8601 format (UTC)
  - `release_type` - Release type (mirrors target_release_type)
  - `src_commit_sha` - Source commit SHA (40 characters)
  - `release_notes` - Optional release description
- API `api_version` field includes calculated extensions (e.g., 3.2.0-rc.2)
- Dependencies include resolved semantic versions (e.g., r4.2 (1.2.0))

## Example Files

The [examples/](examples/) directory contains five scenarios:

| File | Scenario |
|------|----------|
| [01-new-repo-sandbox.yaml](examples/01-new-repo-sandbox.yaml) | New sandbox repository not yet in meta-release |
| [02-multi-api-mixed-status.yaml](examples/02-multi-api-mixed-status.yaml) | Multi-API repository with mixed API status values |
| [03-rc-preparation.yaml](examples/03-rc-preparation.yaml) | Single API preparing for M3 pre-release |
| [04-maintenance-release.yaml](examples/04-maintenance-release.yaml) | Maintenance patch on maintenance branch |
| [05-generated-release-metadata.yaml](examples/05-generated-release-metadata.yaml) | Generated release-metadata format |

## Validation

Validation of `release-plan.yaml` is performed by the [`pr_validation` workflow](https://github.com/camaraproject/tooling) in the `camaraproject/tooling` repository. The workflow validates PRs that modify `release-plan.yaml` against the schema and performs semantic checks including:

- Schema validation (structure, required fields, data types, patterns)
- Release type consistency with API statuses
- Meta-release field consistency with release track
- API definition file existence checks (with two-tier severity)

## Key Concepts

### Two-File Approach

- **release-plan.yaml** lives on main branch, updated via PRs, CI-validated
- **release-metadata.yaml** lives on release branches, generated automatically, preserved in tags

### Field Naming Standards

Use these exact field names:

- `release_track` (independent or meta-release)
- `target_release_tag` (in release-plan.yaml) / `release_tag` (in release-metadata.yaml)
- `api_name` (not name)
- `commonalities_release` (not commonalities_version)
- `identity_consent_management_release` (not icm_release)
- `target_api_status` (in release-plan.yaml, `api_status` not used)
- `main_contacts` (array of GitHub usernames, only in release-plan.yaml)

### Release Track

**release_track** determines how the repository participates in CAMARA releases:
- `independent` - Release outside meta-release cycle (default)
- `meta-release` - Participating in a CAMARA meta-release (requires meta_release field)

### Target Release Type vs Target API Status

**Repository target_release_type** determines what type of release can be triggered:
- `none` - No release planned or not ready yet
- `pre-release-alpha` - All APIs at alpha or better (mix of alpha/rc allowed)
- `pre-release-rc` - All changed APIs at rc status
- `public-release` - All APIs at public status
- `maintenance-release` - Maintenance/hotfix release

**target_api_status** indicates the individual API target status for the next release (and determines the version extension):
- `draft` - API declared but implementation in progress (basic validation)
- `alpha` - Initial implementation ready for early feedback
- `rc` - Release candidate, feature-complete version
- `public` - Published version meeting all quality requirements

**Note:** APIs targeting a version already released as public are automatically locked by CI (modifications blocked).

### Meta-Release Field

The `meta_release` field is only used when `release_track` is "meta-release":
- Use meta-release labels (Sync26, Signal27) for repositories participating in meta-releases
- For independent releases, use `release_track: independent` without meta_release field

### Version Fields

**release-plan.yaml:**
- `apis[].target_api_version` - Base semantic version only (1.0.0, 0.5.0)
- No version extensions are used in planning

**release-metadata.yaml:**
- `apis[].api_version` - Full version with calculated extension (1.0.0-rc.2, 0.5.0-alpha.1)
- Extension is auto-calculated during release branch creation

### Schema Extensibility

The schemas allow additional properties beyond those explicitly defined. This enables:
- Future field additions without breaking existing files (e.g., schema_version, artifacts, compliance_checks)
- Custom extensions for repository-specific needs
- Backward and forward compatibility between schema versions

Required fields and data types are still strictly enforced through the schema.

## Common Validation Errors

### Schema Errors

**Error:** "release_tag does not match pattern"
- **Fix:** Release tags must follow format `rX.Y` where both X and Y are >= 1 (e.g., r4.1, not r0.1 or r4.0)

**Error:** "meta_release does not match pattern"
- **Fix:** Must match pattern (SpringYY, FallYY, SignalYY, or SyncYY), e.g. Sync26, Signal27

**Error:** "target_api_status is not one of enum values"
- **Fix:** Must be exactly: draft, alpha, rc, or public

**Error:** "release_track is not one of enum values"
- **Fix:** Must be exactly: independent or meta-release

### Semantic Errors

**Error:** "target_release_type is 'pre-release-rc' but some APIs are 'draft' or 'alpha'"
- **Fix:** For pre-release-rc release type, all APIs must be rc or public status

**Error:** "target_release_type is 'public-release' but not all APIs are 'public'"
- **Fix:** Public releases require all APIs to have public status

### Field Name Errors

**Error:** Field names not recognized
- **Fix:** Check field names match schema definitions: `release_track`, `target_release_tag` (release-plan) / `release_tag` (release-metadata), `api_name`, `commonalities_release`, `identity_consent_management_release`, `target_api_status`, `main_contacts` (release-plan only)
- **Note:** The schemas allow additional properties for extensibility, but required fields must use exact names

## Questions and Support

For questions about the metadata schemas or validation:
- Refer to the [concept document](../../documentation/SupportingDocuments/CAMARA-Release-Workflow-and-Metadata-Concept.md)
- Check the [example files](examples/)
- Review schema definitions in [schemas/](schemas/)
- Open an issue in the ReleaseManagement repository
