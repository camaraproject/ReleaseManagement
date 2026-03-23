# Testing Guidelines Audit

**Date**: 2026-03-19
**Scope**: Machine-checkable rules from API-Testing-Guidelines.md
**Sources**: API-Testing-Guidelines.md, .gherkin-lintrc (25 rules), api_review_validator_v0_6.py (test checks V6-071–V6-080)

## Methodology

1. Walked API-Testing-Guidelines.md section by section, extracting every machine-checkable requirement
2. Cross-referenced against: .gherkin-lintrc rules, v0_6 validator test alignment checks, pr_validation.yml MegaLinter integration

## Legend

**Coverage column**:
- `gherkin: <rule-name>` — rule exists in .gherkin-lintrc
- `v0_6: V6-NNN` — covered by api_review_validator_v0_6.py
- `gap` — no current implementation

**v1 Engine**: `gherkin-lint` / `python` / `manual`

---

## File Structure and Location

| ID | Rule | Coverage | v1 Engine | Notes |
|----|------|----------|-----------|-------|
| TG-001 | Test files MUST be in `code/Test_definitions/` | v0_6: V6-071 | python | Directory existence check |
| TG-002 | Each API MUST have at least one `.feature` file | v0_6: V6-072 | python | Matched by api-name prefix |
| TG-003 | Single-feature file: filename = api-name (kebab-case) | v0_6: V6-072 | python | e.g. `location-verification.feature` |
| TG-004 | Multi-feature files split by operation: `{api-name}-{operationId}.feature` | v0_6: V6-076 | python | operationId must exist in spec |
| TG-005 | Multi-feature files other grouping: `{api-name}-{description}.feature` | gap | python | No validation of description part |
| TG-006 | Filenames follow `{api-name}` or `{api-name}-{operationId}` convention | v0_6: V6-072/V6-076 | python | gherkin-lint `file-name` (kebab-case) cannot be used: convention mixes kebab-case api-name with camelCase operationId |
| TG-007 | `.feature` files must not be empty | gherkin: no-empty-file | gherkin-lint | |
| TG-008 | `.feature` files must contain scenarios | gherkin: no-files-without-scenarios | gherkin-lint | |

---

## Feature Description

| ID | Rule | Coverage | v1 Engine | Notes |
|----|------|----------|-----------|-------|
| TG-009 | Feature MUST have a name | gherkin: no-unnamed-features | gherkin-lint | |
| TG-010 | Feature name MUST include API name | gap | python | Not checked by gherkin-lint |
| TG-011 | Feature name MUST include API version | v0_6: V6-073 | python | Checks lines 1-2 for version pattern |
| TG-012 | Feature name max 250 characters | gherkin: name-length (Feature: 250) | gherkin-lint | |
| TG-013 | Feature names MUST be globally unique | gherkin: no-dupe-feature-names | gherkin-lint | |

---

## Feature Context (RECOMMENDED)

| ID | Rule | Coverage | v1 Engine | Notes |
|----|------|----------|-----------|-------|
| TG-014 | Feature context SHOULD reference API spec file location | gap | python | Pattern: `in {apiname}.yaml` |
| TG-015 | Feature context SHOULD include "Implementation indications" section | gap | manual | Recommended, not mandatory |
| TG-016 | Feature context SHOULD include "Testing assets" section | gap | manual | Recommended, not mandatory |
| TG-017 | Feature context SHOULD include "References to OAS spec schemas" | gap | manual | Recommended, not mandatory |

---

## Background Section

| ID | Rule | Coverage | v1 Engine | Notes |
|----|------|----------|-----------|-------|
| TG-018 | Background MUST NOT be empty | gherkin: no-empty-background | gherkin-lint | |
| TG-019 | Background MUST NOT exist without scenarios | gherkin: no-background-only-scenario | gherkin-lint | |
| TG-020 | Background SHOULD include environment setup (apiRoot) | gap | manual | Recommended pattern, not strictly checkable |
| TG-021 | Background SHOULD include Content-Type header setup | gap | manual | Recommended pattern |
| TG-022 | Background SHOULD include Authorization header setup | gap | manual | Recommended pattern |
| TG-023 | Background SHOULD include x-correlator header setup | gap | manual | Recommended pattern |

---

## Scenario Structure

