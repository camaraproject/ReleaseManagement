# Validation Framework — Requirements (Internal Draft)

**Status**: Work in progress
**Last updated**: 2026-03-17

---

## 1. Use Cases

### 1.1 Contributor (including dev agents)

UC-01: Check a fix/feature branch on a fork before creating a PR (via GitHub workflow dispatch).

UC-02: See validation results of a PR check in an understandable form, with hints how to resolve failures.

UC-03: Run most validation rules locally (on local clones, via scripts).

UC-04: Check the code base before starting work, to be aware of existing issues (relevant for dev agents and new contributors).

### 1.2 Codeowner

UC-05: Rely on PR checks — if green, the branch fulfills formal requirements for the intended release as defined in release-plan.yaml.

UC-06: Check at any time if the main branch is ready to be released, or which issues remain open (via workflow dispatch on main).

UC-07: See the consequences of a release-plan.yaml change — a PR that only changes release-plan.yaml triggers a re-run, surfacing newly relevant rules.

### 1.3 Release Automation

UC-08: Use validation as a strict gate before creating a release snapshot.

UC-09: Use validation to check the release review PR (strict, also restricting allowed changes to README and CHANGELOG).

### 1.4 Rule Developer

UC-10: Run rule changes against existing release branches as regression tests or to assess impact.

UC-11: Define rule applicability conditions and conditional severity based on context (see section 2.2).

UC-12: Define fix hints for failed checks.

### 1.5 CAMARA Admin

UC-13: Introduce the validation framework incrementally, with central configuration of enabled functionality per repository (no per-repo config files that create change noise).

UC-14: Validate that an API repository is correctly configured for the validation framework.

UC-15: Test the validation framework on feature branches with pinned refs (same mechanism as release automation).

### 1.6 Release Manager (independent)

UC-16: See a dashboard indicating compliance of API repository main branches against their declared intent. *(Independent work — Release Progress Tracker can collect last validation run on merged PR or main branch, trigger validation as camara-release-automation bot.)*

UC-17: Trigger a validation check on selected repositories to update dashboard status. *(Independent — requires validation to be operational but does not depend on specific framework version.)*

---

## 2. Validation Contexts

### 2.1 Validation Profiles

Three profiles control blocking behavior. The framework selects the profile automatically based on how validation is invoked.

| Profile | Blocking behavior | Typical trigger |
|---------|-------------------|-----------------|
| **advisory** | Nothing blocks; all findings shown | Local run, dispatch |
| **standard** | `error` blocks; `warn` and `hint` shown | PR (fork-to-upstream or upstream branch) |
| **strict** | `error` and `warn` block; `hint` shown | Release automation gates (snapshot, release review PR) |

### 2.2 Rule Model

Each rule defines two things:

1. **Applicability conditions** — when the rule fires at all
2. **Conditional level** — what severity it produces, which can vary by context

The profile (section 2.1) then determines which levels block. This separates three concerns cleanly:

- **Rule developer** controls: when a rule applies and what level it produces
- **Framework** controls: which profile is active
- **Profile** controls: which levels block

#### Levels

| Level | Meaning | Blocked by profile |
|-------|---------|-------------------|
| **error** | Must be fixed | standard, strict |
| **warn** | Should be fixed | strict |
| **hint** | Recommendation, never blocking | *(none)* |
| **off** | Suppressed, finding not shown | *(n/a)* |

#### Rule metadata

Rule metadata is expressed in YAML. Fields that are not constrained are omitted (omitted = applies in all contexts for that dimension). The primary use of the metadata is **post-filter and severity mapping**: engines run and produce findings, then the framework applies applicability and conditional level to interpret the results in the current context.

```yaml
id: "042"                    # flat sequential ID, stable across engine changes
name: path-kebab-case        # human-readable name
engine: spectral             # spectral | yamllint | gherkin | python | manual
engine_rule: "camara-parameter-casing-convention"  # native engine rule ID (if applicable)
hint: "Use kebab-case for all path segments: /my-resource/{resourceId}"

applicability:               # only list fields that constrain; omitted = no constraint
  branch_types: [main, release]
  trigger_types: [pr, dispatch]
  # ... further conditions as needed

conditional_level:
  default: error             # always present
  overrides:                 # only if level varies by context
    - condition:
        target_release_type: [pre-release-alpha]
      level: hint
```

#### Applicability conditions

A rule is skipped silently if its conditions don't match the current context. Multiple fields are combined with AND; multiple values within an array field are combined with OR.

| Field | Type | Values | Source |
|-------|------|--------|--------|
| `branch_types` | array | `main`, `release`, `maintenance`, `feature` | Target branch (PR) or checked branch (dispatch) |
| `trigger_types` | array | `pr`, `dispatch`, `release-automation` | How validation was invoked |
| `target_release_type` | array | `none`, `pre-release-alpha`, `pre-release-rc`, `public-release`, `maintenance-release` | `repository.target_release_type` in release-plan.yaml |
| `target_api_status` | array | `draft`, `alpha`, `rc`, `public` | `apis[].target_api_status` in release-plan.yaml (per-API) |
| `target_api_maturity` | array | `initial` (0.x.y), `stable` (x.y.z, x>=1) | Derived from `apis[].target_api_version` |
| `api_pattern` | array | `request-response`, `implicit-subscription`, `explicit-subscription` | Detected from OpenAPI spec content (per-API) |
| `commonalities_release` | string | Range expression, e.g. `">=r3.4"` | `dependencies.commonalities_release` in release-plan.yaml |
| `release_plan_changed` | boolean | `true`, `false` | Whether release-plan.yaml is in the PR diff (PR trigger only) |

Range comparison for `commonalities_release` uses `packaging.specifiers` (Python) with release tags normalized to comparable values.

#### Conditional level

`default` is always present. `overrides` is a list of `{condition, level}` pairs evaluated in order; first match wins. Conditions use the same field/value model as applicability (AND across fields, OR within arrays). The level `off` can be used in overrides to suppress a finding in specific contexts.

Examples:

```yaml
# "Test definition must be present" — hint by default, warn for RC/public of stable APIs
conditional_level:
  default: hint
  overrides:
    - condition:
        target_api_maturity: [stable]
        target_release_type: [pre-release-rc, public-release]
      level: warn

# "Commonalities compliance check" — warn by default, suppressed for draft APIs
conditional_level:
  default: warn
  overrides:
    - condition:
        target_api_status: [draft]
      level: off
```

#### Execution context

The framework constructs a context object at runtime from the trigger, branch, and release-plan.yaml content. Rules are evaluated per-API for API-specific checks (a repository with three APIs at different statuses produces three evaluation contexts).

| Context field | Type | Source |
|---------------|------|--------|
| `branch_type` | string | Derived from branch name |
| `trigger_type` | string | Workflow event |
| `release_plan_changed` | boolean | PR diff (PR trigger only) |
| `target_release_type` | string | release-plan.yaml `repository.target_release_type` |
| `commonalities_release` | string | release-plan.yaml `dependencies.commonalities_release` |
| `icm_release` | string | release-plan.yaml `dependencies.identity_consent_management_release` |
| `target_api_status` | string | release-plan.yaml `apis[].target_api_status` (per-API) |
| `target_api_maturity` | string | Derived from `apis[].target_api_version` (per-API) |
| `api_pattern` | string | Detected from OpenAPI spec content (per-API) |
| `is_release_review_pr` | boolean | Detected by framework (used for profile selection; also available as applicability condition, see section 11.4) |

`is_release_review_pr` is used at the framework level to select the strict profile. It is also available as an optional applicability condition for checks specific to the release review context (section 11.4).

### 2.3 Execution Contexts

The validation framework must support these execution contexts:

