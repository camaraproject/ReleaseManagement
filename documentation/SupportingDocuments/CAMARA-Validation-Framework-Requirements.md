# Validation Framework — Requirements

**Status**: Work in progress
**Last updated**: 2026-03-17

> For design and implementation detail, see [Validation Framework — Detailed Design](CAMARA-Validation-Framework-Detailed-Design.md).

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

Three profiles control blocking behavior:

| Profile | Blocking behavior | Typical use |
|---------|-------------------|-------------|
| **advisory** | Nothing blocks; all findings shown | Dispatch, local run (hardcoded) |
| **standard** | `error` blocks; `warn` and `hint` shown | Default for PRs and release gates |
| **strict** | `error` and `warn` block; `hint` shown | Configurable for release gates during stabilization |

Profile selection is **config-driven** for PR and release contexts. The central config file (section 10.2) provides two per-repo profile fields:

- `pr_profile` — used for PR-triggered validation (default: `standard`)
- `release_profile` — used for pre-snapshot validation and release review PRs (default: `standard`)

Dispatch and local triggers always use `advisory` regardless of config. An explicit `profile` input on the workflow overrides config-driven selection.

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
| **muted** | Suppressed, finding not shown | *(n/a)* |

#### Applicability conditions

A rule is skipped silently if its conditions don't match the current context. Multiple fields are combined with AND; multiple values within an array field are combined with OR.

| Field | Type | Values | Source |
|-------|------|--------|--------|
| `branch_types` | array | `main`, `release`, `maintenance`, `feature` | Target branch (PR) or checked branch (dispatch) |
| `trigger_types` | array | `pr`, `dispatch`, `release-automation`, `local` | How validation was invoked |
| `target_release_type` | array | `none`, `pre-release-alpha`, `pre-release-rc`, `public-release`, `maintenance-release` | `repository.target_release_type` in release-plan.yaml |
| `target_api_status` | array | `draft`, `alpha`, `rc`, `public` | `apis[].target_api_status` in release-plan.yaml (per-API) |
| `target_api_maturity` | array | `initial` (0.x.y), `stable` (x.y.z, x>=1) | Derived from `apis[].target_api_version` |
| `api_pattern` | array | `request-response`, `implicit-subscription`, `explicit-subscription` | Detected from OpenAPI spec content (per-API) |
| `commonalities_release` | string | Range expression, e.g. `">=r3.4"` | `dependencies.commonalities_release` in release-plan.yaml |
| `release_plan_changed` | boolean | `true`, `false` | Whether release-plan.yaml is in the PR diff (PR trigger only) |

Range comparison for `commonalities_release` uses `packaging.specifiers` (Python) with release tags normalized to comparable values.

#### Conditional level

`default` is always present. `overrides` is a list of `{condition, level}` pairs evaluated in order; first match wins. Conditions use the same field/value model as applicability (AND across fields, OR within arrays). The level `muted` can be used in overrides to suppress a finding in specific contexts.

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
| `is_release_review_pr` | boolean | Detected by framework (profile selection + applicability condition for release-review-specific checks) |

### 2.3 Execution Contexts

The validation framework must support these execution contexts:

| Context | Trigger | Profile | Token | Notes |
|---------|---------|---------|-------|-------|
| **PR (fork-to-upstream)** | `pull_request` event | `pr_profile` from config (default: standard) | read-only | Default GitHub behavior: fork PRs get read-only GITHUB_TOKEN regardless of author's repo permissions. Limits output options (no check run annotations, no PR comments via token) |
| **PR (upstream branch)** | `pull_request` event | `pr_profile` from config (default: standard) | write | PR from upstream branch. Note: codeowners should normally use forks too |
| **Dispatch (upstream repo)** | `workflow_dispatch` | advisory (hardcoded) | write | Main (default), maintenance, release branches. Warning on non-standard branches |
| **Dispatch (fork repo)** | `workflow_dispatch` | advisory (hardcoded) | write (fork scope) | Fork owner triggers on own fork. Inherited — no extra work if dispatch trigger exists |
| **Local** | CLI / script | advisory (hardcoded) | n/a | No GitHub context; subset of rules |
| **Release automation: snapshot** | Called by release workflow | `release_profile` from config (default: standard) | write (app token) | Gate before snapshot creation (section 11.1) |
| **Release automation: review PR** | `pull_request` event (push to PR branch) | `release_profile` from config (default: standard) | write or read-only | Same trigger as normal PR; profile based on release review PR detection (section 11.2) |