| ID | Rule | Coverage | v1 Engine | Notes |
|----|------|----------|-----------|-------|
| TG-024 | Each scenario MUST have a name | gherkin: no-unnamed-scenarios | gherkin-lint | |
| TG-025 | Scenario names MUST be unique within feature | gherkin: no-dupe-scenario-names (in-feature) | gherkin-lint | |
| TG-026 | Scenario name max 250 characters | gherkin: name-length (Scenario: 250) | gherkin-lint | |
| TG-027 | Step name max 250 characters | gherkin: name-length (Step: 250) | gherkin-lint | |
| TG-028 | Steps MUST follow Given → When → Then order | gherkin: keywords-in-logical-order | gherkin-lint | |
| TG-029 | Repeated step keywords MUST use `And` | gherkin: use-and | gherkin-lint | |
| TG-030 | Scenario Outline MUST have Examples section | gherkin: no-scenario-outlines-without-examples | gherkin-lint | |
| TG-031 | Max 50 scenarios per file | gherkin: max-scenarios-per-file (50) | gherkin-lint | |
| TG-032 | All scenario variables MUST be defined | gherkin: no-unused-variables | gherkin-lint | |

---

## Scenario Tagging

| ID | Rule | Coverage | v1 Engine | Notes |
|----|------|----------|-----------|-------|
| TG-033 | Scenario tag format: `@{feature_identifier}_{number}_{optional_detail}` | gap | python | Pattern check on tag naming |
| TG-034 | Tag identifiers: lowercase with underscores | gap | python | Could be gherkin-lint allowed-tags pattern |
| TG-035 | Every scenario MUST have at least one tag | gherkin: required-tags (pattern: `^@.*$`) | gherkin-lint | |
| TG-036 | Tags `@watch` and `@wip` are forbidden | gherkin: no-restricted-tags | gherkin-lint | |
| TG-037 | No duplicate tags on same scenario | gherkin: no-duplicate-tags | gherkin-lint | |
| TG-038 | No superfluous tags | gherkin: no-superfluous-tags | gherkin-lint | |
| TG-039 | Single space between tags | gherkin: one-space-between-tags | gherkin-lint | |
| TG-040 | No inline comments on tag lines | gherkin: no-partially-commented-tag-lines | gherkin-lint | |

---

## Request Step Syntax

| ID | Rule | Coverage | v1 Engine | Notes |
|----|------|----------|-----------|-------|
| TG-041 | operationId in `When the request "{operationId}" is sent` MUST exist in API spec | v0_6: V6-075 | python | Cross-file: test ↔ API spec |
| TG-042 | Path parameters: `the path parameter "{name}" is set as "{value}"` | gap | manual | Standardized syntax, hard to enforce |
| TG-043 | Query parameters: `the query parameter "{name}" is set as "{value}"` | gap | manual | Standardized syntax |
| TG-044 | Headers: `the header "{name}" is set as "{value}"` | gap | manual | Standardized syntax |
| TG-045 | Request body: `the request body property "{json_path}" is set as "{value}"` | gap | manual | JSON path notation |

---

## Response Validation Syntax

| ID | Rule | Coverage | v1 Engine | Notes |
|----|------|----------|-----------|-------|
| TG-046 | Status code validation: `the response status code is {code}` | gap | manual | Standardized syntax |
| TG-047 | Schema compliance: `the response body complies with the OAS schema {ref}` | gap | manual | Standardized syntax |
| TG-048 | Error code: `the response property "$.code" is "{ERROR_CODE}"` | gap | manual | Standardized syntax |

---

## URL and Version Alignment (cross-file)

| ID | Rule | Coverage | v1 Engine | Notes |
|----|------|----------|-----------|-------|
| TG-049 | Test file URLs MUST contain correct api-name matching API spec | v0_6: V6-078 | python | Regex extraction + comparison |
| TG-050 | Test file URL version suffix MUST match API version | v0_6: V6-079 | python | Version mapping rules (wip→vwip, 1.0.0→v1, 0.3.0→v0.3) |
| TG-051 | Test file URLs SHOULD have leading slash | v0_6: V6-080 | python | Style convention (LOW severity) |
| TG-052 | Operation-specific test filenames MUST reference valid operationIds | v0_6: V6-076 | python | Cross-file: filename ↔ API spec |
| TG-053 | Orphan test files (not matching any API name) MUST be flagged | v0_6: V6-077 | python | Multi-file name matching |
| TG-066 | If operation-specific test files are used, all operationIds MUST be covered | gap | python | Completeness check: `{api-name}-{operationId}.feature` for every operationId (RC and later) |

