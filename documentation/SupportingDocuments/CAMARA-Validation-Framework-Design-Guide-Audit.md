# Commonalities Design Guide Audit

**Date**: 2026-03-19
**Scope**: Machine-checkable rules from CAMARA-API-Design-Guide.md and CAMARA-API-Event-Subscription-and-Notification-Guide.md
**Versions compared**: r3.4 (Commonalities 0.5) vs r4.1 (Commonalities 0.6)

## Methodology

1. Walked both design guides section by section, extracting every machine-checkable requirement
2. Cross-referenced against: Linting-rules.md, current .spectral.yaml (17 CAMARA rules + core OAS), tooling#95 OWASP rules, api_review_validator_v0_6.py (80 checks)
3. Compared r3.4 tag against current r4.1 for version sensitivity

## Legend

**Coverage column**:
- `spectral: <rule-name>` — rule exists in current .spectral.yaml
- `owasp: <rule-name>` — rule exists in tooling#95 (not merged)
- `linting-rules.md: <rule-name>` — listed in Linting-rules.md but NOT in .spectral.yaml
- `v0_6: V6-NNN` — covered by api_review_validator_v0_6.py
- `core-oas: <rule-name>` — spectral:oas built-in rule
- `gap` — no current implementation

**v1 Engine**: `spectral` / `python` / `manual` / `obsolete`

**Version**: `both` / `r4.x-only` / `changed` / `r3.4-only`

---

## Section 2: Data Types

### 2.2 Data Type Constraints

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-001 | String: maxLength or enum MUST be used | owasp: api4:2023-string-limit (warn) | spectral | r4.x-only | New MUST in r4.1. Target severity: error |
| DG-002 | String: format/pattern/enum/const SHOULD be used | owasp: api4:2023-string-restricted (warn) | spectral | both | Advisory |
| DG-003 | date-time description MUST state RFC 3339 with timezone | gap | spectral | both | Regex on description field |
| DG-004 | duration description MUST state RFC 3339 | gap | spectral | both | Regex on description field |
| DG-005 | Array: maxItems MUST be specified | owasp: api4:2023-array-limit (warn) | spectral | r4.x-only | New MUST in r4.1. Target severity: error |
| DG-006 | Integer: format (int32/int64) MUST be specified | owasp: api4:2023-integer-format (warn) | spectral | r4.x-only | Was informal in r3.4. Target: error |
| DG-007 | Integer: minimum and maximum MUST be specified | owasp: api4:2023-integer-limit-legacy (warn) | spectral | r4.x-only | Was informal in r3.4. Target: error |
| DG-008 | Object: required properties MUST be listed | gap | spectral | both | Check for `required` array on object schemas |
| DG-009 | type attribute MUST be present on all properties | spectral: camara-schema-type-check (error) | spectral | both | |

### 2.2.1 Discriminator

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-010 | oneOf/anyOf SHOULD include discriminator | spectral: camara-discriminator-use (hint) | spectral | changed | Deprecated in r4.1 (was warn in r3.4) |

---

## Section 3: Errors and Responses

### 3.1 Business-level Outcomes (new in r4.1)

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-011 | contextCode values SHOULD follow API_NAME.SPECIFIC_CODE in SCREAMING_SNAKE_CASE | gap | python | r4.x-only | New section. Check if contextCode field is used |