**Profile is independent of token permissions.** A fork-to-upstream PR gets the same profile as an upstream-branch PR. The read-only token only limits *how results are surfaced* (e.g. no check run annotations via GITHUB_TOKEN), not validation strictness.

**Dispatch is always advisory.** Dispatch runs have nothing to block (except the workflow itself). They surface errors, warnings, and hints for the user to review.

**Who can dispatch**: Standard GitHub permission model — write access required. On upstream: codeowners and org-wide teams (admin, release_reviewer). On forks: fork owner.

---

## 3. MVP Scope

The MVP replaces `pr_validation` v0 and delivers the minimum useful validation on PRs and dispatch.

### MVP includes

- UC-01, UC-02, UC-04 through UC-07 (contributor and codeowner use cases)
- UC-13 (incremental rollout with central config)
- UC-15 (feature branch testing with pinned refs)
- Profiles: advisory and standard
- Execution contexts: PR (fork-to-upstream), PR (upstream branch), dispatch (upstream repo), dispatch (fork repo), local (design guardrails only — see Detailed Design Appendix B)
- Existing Spectral rules and YAML linting
- Understandable output with fix hints
- Caller workflow with all triggers from day one (PR, dispatch), deployed alongside `pr_validation` v0
- Central enable/disable per repository (no per-repo config files)

### Post-MVP priorities

- UC-08, UC-09 (release automation strict gates, section 11) — high priority, requires strict profile; depends on PR integration being operational first
- UC-03 (local validation) — framework design supports it (Detailed Design Appendix B), entry point and tooling are post-MVP
- UC-10 (regression testing against release branches) — rule developer tooling
- UC-14 (repository configuration validation) — admin tooling
- Automated cache synchronization for `code/common/` and strict version enforcement — bundling itself (ref resolution via `$ref`) is MVP scope (section 6)
- Python-based consistency checks beyond what Spectral covers — may partially land in MVP

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
- `API-Testing-Guidelines.md` — test file structure, naming, and content requirements
- `artifacts/CAMARA_common.yaml` — canonical common schemas (bundling reference)

