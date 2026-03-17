# Validation Framework — Detailed Design

**Status**: Work in progress
**Last updated**: 2026-03-17

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

The config file schema is an implementation detail. At minimum it maps repository name to rollout stage and per-repo settings (e.g., linting config subfolder previously handled by the `configurations` input in v0).

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

Two handoff models are viable:

**Model A — Validation creates the snapshot branch**: The validation framework creates the snapshot branch with bundled API specs already in place. Release automation takes over the branch for mechanical transformations (version replacement, server URLs, `release-metadata.yaml` generation) and the rest of the release lifecycle.

**Model B — Artifact handoff**: The validation framework uploads bundled specs as workflow artifacts. Release automation downloads these artifacts and commits them to the snapshot branch as part of snapshot creation.

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

The only distinction is the `mode` — the framework needs to know this is a pre-snapshot invocation rather than a dispatch or PR trigger. When `mode` is `pre-snapshot`, the framework:
- Sets `trigger_type` to `release-automation`
- Selects the strict profile
- Produces bundled API specs as output for consumption by release automation (section 7.1)
- Formats findings for inclusion in a Release Issue comment (not a PR comment)

The detailed output model (findings format, artifact structure) will be defined consistently across all execution contexts during implementation.