### 3.2 Error Responses

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-012 | Error response MUST have status, code, message fields | v0_6: V6-033 | python | both | ErrorInfo schema structure. Becomes spectral with bundling (ref to CAMARA_common.yaml) |
| DG-013 | Error code MUST NOT be numeric | gap | spectral | both | Regex on error code enum values |
| DG-014 | Error code MUST be SCREAMING_SNAKE_CASE | gap | spectral | r4.x-only | New explicit requirement in r4.1 |
| DG-015 | API-specific error codes MUST follow API_NAME.SPECIFIC_CODE | gap | spectral | both | Pattern: `^[A-Z][A-Z0-9_]*\.[A-Z][A-Z0-9_]*$`. Clarified in r4.1 |
| DG-016 | All APIs MUST document 401 response | owasp: api8:2023-define-error-responses-401 (error) | spectral | both | |
| DG-017 | All APIs MUST document 403 response | gap | spectral | both | OWASP only covers 401, not 403 |
| DG-018 | CONFLICT error code is DEPRECATED | gap | python | r4.x-only | Warn if API uses CONFLICT |
| DG-019 | Error response content-type MUST be application/json | v0_6: V6-028 | spectral | both | |
| DG-020 | Error responses MUST reference ErrorInfo or allOf containing ErrorInfo | v0_6: V6-029 | python | both | Needs $ref resolution |

---

## Section 5: API Definition

### 5.1 Reserved Words

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-021 | No reserved words in paths, params, operationIds, components, security schemes | spectral: camara-reserved-words (warn) | spectral | both | |
| DG-022 | Resource names MUST NOT contain HTTP method names | linting-rules.md: camara-resource-reserved-words (warn) | spectral | both | **DISCREPANCY**: listed in Linting-rules.md but NOT in .spectral.yaml |

### 5.2 OpenAPI Version

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-023 | OpenAPI version MUST be 3.0.3 | spectral: camara-oas-version (error) | spectral | both | |

### 5.3 Info Object

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-024 | info.title MUST NOT include "API" | v0_6: V6-003; linting-rules.md: camara-info-title (tbd) | spectral | both | **DISCREPANCY**: Linting-rules.md marks "tbd", not in .spectral.yaml |
| DG-025 | info.version MUST follow semver/wip/alpha/rc | v0_6: V6-004; linting-rules.md: camara-info-version-format (tbd) | spectral | both | **DISCREPANCY**: Linting-rules.md marks "tbd", not in .spectral.yaml |
| DG-026 | info.license.name MUST be "Apache 2.0" | v0_6: V6-005 | spectral | both | |
| DG-027 | info.license.url MUST be Apache URL | v0_6: V6-006; core-oas: license-url | spectral | both | |
| DG-028 | x-camara-commonalities MUST specify version | v0_6: V6-007 | spectral | both | |
| DG-029 | info.description MUST contain "Authorization and authentication" section | v0_6: V6-010/V6-011 | python | both | Normalized text matching |
| DG-030 | info.description MUST contain "Additional CAMARA error responses" section | v0_6: V6-012/V6-013 | python | r4.x-only | New in v0.6 |
| DG-031 | info.termsOfService MUST be absent | v0_6: V6-008 | spectral | both | |
| DG-032 | info.contact MUST be absent | gap | spectral | both | core-oas has contact-properties disabled |

### 5.4 External Docs

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-033 | externalDocs MUST be present | v0_6: V6-014 | spectral | both | |
| DG-034 | externalDocs.description MUST match expected text | v0_6: V6-015 | spectral | both | "Product documentation at CAMARA" |
| DG-035 | externalDocs.url MUST be https://github.com/camaraproject/{repo} | v0_6: V6-016/V6-017 | spectral | both | |

### 5.5 Servers

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-036 | At least one server MUST be defined | core-oas: oas3-api-servers | spectral | both | |
| DG-037 | Server URL MUST follow {apiRoot}/api-name/api-version | v0_6: V6-020/V6-057 | python | both | Cross-field: URL pattern vs info.version |
| DG-038 | All servers MUST have same api-name and api-version | v0_6: partial | python | both | |

### 5.6 Tags

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-039 | Each operation SHOULD use exactly one tag | core-oas: operation-singular-tag (warn) | spectral | both | |
| DG-040 | Operation tags MUST be defined in global tags | core-oas: operation-tag-defined (warn) | spectral | both | |
| DG-041 | Tag names SHOULD use Title Case (with spaces) | gap | spectral | both | No casing rule for tags exists |

