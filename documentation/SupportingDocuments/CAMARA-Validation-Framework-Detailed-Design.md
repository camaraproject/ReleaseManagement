# Validation Framework — Detailed Design

**Status**: Work in progress
**Last updated**: 2026-03-18

> This document supplements the [Validation Framework Requirements](CAMARA-Validation-Framework-Requirements.md) with design and implementation detail for developers and architects. It is expected to migrate to the `tooling` repository alongside the implementation.

---

## 1. Rule Metadata Model

### 1.1 YAML Structure and Examples

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

Conditional level examples:

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

### 1.2 Condition Evaluation

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

### 1.3 Spectral Pass-Through Principle

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

Spectral does not resolve `$ref` references before linting — it validates the document as-is. Checks that depend on the content of referenced schemas (e.g., from CAMARA_common.yaml) require either a pre-bundled input spec or a Python implementation with explicit ref resolution. See section 3.1 (Spectral and `$ref` Interaction) for implications.

For further Spectral-specific details, see [spectral-integration-notes.md](../reviews/spectral-integration-notes.md).

### 1.4 Derived Context Fields

Two per-API context fields are derived from content rather than declared in release-plan.yaml:

**`target_api_maturity`**: Derived from `apis[].target_api_version` — `initial` if major version is 0 (v0.x.y), `stable` if major version >= 1 (vx.y.z). Determines which asset requirements apply per the API Readiness Checklist (e.g., stable public APIs require enhanced test cases and user stories).

**`api_pattern`**: Detected from OpenAPI spec content — `request-response`, `implicit-subscription`, or `explicit-subscription`. Detection logic examines paths (subscription endpoints), callbacks, schema names, and content types. Multiple pattern-specific rule sets (REQ, IMP, EXP, EVT categories) depend on this classification. This detection is a cross-cutting capability used by many rules.

### 1.5 Spectral Migration Potential

Analysis of the deprecated `api_review_validator_v0_6.py` shows that approximately 40% of its checks are implementable as Spectral rules (single-file OpenAPI pattern matching), and an additional 15% could use Spectral custom JavaScript functions. This includes:

- Mandatory error response checks (400, 401, 403)
- Server URL format validation
- info.version format validation
- License and security scheme validation
- ErrorInfo and XCorrelator schema presence
- Error response structure validation

The main blocker for migrating ~20% of checks to Spectral is the dependency on `api_pattern` detection — Spectral cannot natively apply rules conditionally based on detected API type. These checks either need custom JS functions that embed the detection logic, or remain as Python checks that use `api_pattern` from the context.

The Commonalities audit should evaluate each candidate check against the current design guide version before migration.

### 1.6 Authoritative Schema References

The execution context fields and their allowed values are defined by the following schemas, which are the authoritative sources:

- **release-plan.yaml**: `artifacts/metadata-schemas/schemas/release-plan-schema.yaml` (in ReleaseManagement)
- **release-metadata.yaml**: `artifacts/metadata-schemas/schemas/release-metadata-schema.yaml` (in ReleaseManagement)

The framework must accept exactly the values defined in these schemas. Any change to the schemas must be reflected in the framework's context model.

---

## 2. Check Inventory Detail

### 2.1 Inventory Status

The per-rule inventory is **not yet complete**. The following work is required:

1. **Commonalities audit** (dependency): Examine `CAMARA-API-Design-Guide.md` and `CAMARA-API-Event-Subscription-and-Notification-Guide.md` at both r3.4 and r4.1/r4.2 versions to:
   - Identify checks not yet covered by any engine
   - Validate existing Spectral rules against the current design guide
   - Identify rules that changed between Commonalities releases

2. **Existing rule classification**: Map each current Spectral rule to the framework metadata model (applicability, conditional level, hints). The existing Spectral severity levels are assumed valid for now; detailed severity review is deferred.

3. **api-review v0.6 coverage**: The deprecated `api_review_validator_v0_6.py` (~43 checks) was a monolithic implementation used manually by release reviewers for the Fall25 meta-release. Its checks serve as input for identifying Python-needed validations not covered by Spectral.

### 2.2 Known Check Areas by Engine

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

## 3. Bundling Pipeline

### 3.1 Spectral and `$ref` Interaction

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

- **Copy-paste repos**: All schemas inline. Spectral runs directly on source. No bundling needed.
- **`$ref` repos**: Spectral runs on bundled output. All external refs resolved, internal refs preserved. Structurally equivalent to copy-paste.

No rule changes are needed between the two models — bundling normalizes external refs while preserving the internal structure that Spectral rules depend on. Rule IDs remain stable across the transition (flat namespace from Requirements section 5).

#### Bundling is MVP scope

Bundling support for `CAMARA_common.yaml` via `$ref` is **within MVP scope**. Commonalities 0.7.x requires updated common schemas, and the ability to consume them via `$ref` — with the framework handling bundling transparently — is the key additional value of the validation framework v1 for codeowners. This avoids repeating the difficult-to-validate copy-paste pattern.

In the MVP, some parts may still be manual — providing the correct copy in `code/common/` and ensuring it matches the declared `commonalities_release` version. But the `$ref` option is available for early adopters, and the framework handles bundling when `$ref` is detected. Automated cache synchronization and strict version enforcement are post-MVP enhancements.

### 3.2 Dependency Categories and File Mapping

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

### 3.3 Commonalities Version Matrix

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

Framework rule metadata uses a single ruleset with `commonalities_release` range conditions for version-specific behavior. This is appropriate because:

- Python checks are framework-controlled and do not produce confusing intermediate output
- Most framework rules apply across versions; only a minority are version-specific
- Duplicating shared rules into per-version files would create drift risk

The Commonalities audit will identify which rules changed between r3.4 and r4.x. Those rules receive `commonalities_release` range conditions in their metadata.

### 3.4 Placeholder Handling

#### Current state