| Context | Trigger | Profile | Token | Notes |
|---------|---------|---------|-------|-------|
| **PR (fork-to-upstream)** | `pull_request` event | standard | read-only | Default GitHub behavior: fork PRs get read-only GITHUB_TOKEN regardless of author's repo permissions. Limits output options (no check run annotations, no PR comments via token) |
| **PR (upstream branch)** | `pull_request` event | standard | write | PR from upstream branch. Note: codeowners should normally use forks too |
| **Dispatch (upstream repo)** | `workflow_dispatch` | advisory | write | Main (default), maintenance, release branches. Warning on non-standard branches |
| **Dispatch (fork repo)** | `workflow_dispatch` | advisory | write (fork scope) | Fork owner triggers on own fork. Inherited — no extra work if dispatch trigger exists |
| **Local** | CLI / script | advisory | n/a | No GitHub context; subset of rules |
| **Release automation: snapshot** | Called by release workflow | strict | write (app token) | Gate before snapshot creation (section 11.1) |
| **Release automation: review PR** | `pull_request` event (push to PR branch) | strict | write or read-only | Same trigger as normal PR; profile is strict based on release review PR detection (section 11.3) |

**Profile is independent of token permissions.** A fork-to-upstream PR gets the same **standard** profile as an upstream-branch PR. The read-only token only limits *how results are surfaced* (e.g. no check run annotations via GITHUB_TOKEN), not validation strictness. Alternative output paths for read-only contexts (workflow summary, `pull_request_target`, bot token) are a Session 4 topic.

**Dispatch is always advisory.** Dispatch runs have nothing to block (except the workflow itself). They surface errors, warnings, and hints for the user to review.

**Who can dispatch**: Standard GitHub permission model — write access required. On upstream: codeowners and org-wide teams (admin, release_reviewer). On forks: fork owner.

---

## 3. MVP Scope

The MVP replaces `pr_validation` v0 and delivers the minimum useful validation on PRs and dispatch.

### MVP includes

- UC-01 through UC-07 (contributor and codeowner use cases)
- UC-13 (incremental rollout with central config)
- UC-15 (feature branch testing with pinned refs)
- Profiles: advisory and standard
- Execution contexts: PR (fork-to-upstream), PR (upstream branch), dispatch (upstream repo), dispatch (fork repo)
- Existing Spectral rules and YAML linting
- Understandable output with fix hints
- Caller workflow with all triggers from day one (PR, dispatch), deployed alongside `pr_validation` v0
- Central enable/disable per repository (no per-repo config files)

### Post-MVP priorities

- UC-08, UC-09 (release automation strict gates, section 11) — high priority, requires strict profile; depends on PR integration being operational first
- UC-10 (regression testing against release branches) — rule developer tooling
- UC-14 (repository configuration validation) — admin tooling
- Automated cache synchronization for `code/common/` and strict version enforcement — bundling itself (ref resolution via `$ref`) is MVP scope (see section 7.3)
- Python-based consistency checks beyond what Spectral covers — Session 2 scope, may partially land in MVP

### Independent work (not sequenced with MVP)

- UC-16, UC-17 (dashboard, section 12.3) — Release Progress Tracker can collect last validation run results and trigger validation with appropriate permissions

### MVP rollout model

1. Deploy caller workflow with all triggers to repositories alongside `pr_validation` v0; reusable workflow starts as no-op for most triggers
2. Enable advisory checks on dispatch
3. Enable standard checks on PRs
4. Enable blocking via GitHub rulesets (errors only)
5. Expand repository set incrementally via central include list

---

## 4. Check Inventory

### 4.1 Authoritative Sources

The validation rules are derived from the following upstream documents. Rules must be validated against the version of these documents matching the declared `commonalities_release` in release-plan.yaml.

**Commonalities** (version-dependent — r3.4 = v0.6.x, r4.1/r4.2 = v0.7.x):
- `CAMARA-API-Design-Guide.md` — API design rules, versioning, error handling, naming conventions
- `CAMARA-API-Event-Subscription-and-Notification-Guide.md` — subscription and notification patterns

**Release Management:**
- `release-plan-schema.yaml` — field definitions and allowed values for release-plan.yaml
- `release-metadata-schema.yaml` — field definitions for generated release-metadata.yaml on release branches
- `api-readiness-checklist.md` — release asset requirements matrix by API status and maturity

### 4.2 Check Engines

| Engine | Scope | Current status |
|--------|-------|----------------|
| **Spectral** | OpenAPI structural and naming rules against `code/API_definitions/*.yaml` | Active in `pr_validation` v0 (~47 rules) |
| **yamllint** | YAML formatting for `code/API_definitions/*.yaml` | Active in `pr_validation` v0 (via MegaLinter) |
| **gherkin-lint** | Test file structure for `code/Test_definitions/*.feature` | Active in `pr_validation` v0 (via MegaLinter) |
| **Python** | Cross-file consistency, release-plan validation, context-dependent checks | Partially active (release-plan validation only); api-review v0.6 deprecated |
| **manual** | Checks too semantic to automate; framework provides prompts for human/AI review | Not yet implemented |

### 4.3 Implementation Classification

Each check falls into one of five categories:

| Category | Description |
|----------|-------------|
| **spectral** | Implementable as a Spectral rule (single-file OpenAPI checks, pattern matching, schema structure) |
| **python** | Requires Python implementation (cross-file checks, release-plan awareness, file existence, version consistency) |
| **manual** | Too semantic to fully automate (e.g., data minimization, meaningful descriptions). Framework generates a prompt or checklist |
| **obsolete** | Handled by release automation — validation framework should not re-check (e.g., readiness checklist file management, release tag creation, version field replacement on release branches) |
| **existing** | Already implemented in current Spectral/yamllint/gherkin rules. Severity mapping to be determined when individual rules are classified |

### 4.4 Check Inventory Status

The per-rule inventory is **not yet complete**. The following work is required:

1. **Commonalities audit** (dependency): Examine `CAMARA-API-Design-Guide.md` and `CAMARA-API-Event-Subscription-and-Notification-Guide.md` at both r3.4 and r4.1/r4.2 versions to:
   - Identify checks not yet covered by any engine
   - Validate existing Spectral rules against the current design guide
   - Identify rules that changed between Commonalities releases

2. **Existing rule classification**: Map each current Spectral rule to the framework metadata model (applicability, conditional level, hints). The existing Spectral severity levels are assumed valid for now; detailed severity review is deferred.

3. **api-review v0.6 coverage**: The deprecated `api_review_validator_v0_6.py` (~43 checks) was a monolithic implementation used manually by release reviewers for the Fall25 meta-release. Its checks serve as input for identifying Python-needed validations not covered by Spectral.

### 4.5 Known Check Areas by Engine

Summary of check areas identified so far, pending the Commonalities audit for completeness:

**Spectral (existing + new):**
- OpenAPI version enforcement (3.0.3)
- Naming conventions (paths: kebab-case, schemas: PascalCase, operationId: camelCase)
- Required descriptions (operations, parameters, responses, properties)
- Reserved words detection
- Security: no secrets in path/query parameters
- HTTP method validity, no request body on GET/DELETE
- Unused components detection
- *New*: info.version format (wip/alpha.n/rc.n/public), XCorrelator pattern, phone number format, device object structure

**Python (new):**
- Server URL version consistency with info.version (cross-field)
- Version must be wip on main, must not be wip on release branches (context-dependent)
- release-plan.yaml non-exclusivity check (PR diff analysis)
- release-plan.yaml schema and semantic validation (existing, to be integrated)
- Error response structure and code compliance (cross-schema)
- Test file existence and version alignment (cross-file)
- CHANGELOG format and link tag-locking (file content analysis)
- API pattern-specific checks: subscription endpoints, CloudEvents format, event type naming (structural + semantic)

**Manual + prompt:**
- Data minimization compliance (GEN-009, GEN-010)
- Meaningful description quality (beyond presence checks)
- User story adequacy
- Breaking change justification

**Obsolete (handled by release automation):**
- API Readiness Checklist file management (files should no longer be in the repository)
- Release tag creation and format
- Version field replacement on release branches (wip → actual version)
- release-metadata.yaml generation
- README update with release information

---

## 5. Rule Architecture

### 5.1 Overview

The framework uses a **post-filter and severity mapping** architecture:

1. Framework determines the execution context (branch type, trigger, release-plan.yaml content)
2. Engines run (Spectral, yamllint, gherkin-lint, Python checks) and produce findings
3. Framework collects all findings
4. For each finding: look up rule metadata → is it applicable in this context? → what level? → apply profile (advisory/standard/strict) to determine blocking
5. Produce unified output with hints