### 5.7.1 Paths

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-042 | Paths MUST use kebab-case | spectral: camara-parameter-casing-convention (error) | spectral | both | |
| DG-043 | Path parameters MUST NOT be generic {id} | spectral: camara-path-param-id (warn) | spectral | both | |
| DG-044 | Path parameter morphology SHOULD be consistent ({entityId}) | linting-rules.md: camara-path-param-id-morphology (warn) | spectral | both | **DISCREPANCY**: in Linting-rules.md but NOT in .spectral.yaml |
| DG-045 | No trailing slash on paths | core-oas: path-keys-no-trailing-slash | spectral | both | |
| DG-046 | No query string in path | core-oas: path-not-include-query | spectral | both | |

### 5.7.2 Operations

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-047 | Operations MUST have operationId | core-oas: operation-operationId | spectral | both | |
| DG-048 | operationId MUST use camelCase | spectral: camara-operationid-casing-convention (hint) | spectral | both | **SEVERITY**: .spectral.yaml=hint, Linting-rules.md=error |
| DG-049 | Operations MUST have summary | spectral: camara-operation-summary (warn) | spectral | both | |
| DG-050 | Operations MUST have description | spectral: camara-routes-description (warn) | spectral | both | |
| DG-051 | operationId MUST be unique | core-oas: operation-operationId-unique (error) | spectral | both | |
| DG-052 | Valid HTTP methods only (GET/PUT/POST/PATCH/DELETE/OPTIONS) | spectral: camara-http-methods (error) | spectral | both | |
| DG-053 | Operations MUST have at least one 2xx/3xx response | core-oas: operation-success-response | spectral | both | |

### 5.7.4 Parameters

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-054 | All parameters MUST have description | spectral: camara-parameters-descriptions (warn) | spectral | both | |
| DG-055 | Property names MUST use lowerCamelCase | linting-rules.md: camara-property-casing-convention (error) | spectral | both | **DISCREPANCY**: in Linting-rules.md but NOT in .spectral.yaml |

### 5.7.5 Request Bodies

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-056 | GET/DELETE MUST NOT have requestBody | spectral: camara-get-no-request-body (error) | spectral | both | |

### 5.7.6 Responses

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-057 | All responses MUST have description | spectral: camara-response-descriptions (warn) | spectral | both | |
| DG-058 | Array response items MUST have description | gap | spectral | r4.x-only | New requirement in r4.1 |

### 5.8.1 Schemas

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-059 | Schema names MUST use PascalCase | spectral: camara-schema-casing-convention (warn) | spectral | both | |
| DG-060 | All schema properties MUST have description | spectral: camara-properties-descriptions (warn) | spectral | both | |

### 5.8.5 Headers

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-061 | x-correlator header MUST be included | v0_6: V6-032 | spectral | both | Check parameter/header presence |
| DG-062 | x-correlator pattern MUST match expected regex | v0_6: V6-062 | spectral | both | Pattern: `^[a-zA-Z0-9-_:;.\/<>{}]{0,256}$` |

### 5.8.6 Security Schemes

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-063 | MUST use openIdConnect scheme named 'openId' | v0_6: V6-036/V6-041 | spectral | both | |
| DG-064 | openIdConnectUrl MUST use HTTPS | v0_6: V6-039 | spectral | both | |
| DG-065 | openIdConnectUrl MUST point to .well-known/openid-configuration | v0_6: V6-040 | spectral | both | |
| DG-066 | No oauth2 scheme type (must use openIdConnect) | v0_6: V6-042 | spectral | both | |

---

