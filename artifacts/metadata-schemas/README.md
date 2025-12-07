# CAMARA Release Metadata Schemas

This directory contains JSON Schema definitions and validation tools for CAMARA release metadata files.

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
│   ├── 04-patch-release.yaml
│   └── 05-generated-release-metadata.yaml
├── scripts/
│   └── validate-release-plan.py
└── README.md
```

## Schema Files

### release-plan-schema.yaml

Defines the structure for `release-plan.yaml` files maintained on the main branch.

**Key fields:**
- `repository.release_track` - Release track (none, sandbox, meta-release)
- `repository.meta_release` - Meta-release label (Fall26, Spring27), required when release_track is "meta-release"
- `repository.release_tag` - CAMARA release tag (e.g., r4.1), must be the next available number in the release cycle or rN+1.1 for start of new release cycle
- `repository.release_readiness` - Declared readiness level, validated by CI against API statuses (none, pre-release-alpha, pre-release-rc, public-release, patch-release)
- `dependencies` - Dependencies on Commonalities and ICM releases
- `apis[]` - Array of APIs with api_name, target_version and api_status

**API status values:** `draft`, `alpha`, `rc`, `public`

**Important:** API `target_version` contains only base semantic version (X.Y.Z), version extensions are auto-calculated during release.

### release-metadata-schema.yaml

Defines the structure for `release-metadata.yaml` files generated on release branches.

**Key differences from release-plan:**
- Generated fields added directly in `repository` section:
  - `release_date` - Actual release date and time in ISO 8601 format (UTC)
  - `release_type` - Release type (mirrors release_readiness)
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
| [04-patch-release.yaml](examples/04-patch-release.yaml) | Maintenance patch on maintenance branch |
| [05-generated-release-metadata.yaml](examples/05-generated-release-metadata.yaml) | Generated release-metadata format |

## Validation

### Basic Validation

Validate a metadata file against its schema:

```bash
python3 scripts/validate-release-plan.py release-plan.yaml
```

The script auto-detects whether the file is a release-plan or release-metadata and selects the appropriate schema.

### With Explicit Schema

```bash
python3 scripts/validate-release-plan.py release-plan.yaml \
  --schema schemas/release-plan-schema.yaml
```

### With File Existence Checks

```bash
python3 scripts/validate-release-plan.py release-plan.yaml --check-files
```

This checks if API definition files referenced in the metadata actually exist in the repository.

### Exit Codes

- `0` - Validation passed
- `1` - Validation failed (errors found)

### Validation Features

The validator performs:

1. **Schema validation** - Checks structure, required fields, data types, and patterns
2. **Semantic checks:**
   - Release readiness consistency with API statuses
   - API status progression rules
   - Version format alignment
3. **Optional file checks** - Verifies referenced API files exist (with `--check-files`)

## Using in CI

Example GitHub Actions workflow:

```yaml
- name: Validate Release Plan
  run: |
    python3 -m pip install pyyaml jsonschema
    python3 artifacts/metadata-schemas/scripts/validate-release-plan.py release-plan.yaml
```

### Future JavaScript Implementation

The validation script is currently implemented in Python. A JavaScript version can be implemented using the `ajv` library for JSON Schema validation and `js-yaml` for YAML parsing. This will be done during the CI integration phase (Phase 1B) to align with other CAMARA validation scripts.

Recommended dependencies for JavaScript version:
- ajv (^8.12.0) - JSON Schema validator with full Draft 7 support
- ajv-formats (^3.0.1) - Format validation (date, uri)
- js-yaml (^4.1.0) - YAML parsing

## Key Concepts

### Two-File Approach

- **release-plan.yaml** lives on main branch, updated via PRs, CI-validated
- **release-metadata.yaml** lives on release branches, generated automatically, preserved in tags

### Field Naming Standards

Use these exact field names:

- `release_track` (none, sandbox, meta-release)
- `release_tag` (not release_number)
- `api_name` (not name)
- `commonalities_release` (not commonalities_version)
- `identity_consent_management_release` (not icm_release)
- `api_status` (not just status)
- `main_contacts` (array of GitHub usernames, only in release-plan.yaml)

### Release Track

**release_track** determines how the repository participates in CAMARA releases:
- `none` - No release planned
- `sandbox` - Release outside meta-release cycle
- `meta-release` - Participating in a CAMARA meta-release (requires meta_release field)

### Release Readiness vs API Status

**Repository release_readiness** determines what type of release can be triggered:
- `none` - No release planned or not ready yet
- `pre-release-alpha` - All APIs at alpha or better (mix of alpha/rc allowed)
- `pre-release-rc` - All changed APIs at rc status
- `public-release` - All APIs at public status
- `patch-release` - Maintenance/hotfix release

**api_status** indicates the individual API (achieved) validation level (and determines the version suffix in case of a release)
- `draft` - API declared but implementation in progress (basic validation)
- `alpha` - Initial implementation ready for early feedback
- `rc` - Release candidate, feature-complete version
- `public` - Published version meeting all quality requirements

**Note:** APIs targeting a version already released as public are automatically locked by CI (modifications blocked). This replaces the previous "unchanged" status.

### Meta-Release Field

The `meta_release` field is only used when `release_track` is "meta-release":
- Use meta-release labels (Fall26, Spring27) for repositories participating in meta-releases
- For sandbox releases, use `release_track: sandbox` without meta_release field

### Version Fields

**release-plan.yaml:**
- `apis[].target_version` - Base semantic version only (1.0.0, 0.5.0)
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

## Dependencies

The validation script requires:
- Python 3.7+
- pyyaml
- jsonschema

Install with:
```bash
pip install pyyaml jsonschema
```

## Common Validation Errors

### Schema Errors

**Error:** "release_tag does not match pattern"
- **Fix:** Release tags must follow format `rX.Y` where both X and Y are >= 1 (e.g., r4.1, not r0.1 or r4.0)

**Error:** "meta_release does not match pattern"
- **Fix:** Must be Fall26, Spring27, or similar pattern (SpringYY or FallYY)

**Error:** "api_status is not one of enum values"
- **Fix:** Must be exactly: draft, alpha, rc, or public

**Error:** "release_track is not one of enum values"
- **Fix:** Must be exactly: none, sandbox, or meta-release

### Semantic Errors

**Error:** "release_readiness is 'pre-release-rc' but some APIs are 'draft' or 'alpha'"
- **Fix:** For pre-release-rc readiness, all APIs must be rc or public status

**Error:** "release_readiness is 'public-release' but not all APIs are 'public'"
- **Fix:** Public releases require all APIs to have public status

### Field Name Errors

**Error:** Field names not recognized
- **Fix:** Check field names match schema definitions: `release_track`, `release_tag`, `api_name`, `commonalities_release`, `identity_consent_management_release`, `api_status`, `main_contacts` (release-plan only)
- **Note:** The schemas allow additional properties for extensibility, but required fields must use exact names

## Questions and Support

For questions about the metadata schemas or validation:
- Refer to the [concept document](../../documentation/SupportingDocuments/CAMARA-Release-Workflow-and-Metadata-Concept.md)
- Check the [example files](examples/)
- Review schema definitions in [schemas/](schemas/)
- Open an issue in the ReleaseManagement repository