The current `CAMARA_common.yaml` contains placeholder patterns (e.g., `{{SPECIFIC_CODE}}`) that have no defined resolution rules. These should be removed from Commonalities, with API repositories extending shared schemas via `allOf` instead (per the [bundling design document](https://github.com/camaraproject/ReleaseManagement/pull/436)).

#### Future direction

Placeholder replacement with defined values could be introduced together with bundling as part of a broader transformation pipeline. This could include dynamic variables such as `api_version`, `commonalities_release`, `commonalities_version`, effectively replacing the current "wip" and "/main/" substitutions done by the snapshot transformer. In this model, bundling + transformation (including placeholder replacement) would produce the release-ready artifact.

### 3.5 Rule Architecture Integration

Bundling integrates into the rule architecture (Requirements section 5) without requiring changes to the context model or rule metadata:

- **Step assignment**: Each rule runs in either step 1 (pre-bundling validation) or step 3 (full validation). Assignment is an implementation detail — the framework knows which checks belong to which step.
- **No new context fields**: The context model from Requirements section 2.2 is sufficient. Whether external refs existed and were resolved is an implementation concern, not a rule applicability condition.
- **Cache sync is a check, not context**: The cache synchronization validation (section 3.2) produces findings (warning or error depending on profile). It is not a context field consumed by other rules.
- **Spectral ruleset selection**: The `commonalities_release` field (already in the context model) drives Spectral ruleset pre-selection (section 3.3). No additional metadata is needed.

---

## 4. Artifact Surfacing Detail

### 4.1 Workflow Artifact Naming

- Bundled specs are uploaded as GitHub workflow artifacts with a naming convention that identifies the API name, branch, and commit SHA
- Bundled files include a header comment: `# For information only - DO NOT EDIT`
- Workflow artifact retention uses the GitHub default (90 days)

### 4.2 Temporary Branch Model

Workflow artifacts replace the temporary branch model (`/tmp/bundled/<branch>-<SHA>`) for MVP. Temporary branches may be revisited post-MVP if reviewers need a browsable view of bundled content.

### 4.3 "wip" Version Handling

Bundling on `main` leaves `info.version` as-is — it contains `wip` as expected for unreleased code. Version replacement on release branches is handled by release automation (snapshot transformer), not by the validation framework's bundling step. The framework validates version correctness per branch type — this is an existing check (section 2.2), not a new bundling-specific requirement.

---

## 5. Caller Workflow Design

### 5.1 Token Resolution Strategy

The framework uses a layered token resolution strategy. The order prioritizes consistent branding (all findings come from the same bot identity) over using whichever token happens to be available:

1. **Snapshot context**: `camara-release-automation` app token — provided by the calling release workflow. The validation framework does not mint this token; it is passed in by the release automation caller.
2. **Validation default**: Dedicated validation app bot token — the framework mints an installation token for the current repository. This is the primary path for all PR and dispatch contexts, ensuring consistent bot identity on annotations and comments.
3. **Fallback**: `GITHUB_TOKEN` with write access — used when the validation app is not installed (e.g., dispatch in a fork, or repositories not yet onboarded to the app). Write capability is probed at runtime.
4. **Read-only**: Workflow summary and diagnostic artifacts only — when no write token is available.

In normal operation, both upstream PRs and fork PRs show findings from the validation bot. The `GITHUB_TOKEN` fallback and read-only mode are degraded paths, not the expected default.

### 5.2 Validation GitHub App

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

#### Relationship to v0 surfacing

The v0 workflow surfaces findings via MegaLinter's built-in reporters (`GITHUB_COMMENT_REPORTER`, `GITHUB_STATUS_REPORTER`) and custom `actions/github-script` steps for release-plan validation. The v1 framework replaces all of these with its own unified surfacing layer. MegaLinter is no longer used as the orchestration layer.

### 5.3 Trigger and Concurrency YAML

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

Dispatch runs on whatever branch the user selects in the GitHub UI. The framework derives branch type, release context, and all validation parameters from the checked-out branch content.

#### Concurrency

```yaml
concurrency:
  group: ${{ github.ref }}-${{ github.workflow }}
  cancel-in-progress: true
```

Same model as v0: a new push to a PR branch cancels the previous validation run. Dispatch behaves identically — a second dispatch on the same branch cancels the first.

### 5.4 Permissions Detail

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
| `id-token: write` | OIDC token for tooling ref resolution (section 5.6) | May not be granted for fork PRs — see section 5.6 |

For fork PRs, `GITHUB_TOKEN` write permissions are restricted by GitHub regardless of what the caller declares. The validation app token (section 5.1) bypasses this restriction because it is minted from the app's own credentials, independent of `GITHUB_TOKEN`.

### 5.5 Input Design Detail

The reusable workflow does not accept inputs that duplicate information derivable from the checked-out branch. This prevents contradictions where an input says one thing but branch content says another.

**Example of the problem avoided**: If the workflow accepted a `release_type` input, a user could dispatch on `main` with `release_type: public-release` while `release-plan.yaml` on `main` says `target_release_type: pre-release-alpha`. The framework would need reconciliation logic, and the user would get confusing results.

**Forbidden inputs**: `branch_type`, `release_type`, `api_status`, `commonalities_version`, `configurations` — all derivable from branch content or from the central configuration file (Requirements section 10).

**Consequence for the caller workflow**: No per-repo inputs exist. All per-repo configuration (linting config subfolder, enabled features, rollout stage) lives in the central config file read by the reusable workflow. The caller workflow is identical across all repositories, with no `with:` block needed in standard operation. This makes it protectable via CODEOWNERS or rulesets — nobody ever needs to edit it.

### 5.6 Ref Resolution

#### OIDC-based ref resolution (primary)

The reusable workflow resolves its own tooling repository and commit SHA via OIDC claims (`job_workflow_sha`), following the pattern established in tooling#121. This ensures all internal checkouts (linting config, shared actions at runtime) use the same tooling version that the caller specified.

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

### 5.7 Caller Workflow Template

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

### 5.8 Version Tagging and Secrets

#### Version tagging

The reusable workflow uses a floating version tag (`v1`) analogous to v0's `v0` tag. The tag is moved forward as the framework evolves within the v1 major version. Breaking changes (new required permissions, changed caller contract) require a new major version tag.

#### Secrets

The caller passes `secrets: inherit`. The reusable workflow uses:
- `GITHUB_TOKEN` — inherited, for checkout and fallback write surfaces
- Org secrets for validation app token minting (`VALIDATION_APP_PRIVATE_KEY`) — accessed via `secrets` context
- Org variables for app identity (`VALIDATION_APP_ID`) — accessed via `vars` context

---

## 6. Rollout Implementation

### 6.1 Why Separate Callers

The v0 reusable workflow has a fundamentally different structure (MegaLinter-based, single job, different permissions and output model). A single caller with version switching would require complex conditional logic.

Separate callers allow independent lifecycle: v0 can be removed per-repo after v1 is proven, without coordinating a simultaneous switch. GitHub rulesets can reference the v1 check name independently of v0.

### 6.2 Central Config Alternatives Analysis

**Rationale for config file over alternatives:**

- **Org variable with repo list** (rejected): JSON arrays in org variables become unwieldy at 60+ repos and hit variable size limits. Not PR-reviewable.
- **Per-repo variable** (rejected): Requires touching each repository to enable. Violates UC-13 — central administration without per-repo configuration changes.
- **Caller version tag** (rejected): Would require editing the caller workflow per-repo, undermining the identical-caller-across-all-repos design (section 5.7).
- **Tooling config file** (chosen): Version-controlled, PR-reviewable, scalable. Adding a repo is one line in a YAML file. Can hold per-repo settings beyond enable/disable (linting config subfolder, rollout stage). Satisfies UC-13 — no per-repo config changes needed.

#### Central config file schema

The central config file lives in the tooling repository and maps each API repository to its rollout stage. Spectral ruleset selection is **not** a per-repo config field — it is derived from `commonalities_release` in the repository's own `release-plan.yaml` (section 3.3).

```yaml
# validation-config.yaml in camaraproject/tooling
version: 1
defaults:
  stage: disabled             # default for repositories not listed below
fork_owners: [hdamker, rartych]  # GitHub users allowed to test in their forks
repositories:
  QualityOnDemand:
    stage: standard           # stage 2: runs on PRs, standard profile
  DeviceLocation:
    stage: standard
  ReleaseTest:
    stage: standard
  NetworkSliceBooking:
    stage: advisory           # stage 1: dispatch only
```

| Field | Type | Description |
|-------|------|-------------|
| `version` | integer | Schema version (currently `1`). Allows future schema evolution without breaking existing configs. |
| `defaults.stage` | enum | Default stage for unlisted repositories: `disabled`, `advisory`, `standard`. |
| `fork_owners` | array of strings | GitHub usernames allowed to run validation in their forks. When the workflow runs in a fork owned by a listed user, stage is overridden to `standard` regardless of the repository's upstream stage (section 8.2). |
| `repositories.<name>.stage` | enum | Per-repo rollout stage override. Same values as `defaults.stage`. |

**Stage mapping** (see also Requirements section 10.3):

| Stage | Config value | Behavior |
|-------|-------------|----------|
| 0 (dark) | `disabled` | Caller deployed but reusable workflow exits immediately |
| 1 (advisory) | `advisory` | Runs on dispatch only, advisory profile, nothing blocks |
| 2 (standard) | `standard` | Runs on PRs and dispatch, standard profile on PRs |
| 3 (blocking) | `standard` + ruleset | Same as stage 2; blocking is enforced by a GitHub ruleset, not the config file |

**Extensibility**: Additional per-repo fields (e.g., `features`, optional overrides) can be added without a `version` bump — new fields are additive. Future candidates include `spectral_ruleset_override` and `extra_checks`.

**Self-validation**: The reusable workflow validates the config file against a JSON Schema on every run. An invalid config file is a hard failure with an explicit error message naming the file and the problematic entry. This catches typos, unknown stage values, and schema drift before any validation logic runs.

### 6.3 GitHub Rulesets for Blocking

A new ruleset (org-level or per-repo) requires the v1 validation check to pass before PR merge. The pattern follows the existing `release-snapshot-protection` ruleset.

- The ruleset references the v1 workflow by check name (workflow name or job name)
- The `camara-release-automation` app can be a bypass actor for automated release PRs that need to merge without validation
- Ruleset management can reuse the existing admin script pattern (`apply-release-rulesets.sh`)

### 6.4 Rollout Sequence

1. **Test repo**: `ReleaseTest` — full cycle through stages 0-3, validates all surfacing paths
2. **Template**: `Template_API_Repository` — ensures new repos get v1 caller from creation
3. **Pilot API repos**: 2-3 active repos with engaged codeowners
4. **Batch rollout**: Remaining repos, coordinated with v0 removal

### 6.5 Feature Branch Testing

Admins and rule developers test validation changes on feature branches before merging to main and tagging (UC-15).

The caller workflow in a test repo is temporarily pointed at the feature branch:

```yaml
uses: camaraproject/tooling/.github/workflows/validation.yml@feature-branch
```

Ref resolution (section 5.6) ensures internal checkouts match — admins have write access, so OIDC resolves the exact SHA. `tooling_ref_override` is available as break-glass for composite action changes not on the workflow branch.

Rule developers can dispatch validation on existing release branches in a test repo while calling the feature-branch version of the reusable workflow. This validates rule changes against known-good content before merging (UC-10).

No special framework support is needed — pinned refs are a standard GitHub Actions feature. The framework's only requirement is correct ref resolution (section 5.6).

### 6.6 Caller Update Strategy

The v1 caller workflow is deployed by copying from `Template_API_Repository` to each API repo. Since the caller is identical across all repos (section 5.7), deployment is a mechanical copy — no per-repo customization.

Deployment can be batched using the existing admin tooling pattern (scripted multi-repo operations). The caller can be deployed to all repos at once in stage 0 (dark) — it has no effect until the repo is listed in the config file.

### 6.7 WP-01 Relationship

WP-01 (tooling#121) fixes ref consistency in the existing v0 reusable workflow. It validates the OIDC ref resolution pattern that v1 reuses and adds the `tooling_ref_override` break-glass input. WP-01 does not change the v0 caller — callers still call `@v0`. The v1 reusable workflow reuses the same ref resolution pattern with the hardcoded version fallback (section 5.6).

---

## 7. Release Automation Implementation

### 7.1 Bundling and Snapshot Interaction

The validation framework produces the bundled API specs as part of its validation pipeline (Requirements section 6.2, steps 2-3). These bundled specs are the same artifacts that become the release content on the snapshot branch. Bundling happens exactly once — during validation. Release automation consumes the bundled output rather than re-bundling independently.

On the snapshot branch, source API definition files (which contain `$ref` to `code/common/` and `code/modules/`) are **replaced** with the bundled standalone specs produced by the validation framework. This is the "swap strategy" described in the [bundling design document](https://github.com/camaraproject/ReleaseManagement/pull/436): the familiar filename (`api-name.yaml`) is retained, but the content is the fully resolved, consumer-ready artifact.

#### Handoff model

The validation framework uploads bundled specs as **workflow artifacts** (artifact handoff). Release automation downloads these artifacts and commits them to the snapshot branch as part of snapshot creation. See section 9.7 for the detailed handoff sequence.

This model was chosen over the alternative (validation creates the snapshot branch directly) because:
- The validation reusable workflow's checkout is ephemeral — there is no mechanism to hand uncommitted file changes to a different branch without committing and pushing from within the validation job
- Validation would need `contents: write` permission and knowledge of snapshot branch naming conventions, creating tight coupling to release automation internals
- The artifact model keeps validation stateless: it produces files and reports results, release automation owns repository state

Bundling runs once, during validation. Release automation consumes the bundled output without re-bundling.

#### Mechanical transformations after bundling

After release automation downloads the bundled artifacts, the mechanical transformer applies version-specific changes on top of the bundled content:

- `info.version` replacement (`wip` → calculated release version)
- Server URL version updates
- `x-camara-commonalities` version field
- Feature file version updates
- Link replacements

These transformations are release automation's responsibility. The validation framework validates the source content (including bundling); the mechanical transformer produces the final release-ready content.

#### Cache sync at snapshot time

A cache synchronization mismatch is an error in strict profile, blocking snapshot creation. This ensures that `code/common/` content matches the declared `commonalities_release` version before the bundled output is produced and becomes immutable on the snapshot branch.

### 7.2 Token and Findings Output for Pre-Snapshot

**Token**: The `camara-release-automation` app token is passed by the release workflow. This is token priority 1 in the layered resolution (section 5.1). The validation framework does not mint this token; it receives it from the caller.

**Findings output**: Validation findings are reported in the bot's response comment on the Release Issue. The comment includes a structured findings section with error and warning counts, individual findings with fix hints, and a link to the full workflow run for diagnostic artifacts.

### 7.3 File Restriction Check

The context field `is_release_review_pr` (Requirements section 2.2) serves dual roles: profile selection and applicability condition. The file restriction check is the only check currently using it as an applicability condition.

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

### 7.4 Pre-Snapshot Invocation Detail

Release automation invokes the validation framework on the same branch on which `/create-snapshot` was called. The framework reads `release-plan.yaml` from that branch to derive all context fields (target release type, API statuses, Commonalities version, etc.).

The only distinction is the `mode` input — a reusable workflow input (alongside `tooling_ref_override` and `profile` from Requirements section 9.2) that tells the framework this is a pre-snapshot invocation rather than a dispatch or PR trigger. Release automation passes `mode: pre-snapshot` when calling the validation workflow.

When `mode` is `pre-snapshot`, the framework:
- Sets `trigger_type` to `release-automation`
- Selects the strict profile
- Produces bundled API specs as output for consumption by release automation (section 7.1)
- Formats findings for inclusion in a Release Issue comment (not a PR comment)

The detailed output model (findings format, artifact structure) is defined in section 9.

---

## 8. End-to-End Processing Flow

This section describes the reusable workflow's internal structure and the validation engine's processing pipeline. It covers what happens from the moment the workflow starts to the point where raw findings are collected — output formatting and surfacing are in section 9.

### 8.1 Job Architecture

The reusable workflow uses a **single-job design**. All steps run sequentially within one job.

This differs from release automation's multi-job architecture. Release automation splits into separate jobs because its phases have fundamentally different conditional logic (trigger classification → state derivation → command validation → command execution, where each command is a separate job). The validation workflow has a single linear pipeline — context flows naturally between steps via environment variables and the shared file system within one job. Multi-job would require serializing the context object through job outputs and re-checking out the repository in each job, adding complexity without benefit.

#### Step sequence

| # | Step | Composite action | Skip condition |
|---|------|-----------------|----------------|
| 1 | Checkout repository content | — (inline) | Never |
| 2 | Resolve tooling ref and checkout tooling | `resolve-tooling-ref` | Never |
| 3 | Read central config and check stage | — (inline) | Never (exits here if `disabled`) |
| 4 | Build validation context | `build-validation-context` | Never |
| 5 | Pre-bundling validation | `run-pre-bundling-checks` | `is_release_review_pr` (section 8.6) |
| 6 | Bundling | `run-bundling` | No external `$ref` detected; or `is_release_review_pr` |
| 7 | Full validation | `run-full-validation` | `is_release_review_pr` (runs subset instead — section 8.6) |
| 8 | Post-filter and output | `process-findings` | Never (always produces at least a summary) |

Steps 5–7 are the engine orchestration phase (section 8.4). Step 8 is the output pipeline (section 9).

### 8.2 Checkout Strategy

#### Repository content checkout

```yaml
- uses: actions/checkout@v6
  with:
    fetch-depth: 0
```

Full history (`fetch-depth: 0`) is needed for:
- PR diff analysis: identifying which files changed (used by `release_plan_changed` detection and file restriction check)
- Branch type detection: examining `github.base_ref` for PR triggers

For dispatch triggers, `fetch-depth: 1` would suffice, but a single checkout configuration avoids trigger-specific branching.

#### Tooling checkout

The tooling repository is checked out via sparse checkout at the resolved ref (section 5.6):

```yaml
- uses: actions/checkout@v6
  with:
    repository: camaraproject/tooling
    ref: ${{ steps.resolve-ref.outputs.tooling_sha }}
    sparse-checkout: |
      linting/config
      validation
      shared-actions
    path: .tooling
```

The checkout lands in `.tooling/` within the workspace. This path is used by all subsequent steps to locate linting configs, validation scripts, shared actions, and the central config file.

The sparse checkout scope includes:
- `linting/config/` — Spectral rulesets (per Commonalities version), yamllint config, gherkin-lint config
- `validation/` — Python validation scripts, rule metadata, central config file
- `shared-actions/` — composite actions consumed at runtime

#### Central config gate

Immediately after the tooling checkout, the workflow reads the central config file (section 6.2) and looks up the current repository:

1. Validate the config file against its JSON Schema
2. Extract the repository name from `github.repository` **without the owner prefix** (e.g., `camaraproject/QualityOnDemand` → `QualityOnDemand`)
3. Look up `repositories.<repo-name>.stage` (fall back to `defaults.stage`)
4. **Fork override**: If the workflow is running in a fork (`github.repository_owner` is not `camaraproject` or `GSMA-Open-Gateway`) and the owner is listed in `fork_owners` → override stage to `standard`. If the owner is not listed → keep the resolved stage (typically `disabled` during early rollout, which exits the workflow)
5. If stage is `disabled`: exit the workflow with a notice in the summary ("Validation is not enabled for this repository") and set the overall result to `skipped`
6. If stage is `advisory` and trigger is `pull_request`: exit similarly ("Validation is in advisory mode — use workflow_dispatch to run")
7. Otherwise: continue, passing the resolved stage to subsequent steps

The fork override (step 4) enables trusted testers to run full validation in their forks even before the upstream repository has been onboarded. This is especially useful during early rollout when most repos are still at `disabled`. Once upstream repos move to `standard`, the `fork_owners` list becomes less relevant — forks inherit the upstream stage.

### 8.3 Context Builder

The context builder assembles a unified context object from multiple sources. It follows the same principle as release automation's `BotContext`: all fields are always present in the output, with missing or inapplicable values defaulting to empty strings or `null`. Downstream consumers never need to handle missing keys.

#### Branch type derivation

| Pattern | Branch type | Source |
|---------|-------------|--------|
| `main` | `main` | `github.base_ref` (PR) or `github.ref_name` (dispatch) |
| `release-snapshot/**` | `release` | Same |
| `maintenance/**` | `maintenance` | Same |
| Everything else | `feature` | Same |

For `pull_request` triggers, branch type is derived from the PR's **target branch** (`github.base_ref`), not the source branch. This determines which validation rules apply to the content being merged.

For `workflow_dispatch`, it is derived from the checked-out branch (`github.ref_name`).

#### Trigger type derivation

| Source | Trigger type |
|--------|-------------|
| `github.event_name == 'pull_request'` | `pr` |
| `github.event_name == 'workflow_dispatch'` | `dispatch` |
| `mode` input == `pre-snapshot` | `release-automation` |

The `mode` input (section 7.4) is the only way the trigger type `release-automation` is set. In standard caller workflow operation, `mode` is not set and trigger type comes from the GitHub event.

#### Profile selection

| Trigger type | Branch type | Condition | Profile |
|-------------|-------------|-----------|---------|
| `dispatch` | any | — | `advisory` |
| `pr` | `release` | `is_release_review_pr` = true | `strict` |
| `pr` | any | — | `standard` |
| `release-automation` | any | — | `strict` |

If the `profile` input (Requirements section 9.2) is explicitly set, it overrides the auto-selected profile. This allows dispatch users to preview what a different profile would flag.

#### release-plan.yaml parsing

The context builder reads `release-plan.yaml` from the checked-out branch and validates it against the release-plan JSON Schema (section 1.6). Parsing extracts:

- `target_release_type` — determines release context for all rules
- `dependencies.commonalities_release` — drives Spectral ruleset selection (section 3.3)
- `dependencies.identity_consent_management_release` — version constraint (section 3.2)
- Per-API fields: `api_name`, `target_api_version`, `target_api_status`

If `release-plan.yaml` is absent (valid for repositories not yet using release automation, or feature branches), the context builder produces a minimal context with `target_release_type: null`. Release-plan-specific checks are skipped; Spectral and yamllint still run. If the file is present but invalid, schema violations are reported as findings and processing continues with whatever fields could be parsed.

#### Derived per-API fields

For each API declared in `release-plan.yaml`:

- **`target_api_maturity`**: Derived from `target_api_version` — `initial` if major version is 0, `stable` if >= 1 (section 1.4)
- **`api_pattern`**: Detected from the corresponding OpenAPI spec file content in `code/API_definitions/` (section 1.4). Detection runs during context building because many downstream rules depend on it

#### Spectral ruleset selection

The Commonalities version declared in `release-plan.yaml` (`dependencies.commonalities_release`) determines which Spectral ruleset is used (section 3.3). The framework maps the release tag to a version line:

- `commonalities_release` matching `r3.*` → `.spectral-r3.4.yaml`
- `commonalities_release` matching `r4.*` → `.spectral-r4.yaml`
- Future version lines added as new rulesets are created
- If `commonalities_release` is absent or unresolvable: default to the latest ruleset (currently r4.x)

This selection is derived from the repository's own `release-plan.yaml`, not from the central config. Different branches of the same repo can target different Commonalities versions.

#### Detection of PR-specific context

- **`is_release_review_pr`**: True when the PR targets a `release-snapshot/**` branch (section 7.3)
- **`release_plan_changed`**: True when `release-plan.yaml` is in the PR diff. Detected via the GitHub API's changed files list for the PR. Relevant for the release-plan non-exclusivity check (section 2.2)

#### Fork scenarios

The validation workflow can run in forks as well as upstream:

- **Fork dispatch**: A codeowner dispatches validation on their fork to check work before creating an upstream PR. Org secrets are not available in forks, so the validation app token cannot be minted — token resolution falls back to `GITHUB_TOKEN`, which has full write access within the fork's own context.
- **Fork-internal PRs**: PRs within a fork (feature branch → fork's main) trigger the caller if deployed. Same degraded token situation as fork dispatch.
- **Fork-to-upstream PRs**: The standard contribution path. The workflow runs in the upstream repo context (triggered by `pull_request`), so `github.repository` is the upstream repo. Org secrets are available to the reusable workflow.

The context builder does not expose fork identity as a context field — no validation rule needs it. Fork vs. upstream is a workflow-level concern handled by token resolution (section 5.1).

#### Context object structure

```yaml
# Validation context — all fields always present
repository: "QualityOnDemand"    # repo name without owner prefix
branch_type: "main"              # main | release | maintenance | feature
trigger_type: "pr"               # pr | dispatch | release-automation
profile: "standard"              # advisory | standard | strict
stage: "standard"                # from central config (disabled | advisory | standard)

# Release context (from release-plan.yaml; null if absent)
target_release_type: "pre-release-rc"
commonalities_release: "r4.1"
icm_release: ">= r1.0"

# PR-specific (null for dispatch)
is_release_review_pr: false
release_plan_changed: true
pr_number: 42

# Per-API contexts (array; empty if no release-plan.yaml)
apis:
  - api_name: "qos-booking"
    target_api_version: "1.0.0-rc.1"
    target_api_status: "maintained"
    target_api_maturity: "stable"     # derived
    api_pattern: "request-response"   # detected from spec
    spec_file: "code/API_definitions/qos-booking.yaml"
  - api_name: "qos-on-demand"
    target_api_version: "0.11.0-alpha.1"
    target_api_status: "initial"
    target_api_maturity: "initial"
    api_pattern: "explicit-subscription"
    spec_file: "code/API_definitions/qos-on-demand.yaml"

# Workflow metadata
workflow_run_url: "https://github.com/camaraproject/QualityOnDemand/actions/runs/12345"
tooling_ref: "abc1234def5678..."
```

The context object is serialized as JSON and made available to subsequent steps via an environment variable or step output.

### 8.4 Engine Orchestration

Engines run **sequentially** within the single job. Each step captures its findings and passes them to the post-filter.

Sequential execution is appropriate because:
- GitHub Actions steps within a job are inherently sequential
- Parallel execution would require multi-job with artifact passing — overhead that exceeds the time saved for a 1-3 minute pipeline
- Later steps may depend on earlier results (bundling produces input for Spectral)

#### Step 5: Pre-bundling validation

Runs on **source files** before any ref resolution. These checks must work regardless of whether the repo uses `$ref` or copy-paste:

| Check | Engine | Target files |
|-------|--------|-------------|
| YAML validity | yamllint | `code/API_definitions/*.yaml` |
| `$ref` existence and pattern validation | Python | `code/API_definitions/*.yaml` |
| release-plan.yaml semantic checks | Python | `release-plan.yaml` |
| Cross-file checks not dependent on schema content | Python | Various |

yamllint uses a configuration from the tooling checkout (`linting/config/.yamllint.yaml`). Invalid YAML produces error-level findings that block subsequent steps — there is no point running Spectral on syntactically invalid files.

If all API spec files are syntactically valid and no external `$ref` is detected, step 6 (bundling) is skipped and step 7 runs on the source files directly.

#### Step 6: Bundling

Conditional — only runs when external `$ref` to `code/common/` or `code/modules/` is detected in at least one API spec file.

The framework invokes an **external bundling tool** — it does not implement its own OpenAPI bundler. The tool must satisfy two requirements:

1. **External ref resolution only** (DEC-002): Resolve `$ref` to `code/common/`, `code/modules/`, and other local files. Preserve all internal `$ref` (`#/components/schemas/...`, `#/components/responses/...`). Full dereferencing must not be used.
2. **Source map production**: Produce a mapping from bundled output regions back to source file locations. This is needed for line number translation in the output pipeline (section 9.5). This is a selection criterion for tool evaluation — the chosen tool must either support source maps natively or be wrappable to produce them.

The specific tool choice (e.g., redocly, swagger-cli, prance, custom wrapper) is deferred to implementation, evaluated against these two requirements.

**Cache sync validation** runs as part of bundling: the content of `code/common/` files is compared against the expected content for the declared `commonalities_release` version. A mismatch produces a finding — `warning` in standard profile, `error` in strict profile.

**On bundling failure** (unresolvable `$ref`, missing file, tool error):
- Report bundling error as a finding
- Skip step 7's Spectral run on bundled output (Spectral cannot lint incomplete specs)
- Proceed to step 8 with pre-bundling findings only
- Overall result: `error` (incomplete evaluation)

#### Step 7: Full validation

Runs on the **effective input** — bundled specs (from step 6) if bundling ran, otherwise source specs.

| Check | Engine | Configuration | Output format |
|-------|--------|--------------|---------------|
| Spectral linting | Spectral | Version-selected ruleset (section 3.3) | JSON (`--format json`) |
| Test definition linting | gherkin-lint | `linting/config/.gherkin-lintrc` | Text or JSON |
| Cross-field consistency | Python | Rule metadata (section 1) | Common findings model |
| Version checks | Python | Context + spec content | Common findings model |
| Error response structure | Python | Context + spec content | Common findings model |
| API pattern-specific checks | Python | Context + spec content + `api_pattern` | Common findings model |

**Spectral** is invoked with `--format json` to capture structured output for programmatic post-processing:

```bash
spectral lint \
  --ruleset .tooling/linting/config/.spectral-r4.yaml \
  --format json \
  code/API_definitions/*.yaml \
  > spectral-output.json
```

The JSON output provides per-finding: `code` (rule name), `path` (file), `message`, `severity` (0=error, 1=warn, 2=info, 3=hint), `range.start.line`, `range.start.character`.

**Python checks** produce findings directly in the common findings model (section 8.4.1). They receive the full context object and have access to the file system for cross-file analysis.

**gherkin-lint** validates test definition files in `code/Test_definitions/`. Its findings are normalized into the common model by the framework.

#### 8.4.1 Common Findings Model

All engine outputs are normalized into a common findings format before post-filtering:

```yaml
- rule_id: "042"                   # framework rule ID (sequential, stable)
  engine: spectral                  # spectral | yamllint | gherkin | python
  engine_rule: "camara-parameter-casing-convention"  # native engine rule name
  level: error                      # engine-reported level (before post-filter)
  message: "Path segment 'qualityOnDemand' should be kebab-case"
  path: "code/API_definitions/qos-on-demand.yaml"
  line: 47                          # line in source file (mapped back if bundled)
  column: 5                         # column (if available from engine)
  api_name: "qos-on-demand"         # which API this finding belongs to
  hint: "Use kebab-case: /quality-on-demand/{sessionId}"
```

| Field | Source — Spectral | Source — yamllint | Source — Python |
|-------|------------------|------------------|-----------------|
| `rule_id` | Looked up from rule metadata by `engine_rule`; auto-assigned if no metadata | Looked up similarly | Set directly by check |
| `engine` | `"spectral"` | `"yamllint"` | `"python"` |
| `engine_rule` | `code` field from JSON | Rule name from output | Check function name |
| `level` | Mapped from severity integer: 0→error, 1→warn, 2→hint, 3→hint | Mapped from yamllint severity | Set directly |
| `message` | `message` field | Error message text | Set directly |
| `path` | `source` field | File path from output | Set directly |
| `line` | `range.start.line` (0-indexed → 1-indexed) | Line number from output | Set directly |
| `column` | `range.start.character` | Column from output | Set directly (or null) |
| `api_name` | Derived from file path | Derived from file path | Set directly |
| `hint` | From rule metadata `hint` field (if present); otherwise engine `message` serves as hint | From rule metadata | Set directly |

Spectral rules **without** explicit framework metadata entries pass through with identity mapping (section 1.3): `rule_id` is auto-assigned, `hint` defaults to the engine's `message`, and the level maps directly. This means the check inventory does not need to be complete before the framework can run — new Spectral rules work immediately.

### 8.5 Composite Action Boundaries

Composite actions encapsulate logic that is independently testable, reusable across contexts, or benefits from encapsulation (e.g., Python scripts with dependencies). Simple shell commands and conditional logic remain as inline workflow steps.

| Action | Purpose | Key inputs | Key outputs |
|--------|---------|-----------|-------------|
| `resolve-tooling-ref` | OIDC-based ref resolution (section 5.6) | `tooling_ref_override` | `tooling_sha` |
| `build-validation-context` | Context assembly (section 8.3) | Repository checkout path, tooling path, central config | Context JSON, stage, profile |
| `run-pre-bundling-checks` | Pre-bundling validation (section 8.4 step 5) | Context JSON, source files | Findings JSON |
| `run-bundling` | External ref resolution + cache sync (section 8.4 step 6) | Context JSON, source files, cache dir | Bundled specs, source map, findings JSON |
| `run-full-validation` | Spectral + gherkin + Python checks (section 8.4 step 7) | Context JSON, effective input files, ruleset path | Findings JSON |
| `process-findings` | Post-filter + output formatting (section 9) | Context JSON, all findings JSONs, token | Summary, annotations, comment, status |

The `validate-release-plan` action from release automation is reused (enhanced to produce findings in the common model) rather than reimplemented. Other release automation shared actions (`resolve-tooling-ref`) are consumed directly.

The boundary between "one large action" and "several small actions" per engine is an implementation choice. The table above shows the logical boundaries; implementation may merge or split actions based on testability and maintenance considerations.

### 8.6 Release Review PR Short Circuit

When `is_release_review_pr` is true, the processing flow is shortened:

- **Skip**: Steps 5 (pre-bundling), 6 (bundling), and the Spectral/gherkin/most-Python portions of step 7
- **Run**: CHANGELOG format check, README validation, file restriction check (section 7.3)
- **Rationale**: API specs are immutable on the snapshot branch — Spectral checks would be redundant. Release-plan and cache sync were already validated at snapshot creation time (Requirements section 11.2)

This is implemented as a conditional skip within the engine orchestration steps, not a separate workflow path. The context builder sets `is_release_review_pr` and subsequent steps check it before executing.

---

## 9. Output Pipeline

This section covers step 8 of the processing flow (section 8.1): post-filter processing, output formatting, truncation, line number mapping, and error handling. It takes the raw findings from all engines and produces the user-visible output.

### 9.1 Post-Filter Processing

The post-filter evaluates each raw finding against the rule metadata (section 1) and the current validation context (section 8.3). It produces a filtered, severity-adjusted findings list ready for output formatting.

**Processing steps per finding:**

1. **Rule metadata lookup**: Match the finding to its framework rule metadata entry by `engine` + `engine_rule`. Python-produced findings already carry a `rule_id` and skip this step.

2. **Applicability evaluation**: Apply the rule's `applicability` conditions against the current context (section 1.2). If any condition does not match, the finding is silently removed — it does not apply in this context.

3. **Conditional level resolution**: Apply `conditional_level` overrides against the context (section 1.2). The first matching override determines the resolved level; if none match, the default level is used. The resolved level replaces the engine-reported level. If the resolved level is `off`, the finding is removed.

4. **Pass-through**: Spectral rules without explicit framework metadata entries pass through with identity mapping (section 1.3). Their engine-reported severity becomes the resolved level, and the engine's `message` serves as the hint. This is the common case for most Spectral rules — the framework runs without requiring a complete metadata inventory.

**Per-API evaluation**: Findings associated with a specific API (identified by `api_name`) are evaluated against that API's context fields (`target_api_status`, `target_api_maturity`, `api_pattern`). Repository-level findings (e.g., release-plan.yaml checks) are evaluated against the repository-level context.

### 9.2 Profile Application and Blocking Decision

After post-filtering, each finding has a resolved level. The active profile (section 8.3) determines which levels block:

| Profile | Blocking levels | Typical context |
|---------|----------------|-----------------|
| `advisory` | None — nothing blocks | Dispatch (stage 1) |
| `standard` | `error` | PR validation (stage 2) |
| `strict` | `error` and `warn` | Pre-snapshot, release review PR |

**Overall result** — one of three values:

| Result | Meaning |
|--------|---------|
| `pass` | No blocking findings |
| `fail` | At least one finding at a blocking level |
| `error` | An engine failure prevented complete evaluation (section 9.6) — even if no blocking findings were collected, the result is uncertain |

**Finding grouping for output**: Findings are grouped for display in the following order: by resolved level (error → warn → hint), then by API name, then by file path, then by line number. This ensures the most actionable items appear first.

### 9.3 Output Formatting

The framework produces output on multiple surfaces, each with different capabilities and token requirements. All surfaces are generated from the same filtered findings list.

#### Workflow summary (always available)

The workflow summary is the primary detailed surface. It requires no write token — it is written via `$GITHUB_STEP_SUMMARY` and is always available, even for fork PRs with read-only tokens.

Structure:

```markdown
## CAMARA Validation — {result}

**Profile**: {profile} | **Branch**: {branch_type} | **Trigger**: {trigger_type}

### Summary

| API | Errors | Warnings | Hints |
|-----|--------|----------|-------|
| qos-booking | 0 | 2 | 1 |
| qos-on-demand | 1 | 0 | 3 |

### Findings

#### Errors

| Rule | File | Line | Message | Hint |
|------|------|------|---------|------|
| 042 | qos-on-demand.yaml | 47 | Path segment should be kebab-case | Use: /quality-on-demand |

#### Warnings
...

#### Hints
...

### Engine Status

| Engine | Status | Findings |
|--------|--------|----------|
| Spectral | Completed | 4 |
| yamllint | Completed | 0 |
| Python | Completed | 3 |

---
Commit: abc1234 | Tooling: def5678 | [Full workflow run]({workflow_run_url})
```

#### Check run annotations (write token required)

One annotation per finding, mapped to the source file and line number:

- Annotation level: `failure` for error, `warning` for warn, `notice` for hint
- Annotation message: includes the rule ID, engine rule name, and fix hint
- Annotation title: rule name from metadata (or engine rule name if no metadata)

GitHub limits annotations to **50 per step**. If more findings exist:
- Prioritize: errors first, then warnings, then hints
- Note the truncation in the workflow summary: "Showing 50 of N findings as annotations. See workflow summary for the complete list."

#### PR comment (write token required)

A concise summary comment on the PR — not a full findings list. Links to the workflow summary for details.

```markdown
### CAMARA Validation — {result}

{errors} errors, {warnings} warnings, {hints} hints | Profile: {profile}

[View full results]({workflow_run_url})
```

The comment uses a create-or-update pattern with a marker (`<!-- camara-validation -->`) to avoid duplicate comments on subsequent pushes. Each new push updates the existing comment rather than creating a new one.

**Pre-snapshot context**: When invoked by release automation (`mode: pre-snapshot`), findings are formatted for inclusion in the bot's Release Issue comment (section 7.2) rather than as a standalone PR comment. The framework returns the formatted findings section to the calling workflow.

#### Commit status (write token required)

Commit statuses provide at-a-glance results in the PR's checks list:

- **Overall status**: Context `CAMARA Validation`, state = `success` / `failure` / `error`
- **Per-engine statuses** (optional, for diagnostics): `CAMARA Validation / Spectral`, `CAMARA Validation / yamllint`, etc. — each shows the engine's individual pass/fail state

The overall status is the one referenced by GitHub rulesets for blocking (stage 3).

### 9.4 Truncation Strategy

GitHub limits workflow step summaries to **1 MB per step** and **1 MB total per job**. The framework must stay within this limit.

**Approach**: Estimate the rendered size during summary generation. If the cumulative size approaches 900 KB:

1. Show all **errors** first — never truncated
2. Show **warnings** up to the remaining budget
3. If budget exhausted before all warnings are shown: display a count of remaining findings and link to the full report
4. **Hints** are shown only if budget permits after errors and warnings

```markdown
> Showing 85 of 214 findings. Full Spectral output available in
> [workflow artifacts]({artifact_url}).
```

The full Spectral JSON output and the complete findings list (all engines) are always uploaded as **workflow artifacts** regardless of summary truncation. These artifacts are the authoritative complete record.

### 9.5 Line Number Mapping

When Spectral runs on bundled output (section 8.4, step 7), finding line numbers reference the bundled file, not the original source file. Annotations and summary tables must show source file locations to be actionable for developers.

**Requirement on the bundling tool**: The external bundling tool (section 8.4, step 6) must produce — or be augmented to produce — a source map that records which regions of the bundled file originated from which source file and line range. This is a selection criterion for bundling tool evaluation, alongside external-ref-only resolution (DEC-002).

**Design choice**: Content pulled in from external refs (e.g., schemas from `CAMARA_common.yaml`) maps back to the **`$ref` line in the source file**, not to the external file itself. The `$ref` declaration is the actionable location — it is the line the developer controls. If Spectral reports an issue at line 247 of the bundled file, and that region was pulled from an external ref declared at line 15 of the source file, the finding is reported at source line 15.

**Scope**: Line number mapping is only needed for repositories that use `$ref` to `code/common/` or `code/modules/`. Copy-paste repositories have identity mapping — source and effective input are the same file.

The source map format is an implementation detail. A line-offset table per external ref insertion point is sufficient for MVP.

### 9.6 Error Handling

**Design principle**: Always surface what succeeded; never silently skip. If an engine fails, the failure is reported explicitly and remaining engines continue.

#### Engine failure

When an engine crashes (Spectral error, Python exception, missing dependency):

1. Catch the failure in the step (non-zero exit code or exception)
2. Record an engine-level error finding:
   ```yaml
   - rule_id: "engine-failure"
     engine: spectral           # the engine that failed
     engine_rule: null
     level: error
     message: "Spectral exited with code 2: Cannot read ruleset file"
     path: null
     line: null
     api_name: null
     hint: "Check the workflow log for details"
   ```
3. Continue with remaining engines
4. Set overall result to `error` (distinct from `fail` — signals incomplete evaluation)
5. Workflow summary explicitly lists which engines succeeded and which failed (engine status table in section 9.3)

Following the release automation pattern: error messages are shown in code blocks, immediately visible, not collapsed. The workflow run URL links to full logs.

#### Config file missing or invalid

- Config file **missing** from the tooling checkout: hard failure with an explicit error in the summary. This is a tooling repository issue, not a per-repo issue.
- Config file **invalid** (bad YAML, unknown stage value, schema violation): hard failure naming the config file and the problematic entry. The framework does not proceed with potentially incorrect configuration.

#### release-plan.yaml missing or invalid

- **Missing**: The context builder produces a minimal context with `target_release_type: null`. Release-plan-specific checks (version consistency, non-exclusivity, dependency validation) are skipped. Spectral and yamllint still run on source files. This is not an error — repos without release-plan.yaml (or feature branches that haven't added one) are valid.
- **Invalid** (present but fails schema validation): Schema violations are reported as findings. The context builder extracts whatever fields it can and continues with a partial context. Remaining checks run with the available context.

#### Bundling failure

When bundling fails (unresolvable `$ref`, missing file in `code/common/`, tool crash):

1. Report the bundling error as a finding (error level)
2. Skip Spectral on bundled output (step 7 Spectral) — cannot lint incomplete specs
3. Proceed to post-filter with pre-bundling findings (step 5 results) and the bundling error
4. Set overall result to `error` if the active profile would have required checks on bundled output

Pre-bundling findings are still valuable — yamllint and ref pattern checks provide feedback even when bundling fails.

#### Token minting failure

When the validation app token cannot be minted (app not installed, secret missing, API error):

1. Follow the layered token resolution (section 5.1) — fall back to `GITHUB_TOKEN`, then to read-only
2. Log the degraded state in the workflow summary header: "Write surfaces unavailable — showing findings in workflow summary only"
3. **Never** fail the workflow because of a token issue — validation results are always produced, only the surfacing degrades
4. Check run annotations, PR comments, and commit statuses are silently skipped when no write token is available

#### Failure mode summary

| Failure | Behavior | Overall result |
|---------|----------|---------------|
| Engine crash | Record engine-failure finding, continue with remaining engines | `error` |
| Config file missing/invalid | Hard failure, explicit error in summary | `error` (workflow exits) |
| release-plan.yaml missing | Minimal context, skip release-plan checks, run Spectral/yamllint | Normal (`pass`/`fail`) |
| release-plan.yaml invalid | Report violations as findings, partial context, continue | Normal (`pass`/`fail`) |
| Bundling failure | Report error, skip bundled-output checks, show pre-bundling findings | `error` |
| Token minting failure | Degrade surfacing, never fail the workflow | Normal (`pass`/`fail`) |

### 9.7 Bundled Spec Artifacts

Bundled API specs produced in step 6 (section 8.4) are a distinct output category from findings — they are build artifacts, not validation results. This section covers how they are persisted and consumed.

#### Artifact upload

After bundling completes (step 6), the bundled spec files are uploaded as **GitHub workflow artifacts**, regardless of whether validation passes or fails. Bundled specs are useful for review even when findings exist.

Artifact naming follows a convention that identifies the content:

```
validation-bundled-specs-{commit-sha-short}
```

The artifact contains one bundled YAML file per API (retaining the original filename, e.g., `qos-booking.yaml`) plus the source map file produced by the bundling tool (section 9.5).

Artifacts use the GitHub default retention period (90 days). They are available for download from the workflow run's artifact list.

#### User surfacing

The workflow summary (section 9.3) includes a link to the bundled spec artifacts when bundling ran:

```markdown
### Bundled Specs

Bundled standalone API specs are available as [workflow artifacts]({artifact_url}).
```

This gives PR reviewers visibility into the bundled output — they can download and inspect the fully resolved specs to verify that `$ref` resolution produced the expected result. For copy-paste repositories (no bundling), this section is omitted.

#### Release automation handoff (Model B)

When release automation invokes validation with `mode: pre-snapshot`, it consumes the bundled spec artifacts to populate the snapshot branch. The handoff uses the **artifact model** (section 7.1, Model B):

1. Release automation calls the validation reusable workflow with `mode: pre-snapshot`
2. Validation runs the full pipeline (context → pre-bundling → bundling → full validation → output)
3. Validation uploads bundled specs as workflow artifacts
4. Validation returns its overall result (`pass` / `fail` / `error`) to the caller
5. If result is `pass`: release automation downloads the bundled spec artifacts and commits them to the snapshot branch, replacing the source files that contained `$ref`
6. If result is `fail` or `error`: release automation does not create the snapshot — findings are reported in the Release Issue comment

The validation framework does not need `contents: write` permission and has no knowledge of snapshot branch naming. It produces files and reports results; release automation decides what to do with them. This keeps a clean separation: validation is stateless, release automation owns the repository state.

**For non-pre-snapshot runs** (PR and dispatch triggers): bundled specs are uploaded as artifacts for reviewer inspection only. No branch creation or file replacement occurs — the artifacts are informational.