Further Commonalities artifacts (API template, subscription template) can be added after the Commonalities restructuring ([Commonalities#603](https://github.com/camaraproject/Commonalities/issues/603)) has landed and files are stable.

**Release Management:**
- `release-plan-schema.yaml` — field definitions and allowed values for release-plan.yaml
- `release-metadata-schema.yaml` — field definitions for generated release-metadata.yaml on release branches
- `api-readiness-checklist.md` — release asset requirements matrix by API status and maturity

The `release-plan-schema.yaml` and `release-metadata-schema.yaml` are the authoritative source for execution context field values. The framework must accept exactly the values defined in these schemas.

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

---

## 5. Rule Architecture

### 5.1 Processing Model

The framework uses a **post-filter and severity mapping** architecture:

1. Framework determines the execution context (branch type, trigger, release-plan.yaml content)
2. Engines run (Spectral, yamllint, gherkin-lint, Python checks) and produce findings
3. Framework collects all findings
4. For each finding: look up rule metadata → is it applicable in this context? → what level? → apply profile (advisory/standard/strict) to determine blocking
5. Produce unified output with hints

### 5.2 Key Design Decisions

- **Flat ID namespace**: Sequential IDs (e.g., `042`) that are stable across engine changes. A rule migrating from Python to Spectral keeps its ID.
- **Engine as metadata**: The `engine` field records which engine implements the check. The `engine_rule` field maps to the native rule ID (e.g., Spectral rule name) for configuration synchronization.
- **Condition language**: Plain YAML with AND across fields, OR within arrays. Range comparison on `commonalities_release`. No custom DSL or policy engine.
- **Per-API evaluation**: API-specific rules are evaluated once per API in the repository, using the API's own `target_api_status`, `target_api_maturity`, and `api_pattern` from release-plan.yaml and OpenAPI spec content.

---

## 6. Bundling & Refs

The overall bundling model — controlled local copy on `main`, source-only `main`, bundled release artifacts — is defined in the [Commonalities Consumption and Bundling Design](https://github.com/camaraproject/ReleaseManagement/pull/436) document. This section captures what the validation framework checks about that model, not the model itself.

### 6.1 Repository Model Validation

The framework validates the repository layout and `$ref` patterns used in API source files:

- **Layout**: When API source files contain `$ref` to `../common/` or `../modules/`, the framework validates that referenced files exist, that `code/common/` contains only cache copies from external repositories, and that `code/modules/` contains project-local reusable schemas.
- **Ref patterns**: API source files must use only relative `$ref` for normative schema consumption. Remote URL-based `$ref` used for normative schema content is an error. Internal component references (`#/components/...`) are always valid.
- **Transition**: Repositories not yet using `code/common/` (current copy-paste model) remain valid. Layout and ref pattern checks only fire when `$ref` to `../common/` or `../modules/` is detected. The framework does not force migration.

### 6.2 Validation Pipeline

The framework applies a uniform validation flow regardless of context:

1. **Engine validation** (always runs on source files): All engines run sequentially on source files — yamllint (YAML validity), Spectral (OpenAPI linting with version-selected ruleset), Python checks (cross-field consistency, version alignment, release-plan semantics), gherkin-lint (test definition linting). Spectral CLI natively follows external `$ref` during linting and reports findings with correct source file and line numbers.
2. **Post-filter and output**: Findings are filtered by applicability and conditional level, profile blocking is applied, and results are surfaced via workflow summary, Check Run annotations, PR comments, and commit status.
3. **Bundling** (post-validation, if `$ref` to `code/common/` or `code/modules/` is detected): Produce standalone bundled specs per API as diagnostic artifacts for reviewer inspection. Internal `$ref` (`#/components/...`) are preserved. The framework uses bundling (external ref resolution only), not full dereferencing.

The validation **profile** (advisory, standard, strict) controls which findings block; it does not change which engines run.

**Bundling is output, not prerequisite**: Spectral natively follows `$ref` to `code/common/` and other local files, so bundling is not required before linting. Bundled specs are produced as review artifacts and uploaded as workflow artifacts (section 7).

**Repositories without `$ref`**: Repositories using the copy-paste model skip the bundling step. Source files are standalone by construction. No bundling overhead is introduced.

**Bundling for release artifacts**: Release automation bundles independently during snapshot creation to produce the standalone release-ready specs. The validation framework's bundled artifacts are for reviewer inspection only and are not consumed by release automation.

### 6.3 Cache Synchronization

When `code/common/` exists, the framework validates that cached files match the declared dependency versions in `release-plan.yaml`. Mismatch severity depends on the profile:

- **standard** (PR): warning — codeowner is informed, merge is not blocked
- **strict** (release automation): error — snapshot creation is blocked

If no `code/common/` directory exists, the sync check is skipped. In the MVP, cache management may be manual; the validation check still applies regardless of how the cache was populated.

### 6.4 Placeholder Handling

- The framework detects unreplaced placeholder patterns (`{{...}}`) in bundled output and reports them as errors — this is a permanent safety net
- Placeholder replacement is not a framework responsibility. If placeholder replacement becomes part of a bundling/transformation pipeline, it is a post-MVP enhancement
- Detection of undefined/unresolvable placeholders remains an error regardless of whether replacement is implemented

---

## 7. Artifact Surfacing

The framework produces bundled artifacts for reviewer visibility. The [bundling design document](https://github.com/camaraproject/ReleaseManagement/pull/436) defines a priority order:

1. **Source diff** — primary review surface, no framework action needed (standard git diff)
2. **Bundled artifact** — the framework uploads the bundled standalone API spec as a GitHub workflow artifact for each API with external `$ref`
3. **Bundled diff** — a diff between the bundled API from the PR base and the bundled API from the PR head, uploaded as a workflow artifact or included in the workflow summary (post-MVP)
4. **API-aware summary** — optional semantic change summary (post-MVP)

Bundled artifacts are diagnostic and review aids — they allow PR reviewers to inspect the fully resolved specs. They are not consumed by release automation (which bundles independently during snapshot creation).

Since all engines run on source files (section 6.2), findings already reference source file locations directly. No line number mapping from bundled to source is needed.

**API-aware change summaries**: The framework should support pluggable diff tools for generating semantic change summaries (breaking changes, new endpoints, modified schemas). This capability is post-MVP.

---

## 8. Findings Surfacing

### 8.1 Output Surfaces

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
| **Bundled spec artifacts** | Standalone bundled API specs (see section 7) |

Diagnostic artifacts are always uploaded as GitHub workflow artifacts regardless of token permissions.

### 8.2 Summary Size Limit

GitHub limits workflow step summaries to 1 MB per step and 1 MB total per job. The framework must:

- Truncate the summary when approaching the limit, showing a count ("50 of 127 findings shown") with a link to the full diagnostic artifact
- Prioritize errors over warnings over hints in the truncated view
- Always include the full findings in the Spectral JSON log artifact (no size limitation on workflow artifacts)

### 8.3 Surfaces by Resolved Capability

| Token capability | Findings output | Diagnostic artifacts |
|-----------------|-----------------|---------------------|
| **Write** (validation app, camara-release-automation, or GITHUB_TOKEN) | Workflow summary + check run annotations + PR comment + commit status | Workflow artifacts (always) |
| **Read-only** (all write paths failed) | Workflow summary only | Workflow artifacts (always) |

A dedicated validation GitHub App provides write token capability even for fork PRs where `GITHUB_TOKEN` is read-only. This app is separate from `camara-release-automation` and is introduced from day one (MVP).

---

## 9. Workflow Contract

### 9.1 Input Design Principle

The reusable workflow does not accept inputs that duplicate information derivable from the checked-out branch. The framework reads branch type from the branch name, and all release context from `release-plan.yaml` on the checked-out branch. These values are derived at runtime, never accepted as inputs.

No per-repo inputs exist. All per-repo configuration lives in the central config file (section 10.2) read by the reusable workflow. The caller workflow is identical across all repositories.

### 9.2 Reusable Workflow Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `tooling_ref_override` | string | no | *(empty)* | 40-character SHA for non-standard tooling ref. Supports testing in contexts where OIDC may not work. Documented as pilot/break-glass only. |
| `profile` | choice | no | *(auto)* | Validation profile: `advisory`, `standard`, `strict`. Default: framework selects based on context. Dispatch users can set explicitly to see what a different profile would flag. |
| `mode` | string | no | *(empty)* | Execution mode. Set to `pre-snapshot` by release automation to invoke validation as a pre-snapshot gate. Affects trigger type derivation, profile selection, bundled spec handoff, and findings output target. |

### 9.3 Trigger Summary

| Trigger | Target branches | Default profile |
|---------|----------------|-----------------|
| `pull_request` | `main`, `release-snapshot/**`, `maintenance/**` | standard (strict for release review PRs) |
| `workflow_dispatch` | Any branch | advisory |
| Release automation call | Base branch (`main` or maintenance) | strict |

---

## 10. Rollout Strategy

### 10.1 v0/v1 Coexistence

The v0 caller (`pr_validation_caller.yml`) and v1 caller (new workflow file) coexist in each repository during the transition period. Both run on every PR and appear in the PR checks list. Lifecycle per repository:

1. **v1 deployed**: v1 caller added alongside v0. Both run on every PR. Codeowners see both check results.
2. **v1 validated**: Codeowners confirm v1 findings are correct and consistent with expectations.
3. **v1 required**: GitHub ruleset makes the v1 check blocking for PR merge.
4. **v0 removed**: v0 caller file deleted from the repository. Any v0-specific ruleset removed.

The transition is per-repository. Repositories move through stages independently based on pilot experience and codeowner readiness.

### 10.2 Central Enable/Disable

A YAML configuration file in the tooling repository maps each API repository to its validation settings. The reusable workflow reads this file from its own checkout. This is version-controlled, PR-reviewable, and scalable. Adding a repo is one line in a YAML file. Satisfies UC-13 — no per-repo config changes needed.

A repository not listed in the config file is treated as `disabled` — the reusable workflow exits immediately with a notice. This is the safe default for the 60+ repos that have the caller deployed but are not yet onboarded.

### 10.3 Stage Model

The config file controls the validation stage per repository:

| Stage | Config value | Behavior |
|-------|-------------|----------|
| **0: dark** | `disabled` (or not listed) | Caller deployed, reusable workflow exits immediately |
| **1: advisory** | `advisory` | Runs on dispatch only, advisory profile, nothing blocks |
| **2: enabled** | `enabled` | Runs on PRs and dispatch, profile from config |

The config file does not control merge blocking. Merge blocking is enforced by a **GitHub ruleset** (org-level or per-repo) that requires the v1 validation check to pass. This separation keeps the config file focused on validation behavior and rulesets focused on merge policy. Any repository at stage `enabled` can optionally have a blocking ruleset — the two concerns are independent.

In addition to stage, the config file provides per-repo profile settings:

| Field | Default | Description |
|-------|---------|-------------|
| `pr_profile` | `standard` | Profile for PR-triggered validation |
| `release_profile` | `standard` | Profile for pre-snapshot and release review PR validation |

These fields allow tuning validation strictness per repository without changing the stage.

---

## 11. Release Automation Integration

The validation framework integrates with CAMARA release automation at two points in the release lifecycle:

1. **Pre-snapshot gate** (UC-08) — validation runs on the base branch before snapshot creation. Failure blocks the release process.
2. **Release review PR validation** (UC-09) — validation runs on the release review PR with strict profile and content restrictions.

Both touchpoints use the strict profile (section 2.1): errors and warnings block.

### 11.1 Pre-Snapshot Validation Gate

Release automation invokes validation as part of the `/create-snapshot` command, before creating any branches. The validation runs on the current HEAD of the base branch — this is exactly the content that will become the snapshot.

**Timing**: The release state is PLANNED when `/create-snapshot` is invoked. If validation fails, no snapshot branch is created and the state remains PLANNED.

**Profile**: Strict — both errors and warnings block snapshot creation. Rationale: once a snapshot is created, content becomes immutable. Issues found post-snapshot require discarding and recreating the snapshot.

**Scope**: The validation framework runs all applicable checks — Spectral rules, Python consistency checks, bundling validation, and release-plan semantic checks. This subsumes the existing `validate-release-plan.py` preflight.

| Aspect | Current release-plan preflight | With validation framework |
|--------|-------------------------------|---------------------------|
| **Checks** | release-plan.yaml schema + semantics | Full framework: Spectral, Python, bundling, release-plan |
| **Blocking** | Errors only | Errors and warnings (strict profile) |
| **Findings output** | Bot comment with error list | Bot comment with structured findings + fix hints |
| **Token** | camara-release-automation app | Same (passed to framework) |

### 11.2 Release Review PR Validation

A release review PR is created by release automation on the `release-review/rX.Y-<sha>` branch, targeting the `release-snapshot/rX.Y-<sha>` branch. It contains only CHANGELOG and README changes — API specs and other files are immutable on the snapshot branch.

**Detection**: The framework detects a release review PR by its target branch pattern (`release-snapshot/**`).

**Profile**: Strict — errors and warnings block the PR.

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
| Release readiness checks (artifact presence by target API status) | No | Already validated at snapshot creation time; artifacts cannot be added or removed on the snapshot branch |

**File restriction check**: The framework examines the PR diff and produces an error if any file outside `CHANGELOG.md` (or `CHANGELOG/` directory) and `README.md` is modified.

### 11.3 Pre-Snapshot Invocation

The pre-snapshot gate follows the same input design principle as PR and dispatch contexts (section 9.1): the framework derives all release context from `release-plan.yaml` on the checked-out branch. The `mode` parameter distinguishes a pre-snapshot invocation from other triggers.

### 11.4 Post-MVP Extensions

The following integration enhancements are post-MVP:

- **API-aware change summaries for release notes**: Semantic change summaries (breaking changes, new endpoints, modified schemas) for inclusion in release notes or the Release Issue.
- **Snapshot transformer validation**: Validating the transformer's configuration before snapshot creation — verifying that version replacement patterns and server URL formats are correct.

---

## 12. Operational Views

### 12.1 Repository Configuration Validation (UC-14)

An admin needs to verify that an API repository is correctly configured for the validation framework. The following aspects must be checkable:

- **Caller workflow**: The v1 caller workflow file exists in `.github/workflows/` and matches the expected template content
- **Central config listing**: The repository is listed in the tooling config file (section 10.2) with a valid stage value
- **GitHub ruleset** (stage 3 only): The v1 validation check is required in the applicable ruleset
- **Validation app installation**: The validation GitHub App is installed for the repository
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

**On-demand trigger** (UC-17): The tracker or an admin can dispatch validation on selected repositories via `workflow_dispatch` to update dashboard status.

### 12.4 Cross-System Integration Map

| System | Integration point | Data flow | Priority |
|--------|------------------|-----------|----------|
| Release automation (`/create-snapshot`) | Pre-snapshot gate (11.1) | Validation → release automation: pass/fail + findings + bundled specs | Post-MVP (high) |
| Release automation (release review PR) | PR trigger with strict profile (11.2) | Standard PR validation flow, profile auto-selected | Post-MVP (high) |
| Release Progress Tracker | Workflow run query (12.3) | Tracker reads validation run data from GitHub API | Independent |
| Release Progress Tracker | Dispatch trigger (12.3) | Tracker dispatches validation via GitHub API | Independent |
| Tooling config file | Central enable/disable (10.2) | Validation reads config at runtime | MVP |
| GitHub rulesets | Blocking enforcement (10.3) | Ruleset references validation check name | Stage 3 |
| Validation GitHub App | Token minting (8.3) | App provides write token for findings surfacing | MVP |
