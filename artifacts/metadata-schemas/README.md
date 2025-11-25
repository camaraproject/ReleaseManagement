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
│   ├── 02-multi-api-mixed-maturity.yaml
│   ├── 03-rc-preparation.yaml
│   ├── 04-patch-release.yaml
│   └── 05-generated-metadata.yaml
├── scripts/
│   └── validate-release-plan.py
└── README.md
```

## Schema Files

### release-plan-schema.yaml

Defines the structure for `release-plan.yaml` files maintained on the main branch.

**Key fields:**
- `repository.meta_release` - Optional meta-release label (Fall26, Spring27, or Sandbox)
- `repository.release_number` - CAMARA release tag (e.g., r4.1), must be the next available number in the release cycle or rN+1.1 for start of new release cycle
- `repository.release_readiness` - Release phase (none, pre-release, pre-release-rc, public-release, patch-release)
- `dependencies` - Dependencies on Commonalities and ICM releases
- `apis[]` - Array of APIs with target versions and status

**API status values:** `planned`, `unchanged`, `alpha`, `rc`, `public`

**Important:** API `target_version` contains only base semantic version (X.Y.Z), pre-release suffixes are auto-calculated during release.

### release-metadata-schema.yaml

Defines the structure for `release-metadata.yaml` files generated on release branches.

**Key differences from release-plan:**
- Generated fields added directly in `repository` section:
  - `release_date` - Actual release date (YYYY-MM-DD)
  - `status` - Release status (mirrors release_readiness)
  - `src_commit_sha` - Source commit SHA (40 characters)
  - `release_notes` - Optional release description
- API `version` field includes calculated suffixes (e.g., 3.2.0-rc.2)
- Dependencies include resolved semantic versions (e.g., r4.2 (1.2.0))

## Example Files

The [examples/](examples/) directory contains five scenarios:

| File | Scenario |
|------|----------|
| [01-new-repo-sandbox.yaml](examples/01-new-repo-sandbox.yaml) | New repository using Sandbox meta-release |
| [02-multi-api-mixed-maturity.yaml](examples/02-multi-api-mixed-maturity.yaml) | Multi-API repository with mixed maturity levels |
| [03-rc-preparation.yaml](examples/03-rc-preparation.yaml) | Single API preparing for first public release |
| [04-patch-release.yaml](examples/04-patch-release.yaml) | Maintenance patch on maintenance branch |
| [05-generated-metadata.yaml](examples/05-generated-metadata.yaml) | Generated release-metadata format |

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

- `commonalities_version` (not commonalities_release)
- `identity_consent_management_version` (not icm_release)
- `api_status` (not just status)
- `main_contacts` (array of GitHub usernames)

### Release Readiness vs API Status

**Repository release_readiness** determines what type of release can be created:
- `none` - No release possible (APIs missing or only planned)
- `pre-release` - Mixed API maturity allowed
- `pre-release-rc` - All APIs must be rc or public
- `public-release` - All APIs must be public
- `patch-release` - Maintenance/hotfix release

**API api_status** indicates individual API maturity:
- `planned` - Declared but not yet implemented
- `unchanged` - No changes from previous public version (not used for alpha and rc versions)
- `alpha` - Early development
- `rc` - Release candidate
- `public` - Stable release

### Meta-Release Field

The `meta_release` field is **optional**:
- Use for repositories participating in meta-releases (Fall26, Spring27, etc.)
- Use "Sandbox" for releases of initial API versions not yet in meta-releases
- Can be omitted entirely if not applicable

### Version Fields

**release-plan.yaml:**
- `apis[].target_version` - Base semantic version only (1.0.0, 0.5.0)
- No pre-release suffixes in planning

**release-metadata.yaml:**
- `apis[].version` - Full version with calculated suffix (1.0.0-rc.2, 0.5.0-alpha.1)
- Suffix is auto-calculated during release branch creation

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

**Error:** "release_number does not match pattern"
- **Fix:** Release numbers must follow format `rX.Y` (e.g., r4.1, not 4.1 or r4.1.0)

**Error:** "meta_release does not match pattern"
- **Fix:** Must be Fall26, Spring27, Sandbox, or similar pattern

**Error:** "api_status is not one of enum values"
- **Fix:** Must be exactly: planned, unchanged, alpha, rc, or public

### Semantic Errors

**Error:** "release_readiness is 'pre-release-rc' but some APIs are 'planned' or 'alpha'"
- **Fix:** For pre-release-rc readiness, all APIs must be rc or public status

**Error:** "release_readiness is 'public-release' but not all APIs are 'public'"
- **Fix:** Public releases require all APIs to have public status

### Field Name Errors

**Error:** Field names not recognized
- **Fix:** Check field names match schema definitions: `commonalities_version`, `identity_consent_management_version`, `api_status`, `main_contacts`
- **Note:** The schemas allow additional properties for extensibility, but required fields must use exact names

## Questions and Support

For questions about the metadata schemas or validation:
- Refer to the [concept document](../../documentation/SupportingDocuments/CAMARA-Release-Workflow-and-Metadata-Concept.md)
- Check the [example files](examples/)
- Review schema definitions in [schemas/](schemas/)
- Open an issue in the ReleaseManagement repository