Individual checks may use the context object as a pre-condition for expensive operations (e.g., release-plan validation only runs if `release_plan_changed` is true on PR trigger, or always on `release-automation` trigger). This is a performance optimization, not a generalized orchestration model.

### 5.2 Rule Metadata Model

See section 2.2 for the full metadata model. Key design decisions:

- **Flat ID namespace**: Sequential IDs (e.g., `042`) that are stable across engine changes. A rule migrating from Python to Spectral keeps its ID.
- **Engine as metadata**: The `engine` field records which engine implements the check. The `engine_rule` field maps to the native rule ID (e.g., Spectral rule name) for configuration synchronization.
- **Condition language**: Plain YAML with AND across fields, OR within arrays. Range comparison on `commonalities_release` uses `packaging.specifiers` (Python). No custom DSL or policy engine.
- **Per-API evaluation**: API-specific rules are evaluated once per API in the repository, using the API's own `target_api_status`, `target_api_maturity`, and `api_pattern` from release-plan.yaml and OpenAPI spec content.

### 5.3 Spectral Pass-Through Principle

The framework uses Spectral's severity names (`error`, `warn`, `hint`) as its native level values. This gives identity mapping for the primary engine:

| Spectral | Framework | Notes |
|----------|-----------|-------|
| `error` | `error` | Identity |
| `warn` | `warn` | Identity |
| `hint` | `hint` | Identity |
| `info` | `hint` | Mapped (rarely used) |
| `off` | `off` | Identity (disable rule) |

Spectral rules already include `message` fields with fix guidance. Therefore, **Spectral rules that do not need context-dependent severity or applicability filtering do not require explicit framework metadata entries**. Their findings pass through with direct severity mapping and native messages.

Framework metadata is only needed for Spectral rules when:
- The level should change based on context (e.g., error on release branch, hint on feature branch)
- The rule should be suppressed in certain contexts (applicability filtering)
- The fix hint should be overridden or augmented

This minimizes the metadata surface: only rules with context-dependent behavior need explicit entries.

The framework consumes Spectral output as structured data (JSON), not terminal text. This enables programmatic post-filtering, severity remapping, and merging with findings from other engines.

Spectral does not resolve `$ref` references before linting — it validates the document as-is. Checks that depend on the content of referenced schemas (e.g., from CAMARA_common.yaml) require either a pre-bundled input spec or a Python implementation with explicit ref resolution. See Session 3 (Bundling & Refs) for implications.

For further Spectral-specific implementation details, see [spectral-integration-notes.md](../reviews/spectral-integration-notes.md).

### 5.4 Condition Evaluation

```
applicability match:
  for each field in rule.applicability:
    if field is array: context value must be IN the array (OR)
    if field is range string: context value must satisfy the range expression
    if field is boolean: context value must equal the field value
  all fields must match (AND)
  omitted fields are unconstrained (always match)

conditional level:
  for each override in rule.conditional_level.overrides (in order):
    if override.condition matches context (same logic as applicability):
      return override.level
  return rule.conditional_level.default
```

### 5.5 Derived Context Fields

Two per-API context fields are derived from content rather than declared in release-plan.yaml:

**`target_api_maturity`**: Derived from `apis[].target_api_version` — `initial` if major version is 0 (v0.x.y), `stable` if major version >= 1 (vx.y.z). Determines which asset requirements apply per the API Readiness Checklist (e.g., stable public APIs require enhanced test cases and user stories).

**`api_pattern`**: Detected from OpenAPI spec content — `request-response`, `implicit-subscription`, or `explicit-subscription`. Detection logic examines paths (subscription endpoints), callbacks, schema names, and content types. Multiple pattern-specific rule sets (REQ, IMP, EXP, EVT categories) depend on this classification. This detection is a cross-cutting capability used by many rules.

### 5.6 Spectral Migration Potential

Analysis of the deprecated `api_review_validator_v0_6.py` shows that approximately 40% of its checks are implementable as Spectral rules (single-file OpenAPI pattern matching), and an additional 15% could use Spectral custom JavaScript functions. This includes:

- Mandatory error response checks (400, 401, 403)
- Server URL format validation
- info.version format validation
- License and security scheme validation
- ErrorInfo and XCorrelator schema presence
- Error response structure validation

The main blocker for migrating ~20% of checks to Spectral is the dependency on `api_pattern` detection — Spectral cannot natively apply rules conditionally based on detected API type. These checks either need custom JS functions that embed the detection logic, or remain as Python checks that use `api_pattern` from the context.

The Commonalities audit (OQ-05) should evaluate each candidate check against the current design guide version before migration.

### 5.7 Authoritative Schema References

The execution context fields and their allowed values are defined by the following schemas, which are the authoritative sources:

- **release-plan.yaml**: `upstream/traversals/ReleaseManagement/artifacts/metadata-schemas/schemas/release-plan-schema.yaml`
- **release-metadata.yaml**: `upstream/traversals/ReleaseManagement/artifacts/metadata-schemas/schemas/release-metadata-schema.yaml`

The framework must accept exactly the values defined in these schemas. Any change to the schemas must be reflected in the framework's context model.

---

## 6. Open Questions

OQ-01: *(Resolved — fork dispatch is inherited automatically if the caller workflow supports dispatch.)*

OQ-02: *(Resolved — bundling for `CAMARA_common.yaml` via `$ref` is within MVP scope. Automated cache sync and strict version enforcement are post-MVP. See section 7.3.)*

OQ-03: What is the minimum set of checks for MVP? Just current Spectral + YAML lint, or also a subset of Python checks? *(Partially addressed by Session 2: the Commonalities audit will identify which checks are needed and which are feasible without bundling.)*

OQ-04: *(Resolved — layered token resolution: validation app bot as default, GITHUB_TOKEN write as fallback, read-only as last resort. Dedicated validation GitHub App separate from camara-release-automation. `pull_request_target` rejected due to security risk at scale. See section 9.1.)*

OQ-05: Commonalities audit — per-rule validation of existing Spectral rules and identification of missing checks against `CAMARA-API-Design-Guide.md` and `CAMARA-API-Event-Subscription-and-Notification-Guide.md` at r3.4 and r4.1/r4.2 versions. Required before the check inventory can be completed.

OQ-06: Sub-project common dependency declaration format — should sub-project dependencies (repository, release tag, array of files) be declared within `release-plan.yaml` or as a separate manifest? See section 7.4.

OQ-07: API-aware change summary tooling — evaluate oasdiff or alternatives for semantic OpenAPI diff summaries. Post-MVP. See section 8.6.

OQ-08: OIDC token availability for fork PRs — does `id-token: write` work when a fork PR triggers the reusable workflow? If not, the hardcoded version fallback (section 9.5) handles ref resolution, but the exact OIDC behavior should be confirmed empirically as part of WP-01 validation.

---

## 7. Bundling & Refs