## Section 6: Security

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-067 | HTTPS must always be used (no HTTP) | owasp: api8:2023-no-scheme-http + no-server-http (error) | spectral | both | |
| DG-068 | Sensitive data (MSISDN/IMSI/phoneNumber) MUST NOT be in path/query params | spectral: camara-security-no-secrets-in-path-or-query-parameters (warn) | spectral | both | |
| DG-069 | Write operations MUST have security scheme | owasp: api2:2023-write-restricted (error) | spectral | r4.x-only | |
| DG-070 | Read operations SHOULD have security scheme | owasp: api2:2023-read-restricted (warn) | spectral | r4.x-only | |
| DG-071 | Short-lived access tokens with refresh | owasp: api2:2023-short-lived-access-tokens (error) | spectral | r4.x-only | |
| DG-072 | No credentials in URL parameters | owasp: api2:2023-no-credentials-in-url (error) | spectral | r4.x-only | |
| DG-073 | No numeric IDs (use UUIDs or random) | owasp: api1:2023-no-numeric-ids (error) | spectral | r4.x-only | |
| DG-074 | Admin endpoints: unique security scheme | owasp: api5:2023-admin-security-unique (error) | spectral | r4.x-only | |
| DG-075 | No unconstrained additionalProperties | owasp: api3:2023-no-additionalProperties (warn) | spectral | r4.x-only | |
| DG-076 | Constrained additionalProperties | owasp: api3:2023-constrained-additionalProperties (warn) | spectral | r4.x-only | |
| DG-077 | 401 response MUST be defined on all operations | owasp: api8:2023-define-error-responses-401 (error) | spectral | both | |
| DG-078 | Error validation response (400/422/4XX) SHOULD be defined | owasp: api8:2023-define-error-validation (warn) | spectral | r4.x-only | |

### 6.6 Scope Naming

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-079 | Scopes MUST follow api-name:[resource:]action pattern | v0_6: V6-050 | python | both | Context-dependent (subscription vs regular) |
| DG-080 | Subscription POST scopes: api-name:event-type:create | v0_6: V6-051 | python | both | |
| DG-081 | Subscription GET scopes: api-name:read | v0_6: V6-052 | python | both | |
| DG-082 | Subscription DELETE scopes: api-name:delete | v0_6: V6-053 | python | both | |

---

## Section 7: Versioning (context-dependent)

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-083 | info.version MUST be wip on main branch | v0_6: V6-054 | python | both | Requires branch context |
| DG-084 | info.version MUST NOT be wip on release branches | v0_6: V6-056 | python | both | Requires branch context |
| DG-085 | Server URL version MUST match info.version | v0_6: V6-057 | python | both | Cross-field validation |

---

## Naming Conventions (complete list)

Consolidated from design guide sections. This is the full set for the detailed design appendix.

| Element | Convention | Spectral Name | DG Section | Coverage |
|---------|-----------|--------------|------------|----------|
| Paths (URLs) | kebab-case | camara-parameter-casing-convention | 5.7.1 | Implemented (error) |
| Path parameters | lowerCamelCase (entityId form) | camara-path-param-id, camara-path-param-id-morphology | 5.7.1 | Partial (morphology not in .spectral.yaml) |
| Schemas | PascalCase | camara-schema-casing-convention | 5.8.1 | Implemented (warn) |
| operationId | camelCase | camara-operationid-casing-convention | 5.7.2 | Implemented (hint; should be error per Linting-rules.md) |
| Properties | lowerCamelCase | camara-property-casing-convention | 5.7.4 | **Not in .spectral.yaml** (Linting-rules.md: error) |
| Enum values | UPPER_SNAKE_CASE (macro) | camara-enum-casing-convention | 3.2 | **Not in .spectral.yaml** (Linting-rules.md: info, tbd) |
| Tags | Title Case (with spaces) | — | 5.7.3 | **Gap** — no rule exists |
| Headers | kebab-case | — | 5.8.5 | **Gap** — implied by x-correlator convention |
| Scope names | kebab-case with : separators | — | 6.6 | v0_6 only (V6-050) |
| API name | kebab-case | — | 1.2 | v0_6 only (V6-058/V6-059) |
| Event type | org.camaraproject.\<api\>.\<ver\>.\<event\> | — | Event Guide 3.1 | **Gap** |
| Error codes | SCREAMING_SNAKE_CASE | — | 3.2 | **Gap** (r4.x-only explicit) |
| API-specific error codes | API_NAME.SPECIFIC_CODE | — | 3.2.1 | **Gap** |