---

## Coverage Requirements

| ID | Rule | Coverage | v1 Engine | Notes |
|----|------|----------|-----------|-------|
| TG-054 | RC: minimum basic test plan with sunny-day scenarios | gap | manual | Semantic — requires human judgment |
| TG-055 | Public release: full test plan with sunny and rainy day scenarios | gap | manual | Semantic |
| TG-056 | All HTTP statuses documented in spec MUST have test scenarios | gap | python | Cross-file: response codes in spec → scenario coverage. Feasible but complex |
| TG-057 | 3-legged token responses: MUST NOT include device identifier | gap | manual | Response content validation at runtime |
| TG-058 | 2-legged token responses: SHOULD include device identifier | gap | manual | Response content validation at runtime |

---

## Indentation and Formatting

| ID | Rule | Coverage | v1 Engine | Notes |
|----|------|----------|-----------|-------|
| TG-059 | Feature: 0 spaces indentation | gherkin: indentation | gherkin-lint | |
| TG-060 | Background/Scenario/Step: 2 spaces | gherkin: indentation | gherkin-lint | |
| TG-061 | Examples header: 4 spaces | gherkin: indentation | gherkin-lint | |
| TG-062 | Example rows: 6 spaces | gherkin: indentation | gherkin-lint | |
| TG-063 | Tags: 2 spaces indentation | gherkin: indentation | gherkin-lint | |
| TG-064 | No trailing spaces | gherkin: no-trailing-spaces | gherkin-lint | |
| TG-065 | No multiple empty lines | gherkin: no-multiple-empty-lines | gherkin-lint | |

---

## Gherkin-lint Rules Not Mapped to Testing Guidelines

These rules exist in `.gherkin-lintrc` but do not correspond to a specific testing guidelines requirement:

| Gherkin Rule | Status | Notes |
|-------------|--------|-------|
| no-homogenous-tags | ON | Quality heuristic, not in guidelines |
| allowed-tags | ON | Patterns: `^@watch$`, `^@wip$`, `^@.*$` — enforces tagging |
| new-line-at-eof | OFF | Not mentioned in guidelines |
| scenario-size (15 steps) | OFF | Not enforced; guidelines allow complex scenarios |
| only-one-when | OFF | Guidelines explicitly allow multiple When blocks |
| no-restricted-patterns | OFF | Debugging step patterns configured but disabled |

---

## Gap Summary

### Gaps addressable by gherkin-lint configuration changes

| ID | Rule | Suggested Change |
|----|------|-----------------|
| ~~TG-006~~ | ~~Filenames use kebab-case~~ | Not a gap: covered by v0_6 Python checks; gherkin-lint `file-name` cannot be used due to mixed casing (`{api-name}-{operationId}`) |
| TG-033/034 | Tag naming convention `@{feature}_{number}_{detail}` | Could use `allowed-tags` pattern: `^@[a-z][a-z0-9]*(_[a-z0-9]+)*$` |

### Gaps requiring Python checks

| ID | Rule | Priority |
|----|------|----------|
| TG-010 | Feature name includes API name | Medium |
| TG-014 | Feature context references API spec file | Low (RECOMMENDED) |
| TG-056 | All documented HTTP status codes have test scenarios | Medium (cross-file, complex) |

### Gaps that remain manual

| ID | Rule | Reason |
|----|------|--------|
| TG-015–017 | Feature context sections | Semantic content, RECOMMENDED |
| TG-020–023 | Background setup patterns | Recommended patterns, not strict syntax |
| TG-042–048 | Standardized step syntax | Natural language with alternatives allowed |
| TG-054–055 | Test coverage completeness | Requires human judgment on adequacy |
| TG-057–058 | Device identifier in responses | Runtime validation, not static |

---

## Statistics

| Category | Count |
|----------|-------|
| Total rules extracted | 65 |
| Covered by gherkin-lint | 25 |
| Covered by v0_6 validator | 10 |
| Gaps (no implementation) | 30 |
| Of which: addressable by config change | 1 |
| Of which: addressable by Python | 3 |
| Of which: remain manual | 25 |
| Gherkin rules not mapped to guidelines | 6 |