The overall bundling model — controlled local copy on `main`, source-only `main`, bundled release artifacts — is defined in the [Commonalities Consumption and Bundling Design](https://github.com/camaraproject/ReleaseManagement/pull/436) document. This section captures what the validation framework checks about that model, not the model itself.

### 7.1 Repository Model Validation

The framework validates the repository layout and `$ref` patterns used in API source files.

#### Layout validation

When any API source file in `code/API_definitions/` contains a `$ref` to `../common/` or `../modules/`, the framework validates:

- The referenced file exists at the expected path
- `code/common/` contains only cache copies from other repositories (e.g., `CAMARA_common.yaml` from Commonalities). These files are CI-managed, not manually edited. Content validation is covered in section 7.4.
- `code/modules/` contains project-local reusable schemas used to make the API source more readable and structured. No sync validation is needed for these files.

#### Ref pattern validation

- API source files must use only relative `$ref` for normative schema consumption — into `code/common/`, `code/modules/`, or same-directory references
- Remote URL-based `$ref` (e.g., `https://raw.githubusercontent.com/...`) used for normative schema content is an error
- Internal component references (`#/components/...`) are always valid

#### Transition handling

Repositories not yet using `code/common/` (i.e., the current copy-paste model with all schemas inline) remain valid. The layout and ref pattern checks only fire when `$ref` to `../common/` or `../modules/` is detected in source files. The framework does not force migration to the local copy model.

### 7.2 Source vs Bundled Validation

The framework applies a uniform validation flow regardless of context:

1. **Pre-bundling validation** (always runs on source files):
   - YAML validity (yamllint)
   - Ref existence and pattern validation (section 7.1 — do referenced files exist? are refs relative and canonical?)
   - Release-plan.yaml consistency checks (Python)
   - Cross-file checks that do not depend on schema content (file existence, version field presence)

2. **Bundling** (if `$ref` to `code/common/` or `code/modules/` is detected):
   Resolve all local refs and produce a standalone spec per API. The framework invokes an external bundling tool — it does not implement its own OpenAPI bundler/dereferencer. Tool choice is an implementation detail.

3. **Full validation** (runs on the *effective input* — bundled output when refs are present, source directly when no refs):
   - Full Spectral ruleset — all schemas are inline/resolved
   - Python checks that depend on schema content
   - Standalone API spec validation

4. **Artifact surfacing**: Upload bundled specs as workflow artifacts or make them available for further processing (see section 8)

This flow applies to all contexts — PR, dispatch on any branch type, release automation. The validation **profile** (advisory, standard, strict) controls which findings block; it does not change which steps run.

#### Bundling failure

If the bundling step fails (e.g., unresolvable `$ref`, missing file), the framework reports the failure as an error finding. Full validation (step 3) is skipped; only pre-bundling results are available.

#### Repositories without `$ref`

Repositories using the current copy-paste model (all schemas inline) skip step 2. Source files are standalone by construction, so the full Spectral ruleset runs directly on source in step 3. No bundling overhead is introduced for repositories that have not adopted the local copy model.

### 7.3 Spectral and `$ref` Interaction

#### Bundling vs full dereferencing

The framework uses **bundling** (external ref resolution only), not full dereferencing:

- **Bundling**: Resolves external `$ref` — pulls content from `code/common/`, `code/modules/`, and other local files into the document. Internal `$ref` (`#/components/schemas/...`, `#/components/responses/...`) are preserved.
- **Full dereferencing**: Resolves all `$ref` including internal ones, producing a flat document with zero `$ref` and massive duplication. The framework must **not** use full dereferencing.

Preserving internal `$ref` ensures that:

- Spectral rules checking component structure, `$ref` patterns, and `#/components/` organization continue to work on bundled output
- Bundled output remains readable and structurally equivalent to what reviewers expect
- No Spectral rule changes are needed between copy-paste and bundled models

Any constraints on where API designers may use external vs internal `$ref` are defined in the [bundling design document](https://github.com/camaraproject/ReleaseManagement/pull/436), not by the validation framework. The framework enforces whatever ref patterns the design document specifies.

#### Transition period

During migration from copy-paste to the local copy model, both repository types coexist:

- **Copy-paste repos**: All schemas inline. Spectral runs directly on source (step 3 of section 7.2). No bundling needed.
- **`$ref` repos**: Spectral runs on bundled output. All external refs resolved, internal refs preserved. Structurally equivalent to copy-paste.

No rule changes are needed between the two models — bundling normalizes external refs while preserving the internal structure that Spectral rules depend on. Rule IDs remain stable across the transition (flat namespace from section 5.2).

#### OQ-02 resolution — bundling is MVP scope

Bundling support for `CAMARA_common.yaml` via `$ref` is **within MVP scope**. Commonalities 0.7.x requires updated common schemas, and the ability to consume them via `$ref` — with the framework handling bundling transparently — is the key additional value of the validation framework v1 for codeowners. This avoids repeating the difficult-to-validate copy-paste pattern.

In the MVP, some parts may still be manual — providing the correct copy in `code/common/` and ensuring it matches the declared `commonalities_release` version. But the `$ref` option is available for early adopters, and the framework handles bundling when `$ref` is detected. Automated cache synchronization and strict version enforcement are post-MVP enhancements.

### 7.4 Cache Synchronization and Dependency File Mapping

#### Cache sync validation

When `code/common/` exists, the framework validates that cached files match the declared dependency versions in `release-plan.yaml`. Mismatch severity depends on the profile:

- **standard** (PR): warning — codeowner is informed, merge is not blocked
- **strict** (release automation): error — snapshot creation is blocked

If no `code/common/` directory exists (repo has not adopted the local copy model), the sync check is skipped.

In the MVP, cache management may be manual. The validation check still applies — it reports whether the current cache matches the declared dependency, regardless of how the cache was populated.

#### Dependency categories

Three categories of shared schema dependencies exist, each with different characteristics:

**Commonalities** (well-known, hardcoded in tooling):
The Commonalities repository provides shared schemas that are well-known to automation tooling. Currently two files are relevant:
- `CAMARA_common.yaml` — common data types, error responses, headers
- `notification-as-cloud-event.yaml` — CloudEvents notification schema

These files, their source location in the Commonalities repository, and the mapping from `release-plan.yaml.dependencies.commonalities_release` to the correct version are built into the tooling. No per-repository configuration is needed.

**ICM** (version compatibility constraint):
Identity and Consent Management schemas are currently contained within Commonalities files — there are no separate ICM files to cache. The `dependencies.identity_consent_management_release` in `release-plan.yaml` is a version compatibility constraint (potentially `>= x.y.z`) rather than a file-caching relationship. The exact nature of this dependency requires further discussion.

**Sub-project commons** (extensible, declared per repository):
Sub-projects may define common schemas shared across their API repositories (e.g., a device API family sharing common device type definitions). These dependencies must be declarable without requiring changes to the automation tooling. Each sub-project dependency requires:
- Source repository
- Release tag or version
- Array of files to consume

This extensible model requires a dependency declaration format, either within `release-plan.yaml` or as a separate manifest. The schema design is a follow-up topic for the bundling design document.

#### File caching strategy

Which files are cached in `code/common/` — demand-driven (only files actually `$ref`'d) vs declaration-driven (all files from declared dependencies) — is a sync mechanism concern defined in the [bundling design document](https://github.com/camaraproject/ReleaseManagement/pull/436), not a validation framework decision.

The framework's checks are the same regardless: cached files must match their declared source version, and `$ref` targets must exist.

### 7.5 Commonalities Version Matrix

#### Active versions

The framework must support validation rules that vary by Commonalities version. Active versions at the time of writing:

- **r3.4** (Commonalities v0.6.x) — Fall25 meta-release, frozen, maintenance releases only
- **r4.x** (Commonalities v0.7.x) — Spring26 meta-release. r4.1 is the release candidate (available now); r4.2 is the upcoming public release and will replace r4.1

Within a version line (r4.x), the latest release is always authoritative. When r4.2 is available, r4.1 becomes obsolete — new releases must target r4.2. If a maintenance release r4.3 follows, it replaces r4.2 for validation purposes.

Future Commonalities major versions (e.g., r5.x for v1.0.0) will add further version lines. The architecture must not assume a fixed number of active versions.

#### Spectral ruleset selection (pre-selection)

Each Commonalities major version line gets its own Spectral ruleset (e.g., `.spectral-r3.4.yaml`, `.spectral-r4.yaml`). The framework reads `commonalities_release` from `release-plan.yaml` and selects the matching ruleset before running Spectral.

This avoids running contradicting rules from different Commonalities versions simultaneously, which would produce confusing Spectral output even if the results were filtered afterwards. The r3.4 ruleset is effectively frozen — only maintenance fixes. New rule development targets the current r4.x ruleset.

#### Framework rule metadata (post-filter with conditionals)

Framework rule metadata uses a single ruleset with `commonalities_release` range conditions (defined in section 2.2) for version-specific behavior. This is appropriate because:

- Python checks are framework-controlled and do not produce confusing intermediate output
- Most framework rules apply across versions; only a minority are version-specific
- Duplicating shared rules into per-version files would create drift risk

The Commonalities audit (OQ-05) will identify which rules changed between r3.4 and r4.x. Those rules receive `commonalities_release` range conditions in their metadata.

### 7.6 Placeholder Handling

#### Current state

The current `CAMARA_common.yaml` contains placeholder patterns (e.g., `{{SPECIFIC_CODE}}`) that have no defined resolution rules. These should be removed from Commonalities, with API repositories extending shared schemas via `allOf` instead (per the [bundling design document](https://github.com/camaraproject/ReleaseManagement/pull/436)).

#### Future direction

Placeholder replacement with defined values could be introduced together with bundling as part of a broader transformation pipeline. This could include dynamic variables such as `api_version`, `commonalities_release`, `commonalities_version`, effectively replacing the current "wip" and "/main/" substitutions done by the snapshot transformer. In this model, bundling + transformation (including placeholder replacement) would produce the release-ready artifact.

#### Framework requirements

- The framework detects unreplaced placeholder patterns (`{{...}}`) in bundled output and reports them as errors — this is a permanent safety net
- As of now, placeholder replacement is not a framework responsibility. If placeholder replacement becomes part of the bundling/transformation pipeline, it is a post-MVP enhancement
- Detection of undefined/unresolvable placeholders remains an error regardless of whether replacement is implemented

### 7.7 Rule Architecture Integration

Bundling integrates into the rule architecture (section 5) without requiring changes to the context model or rule metadata:

- **Step assignment**: Each rule runs in either step 1 (pre-bundling validation) or step 3 (full validation). Assignment is an implementation detail — the framework knows which checks belong to which step.
- **No new context fields**: The context model from section 2.2 is sufficient. Whether external refs existed and were resolved is an implementation concern, not a rule applicability condition.
- **Cache sync is a check, not context**: The cache synchronization validation (section 7.4) produces findings (warning or error depending on profile). It is not a context field consumed by other rules.
- **Spectral ruleset selection**: The `commonalities_release` field (already in the context model) drives Spectral ruleset pre-selection (section 7.5). No additional metadata is needed.

#### Relationship to snapshot creation

Resolved in section 11.2. The validation framework produces the bundled API specs as part of its validation pipeline (steps 2-3 above). These bundled specs are consumed by release automation for the snapshot branch — bundling happens once, during validation, and the output is handed off to release automation.

## 8. Artifact Surfacing

This section covers how bundled artifacts are surfaced for reviewer visibility. Findings surfacing (how validation errors, warnings, and hints are presented) is a separate topic covered in Session 4 (OQ-04).

### 8.1 PR Review Surfaces

The [bundling design document](https://github.com/camaraproject/ReleaseManagement/pull/436) defines a priority order for reviewer visibility. The framework produces:

1. **Source diff** — primary review surface, no framework action needed (standard git diff)
2. **Bundled artifact** — the framework uploads the bundled standalone API spec as a GitHub workflow artifact for each API affected by the PR
3. **Bundled diff** — a diff between the bundled API from the PR base and the bundled API from the PR head, uploaded as a workflow artifact or included in the workflow summary
4. **API-aware summary** — optional semantic change summary (see section 8.5)

### 8.2 Workflow Artifacts

- Bundled specs are uploaded as GitHub workflow artifacts with a naming convention that identifies the API name, branch, and commit SHA
- Bundled files include a header comment: `# For information only - DO NOT EDIT`
- Workflow artifact retention uses the GitHub default (90 days)

### 8.3 Line Number Mapping

When checks run on bundled output (step 3 of section 7.2), findings report line numbers in the bundled file. These do not correspond to the source files where the issue should be fixed. The framework must map finding locations in the bundled output back to source file and line number, so that findings are actionable for contributors and codeowners.

### 8.4 Temporary Branch Model

Workflow artifacts replace the temporary branch model (`/tmp/bundled/<branch>-<SHA>`) for MVP. Temporary branches may be revisited post-MVP if reviewers need a browsable view of bundled content.

### 8.5 "wip" Version Handling

Bundling on `main` leaves `info.version` as-is — it contains `wip` as expected for unreleased code. Version replacement on release branches is handled by release automation (snapshot transformer), not by the validation framework's bundling step. The framework validates version correctness per branch type — this is an existing check (section 4.5), not a new bundling-specific requirement.

### 8.6 API-Aware Change Summaries

The framework should support pluggable diff tools for generating semantic change summaries (breaking changes, new endpoints, modified schemas). oasdiff is a candidate implementation. This capability is post-MVP — source diff, bundled artifact, and bundled diff provide sufficient reviewer visibility for MVP.

---

## 9. Caller Workflow Design

### 9.1 Findings Surfacing

#### Surfacing categories

Two categories of output are surfaced to users:

**A. Findings output** (validation errors, warnings, hints with fix guidance):

| Surface | Description | Requires write token |
|---------|-------------|---------------------|
| **Workflow summary** | Structured markdown in the Actions run summary. Primary detailed surface with all findings, fix hints, and links to diagnostic artifacts | No |
| **Check run annotations** | Inline annotations in the PR diff, mapped to file and line. Findings appear directly where the issue is | Yes |
| **PR comment** | Concise summary on the PR: error/warn/hint counts, blocking status, link to full workflow summary | Yes |
| **Commit status** | Per-check context visible in the PR checks list (e.g., `--> Validate: release-plan.yaml`). Continuation of the v0 pattern | Yes |

**B. Diagnostic artifacts** (log files, detailed engine output):

| Artifact | Description |
|----------|-------------|
| **Spectral JSON log** | Full structured Spectral output for debugging rule behavior |
| **Engine reports** | Detailed per-engine output (replaces v0 MegaLinter report artifacts) |
| **Bundled spec artifacts** | Standalone bundled API specs (see section 8.2) |

Diagnostic artifacts are always uploaded as GitHub workflow artifacts regardless of token permissions. They have no fork PR limitation.

#### Workflow summary size limit

GitHub limits workflow step summaries to 1 MB per step and 1 MB total per job. For repositories with many APIs or many findings, this limit may be exceeded. The framework must:

- Truncate the summary when approaching the limit, showing a count ("50 of 127 findings shown") with a link to the full diagnostic artifact
- Prioritize errors over warnings over hints in the truncated view
- Always include the full findings in the Spectral JSON log artifact (no size limitation on workflow artifacts)

#### Token resolution

The framework uses a layered token resolution strategy. The order prioritizes consistent branding (all findings come from the same bot identity) over using whichever token happens to be available:

1. **Snapshot context**: `camara-release-automation` app token — provided by the calling release workflow. The validation framework does not mint this token; it is passed in by the release automation caller.
2. **Validation default**: Dedicated validation app bot token — the framework mints an installation token for the current repository. This is the primary path for all PR and dispatch contexts, ensuring consistent bot identity on annotations and comments.
3. **Fallback**: `GITHUB_TOKEN` with write access — used when the validation app is not installed (e.g., dispatch in a fork, or repositories not yet onboarded to the app). Write capability is probed at runtime.
4. **Read-only**: Workflow summary and diagnostic artifacts only — when no write token is available.

In normal operation, both upstream PRs and fork PRs show findings from the validation bot. The `GITHUB_TOKEN` fallback and read-only mode are degraded paths, not the expected default.

#### Validation GitHub App

A dedicated GitHub App handles write surfaces for validation. This is a **separate app** from `camara-release-automation` — it has a narrower permission scope and a different purpose.

| Aspect | Validation App | camara-release-automation |
|--------|---------------|--------------------------|
| **Purpose** | PR annotations, comments, commit status | Release snapshot creation, branch management |
| **Permissions** | `checks: write`, `pull-requests: write`, `statuses: write` | `contents: write`, `workflows: write`, plus release management |
| **Commits/pushes** | Never | Yes (snapshot branches, tags, release assets) |
| **EasyCLA** | Not needed (no commits) | Required (commits to repos with CLA enforcement) |

Org-level configuration:
- `vars.VALIDATION_APP_ID` — app ID (org variable)
- `secrets.VALIDATION_APP_PRIVATE_KEY` — app private key (org secret)

The validation app is introduced from day one (MVP) to establish consistent bot identity and avoid caller workflow changes later.

#### Surfaces by resolved capability

| Token capability | Findings output | Diagnostic artifacts |
|-----------------|-----------------|---------------------|
| **Write** (validation app, camara-release-automation, or GITHUB_TOKEN) | Workflow summary + check run annotations + PR comment + commit status | Workflow artifacts (always) |
| **Read-only** (all write paths failed) | Workflow summary only | Workflow artifacts (always) |

#### Relationship to v0 surfacing

The v0 workflow surfaces findings via MegaLinter's built-in reporters (`GITHUB_COMMENT_REPORTER`, `GITHUB_STATUS_REPORTER`) and custom `actions/github-script` steps for release-plan validation. The v1 framework replaces all of these with its own unified surfacing layer. MegaLinter is no longer used as the orchestration layer.

### 9.2 Trigger Design

#### PR trigger

```yaml
on:
  pull_request:
    branches:
      - main
      - release-snapshot/**
      - maintenance/**
```

- **`main`**: Standard development PRs. Profile: standard (or strict if release review PR detected)
- **`release-snapshot/**`**: Release review PRs created by release automation on snapshot branches. Profile: strict
- **`maintenance/**`**: Maintenance branch PRs. Profile: standard

Default event types (`opened`, `synchronize`, `reopened`) are sufficient. The framework validates code content, not PR metadata — `edited` (title/body changes) is not needed.

#### Dispatch trigger

```yaml
  workflow_dispatch:
```

Dispatch runs on whatever branch the user selects in the GitHub UI. The framework derives branch type, release context, and all validation parameters from the checked-out branch content. Dispatch inputs are discussed in section 9.4.

#### Concurrency

```yaml
concurrency:
  group: ${{ github.ref }}-${{ github.workflow }}
  cancel-in-progress: true
```

Same model as v0: a new push to a PR branch cancels the previous validation run. Dispatch behaves identically — a second dispatch on the same branch cancels the first.

### 9.3 Permissions

The caller workflow declares the maximum permission set. The reusable workflow inherits these as a ceiling — it cannot elevate above what the caller declares.

```yaml
permissions:
  checks: write
  pull-requests: write
  issues: write
  contents: read
  statuses: write
  id-token: write
```

| Permission | Purpose | Fork PR behavior |
|------------|---------|-----------------|
| `checks: write` | Check run annotations (findings inline in PR diff) | Restricted by GitHub; validation app token used instead |
| `pull-requests: write` | PR review interactions | Restricted by GitHub; validation app token used instead |
| `issues: write` | PR comments (PRs use the Issues API for comments) | Restricted by GitHub; validation app token used instead |
| `contents: read` | Repository checkout | Available (read-only) |
| `statuses: write` | Commit status (per-check context in checks list) | Restricted by GitHub; validation app token used instead |
| `id-token: write` | OIDC token for tooling ref resolution (WP-01 pattern) | May not be granted for fork PRs — see section 9.5 |

For fork PRs, `GITHUB_TOKEN` write permissions are restricted by GitHub regardless of what the caller declares. The validation app token (section 9.1) bypasses this restriction because it is minted from the app's own credentials, independent of `GITHUB_TOKEN`.

### 9.4 Input Design Principle

The reusable workflow does not accept inputs that duplicate information derivable from the checked-out branch. This prevents contradictions where an input says one thing but branch content says another.

**Example of the problem avoided**: If the workflow accepted a `release_type` input, a user could dispatch on `main` with `release_type: public-release` while `release-plan.yaml` on `main` says `target_release_type: pre-release-alpha`. The framework would need reconciliation logic, and the user would get confusing results.

**The rule**: The framework reads branch type from the branch name, and all release context from `release-plan.yaml` on the checked-out branch. These values are derived at runtime, never accepted as inputs.

**Forbidden inputs**: `branch_type`, `release_type`, `api_status`, `commonalities_version`, `configurations` — all derivable from branch content or from the central configuration file (section 10.2).

**Consequence for the caller workflow**: No per-repo inputs exist. All per-repo configuration (linting config subfolder, enabled features, rollout stage) lives in the central config file read by the reusable workflow. The caller workflow is identical across all repositories, with no `with:` block needed in standard operation. This makes it protectable via CODEOWNERS or rulesets — nobody ever needs to edit it.

### 9.5 Ref Resolution

#### OIDC-based ref resolution (primary)

The reusable workflow resolves its own tooling repository and commit SHA via OIDC claims (`job_workflow_sha`), following the pattern established in WP-01 (tooling#121). This ensures all internal checkouts (linting config, shared actions at runtime) use the same tooling version that the caller specified.

The caller workflow declares `id-token: write` to enable OIDC token generation.

#### Hardcoded version fallback

If OIDC token generation fails (e.g., fork PRs where `id-token: write` may not be granted), the reusable workflow falls back to its own hardcoded version tag (e.g., `v1`). This is the same pattern as v0's hardcoded `ref: v0`.

This fallback is acceptable because:
- **Fork PRs**: Contributors do not need pinned-SHA ref resolution — the release version tag (`v1`) is correct for production validation
- **Feature branch testing**: Done by admins and rule developers who have write access, so OIDC works
- **Release automation**: Always triggered by codeowners with write access, so OIDC works

The fallback means fork PR validation always uses the published version of the tooling, not a feature branch. This is the expected behavior — only admins test unreleased tooling versions.

#### Break-glass override

`tooling_ref_override` — a 40-character SHA input to the reusable workflow. Takes precedence over both OIDC and the hardcoded fallback. Documented as pilot/break-glass only. Same mechanism as release automation.

#### Resolution order

1. `tooling_ref_override` input (if set) — explicit SHA, highest priority
2. OIDC `job_workflow_sha` claim (if `id-token` available) — exact commit SHA
3. Hardcoded version tag in the reusable workflow (e.g., `v1`) — always available

### 9.6 Reusable Workflow Contract

#### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `tooling_ref_override` | string | no | *(empty)* | 40-character SHA for non-standard tooling ref. Takes highest priority in ref resolution (section 9.5). Supports testing in contexts where OIDC may not work. Documented as pilot/break-glass only. |
| `profile` | choice | no | *(auto)* | Validation profile: `advisory`, `standard`, `strict`. Default: framework selects based on context — advisory for dispatch, standard for PR, strict for release review PR or release automation. Dispatch users can set explicitly to see what a different profile would flag. |

No per-repo inputs. All per-repo configuration lives in the central config file (section 10.2).

#### Caller workflow

The caller workflow is identical across all repositories:

```yaml
name: CAMARA Validation

on:
  pull_request:
    branches:
      - main
      - release-snapshot/**
      - maintenance/**
  workflow_dispatch:

concurrency:
  group: ${{ github.ref }}-${{ github.workflow }}
  cancel-in-progress: true

permissions:
  checks: write
  pull-requests: write
  issues: write
  contents: read
  statuses: write
  id-token: write

jobs:
  validation:
    uses: camaraproject/tooling/.github/workflows/validation.yml@v1
    secrets: inherit
```

No `with:` block in standard operation. The caller is a thin pass-through that provides triggers, permissions, and concurrency. All validation logic, configuration, and surfacing are handled by the reusable workflow.

#### Version tagging

The reusable workflow uses a floating version tag (`v1`) analogous to v0's `v0` tag. The tag is moved forward as the framework evolves within the v1 major version. Breaking changes (new required permissions, changed caller contract) require a new major version tag.

#### Secrets

The caller passes `secrets: inherit`. The reusable workflow uses:
- `GITHUB_TOKEN` — inherited, for checkout and fallback write surfaces
- Org secrets for validation app token minting (`VALIDATION_APP_PRIVATE_KEY`) — accessed via `secrets` context
- Org variables for app identity (`VALIDATION_APP_ID`) — accessed via `vars` context

## 10. Rollout Strategy

### 10.1 v0/v1 Coexistence

The v0 caller (`pr_validation_caller.yml`) and v1 caller (new file) coexist in each repository during the transition period. Both run on every PR and appear in the PR checks list.

#### Why separate callers

- The v0 reusable workflow has a fundamentally different structure (MegaLinter-based, single job, different permissions and output model). A single caller with version switching would require complex conditional logic.
- Separate callers allow independent lifecycle: v0 can be removed per-repo after v1 is proven, without coordinating a simultaneous switch.
- GitHub rulesets can reference the v1 check name independently of v0.

#### Lifecycle per repository

1. **v1 deployed**: v1 caller added alongside v0. Both run on every PR. Codeowners see both check results.
2. **v1 validated**: Codeowners confirm v1 findings are correct and consistent with expectations.
3. **v1 required**: GitHub ruleset makes the v1 check blocking for PR merge.
4. **v0 removed**: v0 caller file deleted from the repository. Any v0-specific ruleset removed.

The transition from stage 1 to stage 4 is per-repository. Repositories move through stages independently based on pilot experience and codeowner readiness.

#### WP-01 relationship

WP-01 (tooling#121) fixes ref consistency in the existing v0 reusable workflow. It validates the OIDC ref resolution pattern that v1 reuses and adds the `tooling_ref_override` break-glass input. WP-01 does not change the v0 caller — callers still call `@v0`. The v1 reusable workflow reuses the same ref resolution pattern with the hardcoded version fallback (section 9.5).

### 10.2 Central Enable/Disable

#### Mechanism: tooling config file

A YAML configuration file in the tooling repository maps each API repository to its validation settings. The reusable workflow reads this file from its own checkout (which it already performs for linting configs and shared actions).

**Rationale for config file over alternatives:**

- **Org variable with repo list** (rejected): JSON arrays in org variables become unwieldy at 60+ repos and hit variable size limits. Not PR-reviewable.
- **Per-repo variable** (rejected): Requires touching each repository to enable. Violates UC-13 — central administration without per-repo configuration changes.
- **Caller version tag** (rejected): Would require editing the caller workflow per-repo, undermining the identical-caller-across-all-repos design (section 9.6).
- **Tooling config file** (chosen): Version-controlled, PR-reviewable, scalable. Adding a repo is one line in a YAML file. Can hold per-repo settings beyond enable/disable (linting config subfolder, rollout stage). Satisfies UC-13 — no per-repo config changes needed.

The config file schema is an implementation detail. At minimum it maps repository name to rollout stage and per-repo settings (e.g., linting config subfolder previously handled by the `configurations` input in v0).

#### Repositories not listed

A repository not listed in the config file is treated as `disabled` — the reusable workflow exits immediately with a notice. This is the safe default for the 60+ repos that have the caller deployed but are not yet onboarded.

### 10.3 Stage Model

The config file controls the validation stage per repository:

| Stage | Config value | Behavior |
|-------|-------------|----------|
| **0: dark** | `disabled` (or not listed) | Caller deployed, reusable workflow exits immediately |
| **1: advisory** | `advisory` | Runs on dispatch only, all findings shown, nothing blocks |
| **2: standard** | `standard` | Runs on PRs and dispatch, standard profile on PRs |
| **3: blocking** | `standard` + GitHub ruleset | Same as stage 2, plus GitHub ruleset requires the v1 check to pass for PR merge |

Stage 3 is the combination of the config file setting (`standard`) and a GitHub ruleset. The config file does not control blocking — rulesets do. This separation keeps the config file focused on validation behavior and rulesets focused on merge policy.

### 10.4 GitHub Rulesets for Blocking

A new ruleset (org-level or per-repo) requires the v1 validation check to pass before PR merge. The pattern follows the existing `release-snapshot-protection` ruleset.

- The ruleset references the v1 workflow by check name (workflow name or job name)
- The `camara-release-automation` app can be a bypass actor for automated release PRs that need to merge without validation
- Ruleset management can reuse the existing admin script pattern (`apply-release-rulesets.sh`)

### 10.5 Rollout Sequence

1. **Test repo**: `ReleaseTest` — full cycle through stages 0-3, validates all surfacing paths
2. **Template**: `Template_API_Repository` — ensures new repos get v1 caller from creation
3. **Pilot API repos**: 2-3 active repos with engaged codeowners
4. **Batch rollout**: Remaining repos, coordinated with v0 removal (section 10.1)

### 10.6 Feature Branch Testing

Admins and rule developers test validation changes on feature branches before merging to main and tagging (UC-15).

The caller workflow in a test repo is temporarily pointed at the feature branch:

```yaml
uses: camaraproject/tooling/.github/workflows/validation.yml@feature-branch
```

Ref resolution (section 9.5) ensures internal checkouts match — admins have write access, so OIDC resolves the exact SHA. `tooling_ref_override` is available as break-glass for composite action changes not on the workflow branch.

Rule developers can dispatch validation on existing release branches in a test repo while calling the feature-branch version of the reusable workflow. This validates rule changes against known-good content before merging (UC-10).

No special framework support is needed — pinned refs are a standard GitHub Actions feature. The framework's only requirement is correct ref resolution (section 9.5).

### 10.7 Caller Update Strategy

The v1 caller workflow is deployed by copying from `Template_API_Repository` to each API repo. Since the caller is identical across all repos (section 9.6), deployment is a mechanical copy — no per-repo customization.

Deployment can be batched using the existing admin tooling pattern (scripted multi-repo operations). The caller can be deployed to all repos at once in stage 0 (dark) — it has no effect until the repo is listed in the config file.

---

## 11. Release Automation Integration

The validation framework integrates with CAMARA release automation at two points in the release lifecycle:

1. **Pre-snapshot gate** (UC-08) — validation runs on the base branch before snapshot creation. Failure blocks the release process.
2. **Release review PR validation** (UC-09) — validation runs on the release review PR with strict profile and content restrictions.

Both touchpoints use the strict profile (section 2.1): errors and warnings block.

### 11.1 Pre-Snapshot Validation Gate

Release automation invokes validation as part of the `/create-snapshot` command, before creating any branches. The validation runs on the current HEAD of the base branch (`main` or maintenance) — this is exactly the content that will become the snapshot.

**Timing and lifecycle position**: The release state is PLANNED when `/create-snapshot` is invoked. If validation fails, no snapshot branch is created and the state remains PLANNED. The codeowner fixes the reported issues and re-invokes `/create-snapshot`.

**Profile**: Strict — both errors and warnings block snapshot creation.

**Rationale for strict**: Once a snapshot is created, mechanical transformations are applied (version replacement, server URLs) and the content becomes immutable. Issues found post-snapshot require discarding and recreating the snapshot. Blocking on warnings at snapshot time avoids this expensive retry cycle.

**Scope**: The validation framework runs all applicable checks — Spectral rules, Python consistency checks, bundling validation, and release-plan semantic checks. This subsumes the existing `validate-release-plan.py` preflight. The framework applies rule applicability conditions (section 5) with the full release context derived from `release-plan.yaml` on the checked-out branch.

**Token**: The `camara-release-automation` app token is passed by the release workflow. This is token priority 1 in the layered resolution (section 9.1). The validation framework does not mint this token; it receives it from the caller.

**Findings output**: Validation findings are reported in the bot's response comment on the Release Issue. The comment includes a structured findings section with error and warning counts, individual findings with fix hints, and a link to the full workflow run for diagnostic artifacts.

| Aspect | Current release-plan preflight | With validation framework |
|--------|-------------------------------|---------------------------|
| **Checks** | release-plan.yaml schema + semantics | Full framework: Spectral, Python, bundling, release-plan |
| **Blocking** | Errors only | Errors and warnings (strict profile) |
| **Findings output** | Bot comment with error list | Bot comment with structured findings + fix hints |
| **Token** | camara-release-automation app | Same (passed to framework) |

### 11.2 Bundling and Snapshot Interaction

This subsection resolves the deferred topic from section 7.7: how bundling and validation interact with release automation's snapshot branch creation.

**The validation framework produces the bundled API specs as part of its validation pipeline (section 7.2, steps 2-3). These bundled specs are the same artifacts that become the release content on the snapshot branch.** Bundling happens exactly once — during validation. Release automation consumes the bundled output rather than re-bundling independently.

On the snapshot branch, source API definition files (which contain `$ref` to `code/common/` and `code/modules/`) are **replaced** with the bundled standalone specs produced by the validation framework. This is the "swap strategy" described in the [bundling design document](https://github.com/camaraproject/ReleaseManagement/pull/436): the familiar filename (`api-name.yaml`) is retained, but the content is the fully resolved, consumer-ready artifact.

#### Handoff model

Two handoff models are viable:

**Model A — Validation creates the snapshot branch**: The validation framework creates the snapshot branch with bundled API specs already in place. Release automation takes over the branch for mechanical transformations (version replacement, server URLs, `release-metadata.yaml` generation) and the rest of the release lifecycle.

**Model B — Artifact handoff**: The validation framework uploads bundled specs as workflow artifacts (section 7.2, step 4). Release automation downloads these artifacts and commits them to the snapshot branch as part of snapshot creation.

Both models avoid duplicate bundling. The choice between them is an implementation detail that depends on workflow architecture constraints. The requirement is: **bundling runs once, during validation, and the output is consumed by release automation for the snapshot.**

#### Mechanical transformations after bundling

Regardless of the handoff model, the mechanical transformer applies version-specific changes on top of the bundled content:

- `info.version` replacement (`wip` → calculated release version)
- Server URL version updates
- `x-camara-commonalities` version field
- Feature file version updates
- Link replacements

These transformations are release automation's responsibility. The validation framework validates the source content (including bundling); the mechanical transformer produces the final release-ready content.

#### Cache sync at snapshot time

A cache synchronization mismatch (section 7.4) is an error in strict profile, blocking snapshot creation. This ensures that `code/common/` content matches the declared `commonalities_release` version before the bundled output is produced and becomes immutable on the snapshot branch.

### 11.3 Release Review PR Validation

A release review PR is created by release automation on the `release-review/rX.Y-<sha>` branch, targeting the `release-snapshot/rX.Y-<sha>` branch. It contains only CHANGELOG and README changes — API specs and other files are immutable on the snapshot branch.

**Detection**: The framework detects a release review PR by its target branch pattern (`release-snapshot/**`). The `is_release_review_pr` context field (section 2.2) is set to `true`, which selects the strict profile.

**Profile**: Strict — same as the pre-snapshot gate. Errors and warnings block the PR.

**Which checks run**: Only a subset of checks is meaningful on a release review PR:

| Check category | Runs on release review PR | Rationale |
|----------------|--------------------------|-----------|
| CHANGELOG format validation | Yes | CHANGELOG is editable on the review branch |
| README content validation | Yes | README is editable on the review branch |
| File restriction check | Yes | Only CHANGELOG and README may be modified |
| Spectral / API definition checks | No | API specs are immutable on the snapshot branch |
| release-plan.yaml checks | No | Already validated at snapshot creation time |
| Bundling validation | No | Source files are immutable |
| Cache sync validation | No | Already validated at snapshot creation time |

**File restriction check**: This is a release-review-specific rule. The framework examines the PR diff and produces an error if any file outside `CHANGELOG.md` (or `CHANGELOG/` directory) and `README.md` is modified. This enforces the separation between immutable snapshot content and reviewable documentation.

**Token**: Standard PR trigger — the validation app token or `GITHUB_TOKEN` fallback. The `camara-release-automation` app token is not used here because this is a regular `pull_request` event, not a release workflow call.

### 11.4 Context Model Notes

The context field `is_release_review_pr` (section 2.2) is documented as "used for profile selection, not rule applicability." The file restriction check (section 11.3) requires `is_release_review_pr` as an applicability condition — the check applies only when this field is `true`.

**Resolution**: `is_release_review_pr` retains its primary role as profile selector. It is also available as an optional applicability condition in rule metadata for checks that are specific to the release review context. This is the only check currently using it as an applicability condition.

```yaml
# File restriction check — release review PR only
id: "060"
name: release-review-file-restriction
engine: python
applicability:
  is_release_review_pr: true
conditional_level:
  default: error
description: "Release review PR may only modify CHANGELOG and README files"
hint: "Only CHANGELOG.md (or CHANGELOG/ directory) and README.md may be modified on the release review branch. API specs and other files are immutable on the snapshot branch."
```

### 11.5 Pre-Snapshot Invocation

The pre-snapshot gate follows the same input design principle as PR and dispatch contexts (section 9.4): the framework derives all release context from `release-plan.yaml` on the checked-out branch. No branch name or release tag inputs are needed.

Release automation invokes the validation framework on the same branch on which `/create-snapshot` was called. The framework reads `release-plan.yaml` from that branch to derive all context fields (target release type, API statuses, Commonalities version, etc.).

The only distinction is the `mode` — the framework needs to know this is a pre-snapshot invocation rather than a dispatch or PR trigger. When `mode` is `pre-snapshot`, the framework:
- Sets `trigger_type` to `release-automation`
- Selects the strict profile
- Produces bundled API specs as output for consumption by release automation (section 11.2)
- Formats findings for inclusion in a Release Issue comment (not a PR comment)

The detailed output model (findings format, artifact structure) will be defined consistently across all execution contexts during document consolidation.

### 11.6 Post-MVP Extensions

The following integration enhancements are post-MVP:

- **API-aware change summaries for release notes**: The framework could use oasdiff (section 8.6) to generate semantic change summaries (breaking changes, new endpoints, modified schemas) for inclusion in release notes or the Release Issue.
- **Snapshot transformer validation**: The framework could validate the transformer's configuration before snapshot creation — verifying that version replacement patterns and server URL formats are correct. This goes beyond API content validation into release tooling self-validation.

---

## 12. Operational Views

### 12.1 Repository Configuration Validation (UC-14)

An admin needs to verify that an API repository is correctly configured for the validation framework. The following aspects must be checkable:

- **Caller workflow**: The v1 caller workflow file exists in `.github/workflows/` and matches the expected template content
- **Central config listing**: The repository is listed in the tooling config file (section 10.2) with a valid stage value
- **GitHub ruleset** (stage 3 only): The v1 validation check is required in the applicable ruleset
- **Validation app installation**: The validation GitHub App (DEC-005) is installed for the repository
- **v0 cleanup** (post-transition): The v0 caller file has been removed after v1 is stable at stage 3

### 12.2 Minimal Change Noise Principle

The design choices throughout this document follow a consistent principle: **minimize the number of changes that require codeowner interaction in API repositories.** The only per-repo change required for onboarding is adding the v1 caller workflow file — a mechanical copy from `Template_API_Repository`. After that, all configuration changes happen centrally in the tooling repository (section 10.2).

### 12.3 Release Manager Dashboard (UC-16, UC-17)

UC-16 and UC-17 are **independent work** — the Release Progress Tracker already exists and is operational. This section defines the integration points between the validation framework and the tracker.

**Compliance indication**: For each repository with validation enabled, the dashboard shows a compliance status derived from the most recent validation run on `main`:

| Status | Meaning |
|--------|---------|
| **compliant** | No errors, no warnings (would pass strict profile) |
| **issues** | Has warnings but no errors (would pass standard, not strict) |
| **failing** | Has errors (would fail standard profile) |
| **unknown** | No validation data available |

**Data collection**: The tracker queries the GitHub API for the most recent completed run of the v1 validation workflow on the default branch (conclusion, URL, timestamp). No changes to the validation framework are needed for this.

**On-demand trigger** (UC-17): The tracker or an admin can dispatch validation on selected repositories via `workflow_dispatch` (section 9.2) to update dashboard status.

### 12.4 Cross-System Integration Map

| System | Integration point | Data flow | Priority |
|--------|------------------|-----------|----------|
| Release automation (`/create-snapshot`) | Pre-snapshot gate (11.1) | Validation → release automation: pass/fail + findings + bundled specs | Post-MVP (high) |
| Release automation (release review PR) | PR trigger with strict profile (11.3) | Standard PR validation flow, profile auto-selected | Post-MVP (high) |
| Release Progress Tracker | Workflow run query (12.3) | Tracker reads validation run data from GitHub API | Independent |
| Release Progress Tracker | Dispatch trigger (12.3) | Tracker dispatches validation via GitHub API | Independent |
| Tooling config file | Central enable/disable (10.2) | Validation reads config at runtime | MVP |
| GitHub rulesets | Blocking enforcement (10.4) | Ruleset references validation check name | Stage 3 |
| Validation GitHub App | Token minting (9.1) | App provides write token for findings surfacing | MVP |