---

## Event Subscription and Notification Guide

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-086 | Event type MUST follow org.camaraproject.\<api\>.\<ver\>.\<event\> | gap (v0_6 partial) | python | both | |
| DG-087 | specversion MUST be "1.0" enum | gap | spectral | both | |
| DG-088 | Subscription API filename MUST append "subscriptions" | gap | python | both | Filesystem check |
| DG-089 | Explicit subscriptions: 4 operations (POST/GET/GET{id}/DELETE) | v0_6: V6-065/V6-066 | python | both | |
| DG-090 | protocol attribute MUST be "HTTP" | gap | spectral | both | Enum constraint |
| DG-091 | sink MUST use HTTPS URI | gap | spectral | both | |
| DG-092 | sinkCredential MUST NOT appear in responses | gap | python | both | |
| DG-093 | notificationsBearerAuth scheme for callbacks | v0_6: V6-037/V6-044–046/V6-048 | python | both | |
| DG-094 | Notification content-type: application/cloudevents+json | gap | spectral | both | |
| DG-095 | Event version independent of API version | gap | python | both | Complex versioning logic |
| DG-096 | Implicit subscriptions: callbacks defined in operations | v0_6: V6-067 | python | both | |

---

## Cross-File Checks

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-097 | Common schemas identical across API files | v0_6: V6-068 | python/obsolete | both | Becomes partially obsolete with bundling |
| DG-098 | License identical across API files | v0_6: V6-069 | python | both | |
| DG-099 | x-camara-commonalities identical across API files | v0_6: V6-070 | python | both | |
| DG-100 | Test directory exists | v0_6: V6-071 | python | both | |
| DG-101 | Test files exist for each API | v0_6: V6-072 | python | both | |
| DG-102 | Test file version alignment | v0_6: V6-073 | python | both | |
| DG-103 | Filename uses kebab-case | v0_6: V6-058 | python | both | |
| DG-104 | Filename matches api-name in server URL | v0_6: V6-059 | python | both | |

---

## Telco Language and Spelling

| ID | Rule | Coverage | v1 Engine | Version | Notes |
|----|------|----------|-----------|---------|-------|
| DG-105 | Avoid telco-specific terminology | spectral: camara-language-avoid-telco (hint) | spectral | both | |
| DG-106 | Spelling check on descriptions | linting-rules.md: camara-language-spelling (No/warn) | spectral | both | Listed but explicitly not enabled |

---

## Gap Summary

### Gaps requiring new Spectral rules (r4.x ruleset)

| ID | Rule | Priority |
|----|------|----------|
| DG-003 | date-time description MUST state RFC 3339 | Low (advisory) |
| DG-004 | duration description MUST state RFC 3339 | Low (advisory) |
| DG-008 | Object: required properties MUST be listed | Medium |
| DG-013 | Error code MUST NOT be numeric | Medium |
| DG-014 | Error code MUST be SCREAMING_SNAKE_CASE | Medium (r4.x-only) |
| DG-015 | API-specific error codes: API_NAME.SPECIFIC_CODE | Medium |
| DG-017 | All APIs MUST document 403 response | Medium |
| DG-032 | info.contact MUST be absent | Low |
| DG-041 | Tag names SHOULD use Title Case | Low |
| DG-058 | Array items MUST have description | Medium (r4.x-only) |
| DG-087 | specversion MUST be "1.0" | Low (subscription APIs only) |
| DG-090 | protocol MUST be "HTTP" | Low (subscription APIs only) |
| DG-091 | sink MUST use HTTPS | Low (subscription APIs only) |
| DG-094 | Notification content-type: cloudevents+json | Low (subscription APIs only) |

### Gaps requiring Python checks

| ID | Rule | Priority |
|----|------|----------|
| DG-011 | contextCode SCREAMING_SNAKE_CASE format | Low (r4.x-only) |
| DG-018 | CONFLICT error code deprecated warning | Low (r4.x-only) |
| DG-086 | Event type format validation | Medium |
| DG-088 | Subscription API filename convention | Medium |
| DG-092 | sinkCredential not in responses | Medium |
| DG-095 | Event version independence from API version | Low |

### Rules already covered by v0_6 but not by Spectral (need Python in v1)

Most v0_6 checks that need Python (V6-010, V6-012, V6-029, V6-050–053, V6-054–057, V6-068–080) will continue to need Python in v1 due to cross-field, cross-file, or context-dependent logic.

---

## Linting-rules.md Discrepancies

Rules listed in Linting-rules.md but **NOT implemented** in current .spectral.yaml:

| Linting-rules.md Rule | Severity | Status | Notes |
|------------------------|----------|--------|-------|
| camara-resource-reserved-words | warn | Missing | Resource names must not contain HTTP method names |
| camara-path-param-id-morphology | warn | Missing | Consistent {entityId} morphology |
| camara-property-casing-convention | error | Missing | Property names lowerCamelCase |
| camara-enum-casing-convention | info | Missing (tbd) | Enum values UPPER_SNAKE_CASE |
| camara-info-title | warn | Missing (tbd) | Title must not contain "API" |
| camara-info-version-format | warn | Missing (tbd) | Version format x.y.z/wip/alpha/rc |
| camara-language-spelling | warn | Missing (No) | Spell checking on descriptions |

Rules in .spectral.yaml but **NOT listed** in Linting-rules.md:
- None found — all current .spectral.yaml rules are listed

## Severity Alignment Issues

| Rule | .spectral.yaml | Linting-rules.md | Design Guide Intent |
|------|----------------|-------------------|---------------------|
| camara-operationid-casing-convention | hint | error | MUST (error appropriate) |
| camara-schema-casing-convention | warn | warn | MUST in DG text (error may be more appropriate) |
| camara-path-param-id | warn | warn | Aligned |
| camara-operation-summary | warn | warn | Aligned |

---

## Version-Sensitive Rules Summary

### New in r4.x (not applicable to r3.4 repos)

| ID | Rule | OWASP? |
|----|------|--------|
| DG-001 | String maxLength/enum MUST | Yes |
| DG-005 | Array maxItems MUST | Yes |
| DG-006 | Integer format MUST | Yes |
| DG-007 | Integer min/max MUST | Yes |
| DG-011 | contextCode naming | No |
| DG-014 | Error code SCREAMING_SNAKE_CASE | No |
| DG-018 | CONFLICT deprecated | No |
| DG-030 | info.description error responses section | No |
| DG-058 | Array items description | No |
| DG-069–078 | All OWASP rules | Yes |

### Changed between versions

| ID | Rule | r3.4 | r4.x |
|----|------|------|------|
| DG-010 | Discriminator on oneOf/anyOf | warn (recommended) | hint (deprecated) |
| DG-048 | operationId casing | hint | error (per Linting-rules.md) |

### Implications for per-version Spectral rulesets

- The r3.4 Spectral ruleset is effectively the current .spectral.yaml (no OWASP, no new MUSTs)
- The r4.x ruleset adds: OWASP rules (from tooling#95) + new CAMARA rules for DG-014, DG-058, and the missing Linting-rules.md rules
- OWASP api4 rules have current (warn) and target (error) severities — target is for 2027 releases

---

## Statistics

| Category | Count |
|----------|-------|
| Total rules extracted | 106 |
| Covered by existing Spectral | 26 |
| Covered by OWASP (tooling#95) | 17 |
| Covered by v0_6 validator only | 28 |
| Gaps (no implementation) | 20 |
| Multiple coverage | 15 (overlap) |
| r4.x-only rules | 19 |
| Changed between versions | 2 |
| Linting-rules.md discrepancies | 7 |
| Severity alignment issues | 2 |
