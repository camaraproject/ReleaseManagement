# ICM Lifecycle and API Compatibility Governance

**Version:** Draft 2 (2026-05-13)
**Status:** Draft for Release Management WG discussion; incorporates V2 working merge and review feedback.
**Scope:** Response to the ICM WG request to Release Management (per [ICM#324](https://github.com/camaraproject/IdentityAndConsentManagement/issues/324), [ICM#340](https://github.com/camaraproject/IdentityAndConsentManagement/issues/340), [ReleaseManagement#351](https://github.com/camaraproject/ReleaseManagement/issues/351)) to define governance for ICM version evolution and its dependencies with CAMARA API versions.

---

## 1. Scope and Purpose

This guideline defines lifecycle management of Identity and Consent Management (ICM) versions and how CAMARA APIs declare and maintain compatibility with them. It defines under what rules API versions and ICM versions can co-evolve while still providing clear compatibility guarantees.

The guideline recognizes operational reality: API Providers offer the same API version against multiple ICM versions, and API Consumers require an API version and an ICM version as part of a single usage contract — if either aspect changes in a way that affects them, their implementation must adapt.

## 2. Glossary

Terms defined in the CAMARA Commonalities glossary (API, API Consumer, API Provider, meta-release, semantic versioning, scope, etc.) are not repeated here. This section defines terms specific to this guideline.

- **ICM design info**: information defined by an ICM version that applies to API definitions at API design time — e.g. scope format, `securitySchemes` syntax, mandatory `info.description` text, schemas, operations, and similar OAS-level constructs. Supported by guidelines from CAMARA Commonalities (the API Design Guide and related artifacts) for use by API Sub Projects. CAMARA-governed.
- **ICM deployment info**: information defined by an ICM version that applies to API deployments (including at API Provider/Consumer design time and at runtime) — auth flows, grant types, assertion format and lifetime, token processing, claim handling, and similar behaviors agreed between an API Provider and API Consumer. API-Provider-governed in their contractual relationship with API Consumers.
- **API version ICM-compatibility**: the guarantee that an API version's definition respects the ICM design info of a given ICM version. A property of the API definition relative to an ICM version declared in its `x-camara-min-icm` field.
- **API deployment ICM-compatibility**: the guarantee that an API Provider's or API Consumer's deployment (a) deploys ICM-compatible API versions and (b) implements the ICM deployment info of the ICM version it claims to operate under.
- **ICM-compatibility** (umbrella): both API version and API deployment ICM-compatibility together. Successful integration of an API Consumer with an API Provider requires both to hold.
- **ICM version**: a Semantic Versioning (SemVer 2.0) compliant version number with major, minor and patch components, identifying a specific set of ICM artefacts. Starting with ICM 1.0.0, major-version increments indicate breaking changes for API definitions, API deployments, or both — changes that cannot be expressed additively.
- **ICM lifecycle states**: Supported / Deprecated / Retired / Revoked are the four possible lifecycle states of an ICM version (see §5). Lifecycle states apply per ICM version.
- **ICM governance**: the decision process to transition an ICM version to a different lifecycle state (see §5).
- **Exception (waiver)**: a time-bound, governance-approved authorization that permits a specific (API version, ICM version) pair outside the normal ICM-compatibility guarantee.
- **Compatibility matrix**: the derived artifact listing which (API version, ICM version) pairs are ICM-compatible at a given point in time (see §9).

## 3. ICM-compatibility

ICM-compatibility concerns two distinct classes of information defined by an ICM version, referred to as ICM design info and ICM deployment info. Each class has its own scope, governance, and announcement mechanism, and either or both can be changed in a given ICM version independently of the other.

### 3.1 API version ICM-compatibility (design-time)

**An API version is ICM-compatible with an ICM version when its definition respects the ICM design info of that ICM version** — its scope format, `securitySchemes` shape, schemas, operations, and `info.description` text use constructs and conventions defined by the ICM version.

- **Owned and governed by CAMARA.** ICM design info is codified by the CAMARA Commonalities API Design Guide, which mandates how an API definition must align with ICM. API Sub Projects produce API versions that conform to the ICM version by following these guidelines.
- **Declared via `x-camara-min-icm`** (§6) in the API version's definition file at API public release time.
- **Maintained in the compatibility matrix** (§9); the matrix governs API version ICM-compatibility (design-time) — published, governed at CAMARA level, and authoritative for which (API version, ICM version) pairs are ICM-compatible from the API design perspective.

### 3.2 API deployment ICM-compatibility (runtime)

**An API Provider's or API Consumer's deployment is ICM-compatible with an ICM version when (a) it deploys ICM-compatible API versions, and (b) the runtime interactions between API Consumer and API Provider implement the ICM deployment info of that ICM version** — auth flows, grant types, assertion format and lifetime, token processing, and claim handling.

- **Owned and governed by the API Provider.** Deployment ICM-compatibility is a contractual matter between API Provider and API Consumer, communicated by the Provider through onboarding documentation, Provider metadata (for example via OIDC discovery), and similar mechanisms. The mandatory `info.description` text in every CAMARA API spec already states that "the specific authorization flows to be used will be agreed upon during the onboarding process."
- **Identified at deployment/runtime.** An API Consumer determines the applicable ICM version's deployment info by inspecting API Provider metadata and onboarding artifacts; the API version alone does not pin a specific ICM version on the deployment side.
- **Not recorded in the CAMARA compatibility matrix.** The matrix governs API version ICM-compatibility (design-time). API deployment ICM-compatibility is the API Provider's responsibility.

### 3.3 Maintaining ICM-compatibility

Maintaining ICM-compatibility as API versions and ICM versions evolve is a joint responsibility of API designers, API Providers, and API Consumers:

- To maintain ICM-compatibility of API versions, API designers must release updates of API versions that are no longer ICM-compatible to align with a more recent ICM version.
- To maintain ICM-compatibility of API deployments, API Providers must ensure that both ICM-compatibility aspects are respected:
  - each deployed API version must be ICM-compatible with the ICM version it operates against (design-time), or must be upgraded to a newer ICM-compatible API version;
  - the API Provider must implement an ICM version that allows ICM-compatibility of all deployed API versions (runtime).
- The API Consumer is responsible for ensuring that its own implementation matches the ICM version deployed by the API Provider, as well as the deployed API version.

A change in ICM version may impact either or both classes of ICM information independently:

- **A change to ICM design info** (for example, a new scope format) → the API definition may need updating → triggers a new API version for impacted APIs (see §6.1). API Consumers consuming the new API version must adapt their requests to the new format.
- **A change to ICM deployment info** (for example, tightening assertion lifetime) → API Provider deployments and API Consumer implementations must update → does NOT by itself imply a new API version. The API definition is unchanged; only the runtime behavior changes.
- **An ICM change to both** → both consequences apply.

### 3.4 Path from ICM through Commonalities into API definitions

ICM design info changes do not reach API definitions directly. The path is:

1. ICM defines or updates design info (security schemas, scope format, mandatory text, etc.).
2. Commonalities updates the API Design Guide (and other relevant artifacts) to mandate the new design info for API definitions.
3. API Sub Projects update their API versions to align with the new Commonalities API Design Guide.

This means an ICM design info change typically also triggers a Commonalities update. How tightly ICM and Commonalities lifecycles must be coupled is an open item (see §12).

## 4. ICM versioning

This guideline assumes ICM adopts strict SemVer versioning starting with its 1.0.0 release. 

ICM versioning relates to the types of changes made to the two classes of ICM information that impact ICM-compatibility: ICM design info and ICM deployment info (§3):

- changes that break **API version ICM-compatibility** — affecting ICM design info (scope format, `securitySchemes` syntax, schemas, operations), requiring API versions to be updated;
- changes that break **API deployment ICM-compatibility** — affecting ICM deployment info (auth flows, grant types, assertion format and lifetime, token processing), requiring API Provider and Consumer implementations to be updated, independently of the API version.

Both types of changes are captured in the ICM version according to standard SemVer rules:

- **Major version (1.x.y → 2.0.0)**: reserved for breaking changes that cannot be expressed additively. These may be due to ICM design info changes (for example, replacement of a mandatory security schema, an incompatible scope format, removal of a required claim), to ICM deployment info changes (for example, mandatory new authentication rules, an assertion lifetime cap that rejects existing Consumers), or both. Major ICM versions should be deliberately rare and driven by security or regulatory necessity.
- **Minor version change (1.x.y → 1.x+1.0)**: additive only. No breaking change, but minor change to ICM design info (preserves API version ICM-compatibility), or no breaking change, but minor change to ICM deployment info (preserves API deployment ICM-compatibility). For example, new optional flows, new optional claims, new recommendations permitted. Minor changes must not reject previously ICM-compatible API deployment behavior, as these may only apply in a major ICM version change.
- **Patch version (1.2.3 → 1.2.4)**: documentation or defect corrections leading to patch API versions (maintain API version ICM-compatibility), and with no impact on API deployment ICM-compatibility. Example: update of the ICM mandatory text for the API version info.description field.

A change to ICM deployment info that invalidates existing API deployments requires a major ICM version release, even if no new API versions are required. ICM versioning is not focused only on preserving API version ICM-compatibility.

## 5. ICM version lifecycle states and governance

### 5.1 ICM version lifecycle states - definitions

Each ICM version is in exactly one lifecycle state at any given time. States apply per ICM version. A  new major ICM version enters the Supported state at its public release. Subsequent minor or patch versions inherit the state of their major ICM version by default. Governance MAY explicitly transition a specific version to a different state.

The table below summarizes the meaning of each state for the ICM version itself, and its consequences for API versions and API deployments.

| State | ICM version | API version | API deployment |
|---|---|---|---|
| **Supported** | OK to use | may use this ICM version as `x-camara-min-icm` | may operate against this ICM version |
| **Deprecated** | Sunset announced (planned end of life); migration window active | SHOULD NOT use this ICM version as `x-camara-min-icm` | may continue to operate against this ICM version |
| **Retired** | Terminal (end of life) | is no longer ICM-compatible; MUST evolve to a Supported ICM version or be Retired at the API level | is no longer ICM-compatible; MUST migrate to an ICM-compatible deployment with a Supported ICM version |
| **Revoked** | Terminal (exceptional end-of-life); explicitly replaced by an earlier or later ICM version due to defects or security issues and MUST NOT be used; governance names the replacement version | MUST re-establish ICM-compatibility with a Supported ICM version | MUST migrate to a Supported ICM version and ICM-compatible deployment |

Note: the "API version" and "API deployment" columns describe impacts (in CAMARA governance scope) on ICM-compatibility of API versions as declared in the ICM-compatibility matrix and on ICM-compatibility of API deployments. Use outside that scope is not governed by this guideline.

### 5.2 ICM version lifecycle states - transitions

The planned (default) state-transition sequence of an ICM version is 

Supported → Deprecated → Retired

The Revoked state is entered through an exceptional transition decided by governance outside the planned sequence and requires an explicit replacement version to be identified.

Governance MAY transition specific minor or patch ICM versions to Deprecated, Retired, or Revoked when they should no longer be used. 
- For example, when known ambiguities or defects are resolved in a later minor ICM version, or when a critical defect requires replacing a specific patch ICM version. Such per-version transitions do not impact ICM-compatibility of API versions or API deployments. 
- Later minor ICM versions remain compatible with earlier ones by SemVer, but they influence the "lowest" Supported ICM version used in §6.4 and are relevant for API deployments.

Note: the term "Retired" aligns with the API lifecycle terminology, so that ICM and API lifecycles use the same vocabulary for the terminal state.

Note: Deprecation or Retirement of an ICM version does not by itself Deprecate or Retire the API versions that reference it in their `x-camara-min-icm` field. It only changes the corresponding entries in the ICM-compatibility matrix. API version lifecycle (Deprecation, Retirement at the API level) is governed independently by CAMARA's API lifecycle process (see tbd [API lifecycle states](https://github.com/camaraproject/ReleaseManagement/issues/459)).

### 5.3 Governance parameters for ICM lifecycle states

| Parameter | Suggested starting value | Notes |
|---|---|---|
| Duration of Supported state (for previous major ICM version, starting when a new major ICM version is released) | 18 months | Once a newer major ICM version is published, ICM versions with the previous major version number remain Supported for this period before governance transitions them to Deprecated. During this period, API Providers are expected to plan migration to the newer major ICM version. |
| Duration of Deprecated state | 12 months | Active migration period for API deployments before a Deprecated ICM version is Retired; impacts API version ICM-compatibility |
| Concurrent support requirement by API deployments | API Providers shall continue to deploy the most recent previous Supported major ICM version next to the latest published Supported major ICM version (see period defined above) | Applies to ICM-compatible API deployments during this period. |
| Exceptions | Conditions permitting governed ICM lifecycle state transition  | Explicit and recorded governance action per exception; see §10. |

These values are starting points for WG discussion. <!-- to be removed when WG agrees -->

### 5.4 ICM version - Release notes

#### 5.4.1 Publication of lifecycle state

The lifecycle state is published in each ICM version's release notes, as a table in the release notes template. No separate governance artifact is required. Each ICM version release carries the lifecycle state for all ICM versions. State transitions are committed at ICM public release unless an out-of-cycle governance action specifies otherwise.

The published lifecycle state must be available in machine-readable form for the CAMARA validation support to consume (§6.5). Until a schema is defined, the ICM version release notes are the single authoritative source — readable by humans but not by tooling.

#### 5.4.2 ICM version change tables

In addition to the lifecycle state table, each ICM release MUST document **breaking changes** introduced in that ICM version, split by ICM design info changes and ICM deployment info changes, covering the two aspects of ICM-compatibility (§3). Non-breaking changes (additive features, clarifications) are documented in the regular CHANGELOG and do not require entries in the tables below.

**Table A — Breaking ICM design info changes** (impacting API versions; see §3.1). Used by API Sub Projects to assess whether their API versions need a new release.

| ICM version | Breaking design info change | Affected construct | Impact on API definition |
|---|---|---|---|
| _2.0.0_ | _introduces new scope format X_ | _where it appears in an API definition_ | _what API teams need to do_ |

**Table B — Breaking ICM deployment info changes** (impacting API deployments; see §3.2). Used by API Providers and API Consumers to plan deployment updates.

| ICM version | Breaking deployment info change | Affected runtime behavior | Impact on API deployment |
|---|---|---|---|
| _0.3.0_ | _introduces 300s client-assertion lifetime cap_ | _which deployment behavior_ | _what Provider and Consumer need to do_ |

The exact column layout is subject to refinement once concrete examples are filled in (see §12).

## 6. API version ICM-compatibility - details

### 6.1 Minimum ICM version

An API version declares its minimum ICM version via the `x-camara-min-icm` field in its API definition:

```yaml
info:
  # The version of the CAMARA Identity and Consent Management (ICM)
  # specification that this API definition is built against.
  # This API version is compatible with higher ICM versions with the same major version number.
  x-camara-min-icm: 1.2.0
```

This declared ICM version is the ICM version that the API definition relies on and which is Supported at the time of public release of this API version. 

- The value of `x-camara-min-icm` field must be a SemVer valid ICM version.
- It identifies the ICM version that this API is initially compatible with by design (e.g., `1.2.0`). The API version is guaranteed ICM-compatible with any higher ICM version that has the same major version number. ICM-compatibility with different higher major ICM versions must be assessed at ICM version public release and may be extended on governance decision as described below.
- Fixed at API public release. Never changes after the API version is released.

### 6.2 ICM governance responsibilities 

When a new major ICM version is publicly released, the ICM-compatibility of each API version in the ICM-compatibility matrix with respect to this new ICM version needs to be assessed by governance:
- API versions that do not rely on impacted ICM design info may be declared ICM-compatible with the new major ICM version through an explicit governance decision. This is recorded in the ICM-compatibility matrix.
- API versions that do rely on the impacted ICM design info must release a new major API version with the new major ICM version in their `x-camara-min-icm` field. This new pair will be added to the ICM-compatibility matrix.

Example: `x-camara-min-icm: 1.2.0` declared in an API definition means that the API version depends on ICM design info from ICM version 1.2.0 onward. The definition is guaranteed ICM-compatible with any Supported or Deprecated ICM version ≥ 1.2.0 with the same major version number (e.g. with 1.2.1, 1.3.0, but not with 2.0.0). Whether an API version remains ICM-compatible with a subsequent ICM version 2.0.0 is a governance assessment made at the time of the ICM 2.0.0 public version release.

### 6.3 API designer responsibilities

To maintain ICM-compatibility of API versions, an API designer must release an update of the API version when it is no longer ICM-compatible. This incompatibility may be due to:

- Lifecycle state change of the referenced ICM version to Retired or Revoked. API designers must release a new API version referencing a Supported ICM version.
- Availability of a new major ICM version with changes that break either or both:
  - API version ICM-compatibility — affecting ICM design info (scope format, securitySchemes syntax, schemas, operations): API designers must release a new API version compatible with the new major ICM version.
  - API deployment ICM-compatibility — affecting ICM deployment info (auth flows, grant types, assertion format and lifetime, token processing): No need to release a new API version. Maintaining API deployment ICM-compatibility is the responsibility of API Providers and API Consumers.

### 6.4 Determining the `x-camara-min-icm` value

At each API version public release (new major, minor, or patch), the API Sub Project determines the value using the following formula:

```
x-camara-min-icm = max (
  lowest Supported ICM version at API version public release,
  lowest Supported ICM version containing all features this API's definition requires,
  ICM version required by the Commonalities version declared in `x-camara-commonalities`
)
```

For APIs with no ICM-version-specific feature dependencies beyond what Commonalities mandates, the second element is not applicable. This reduces the formula to `max (lowest Supported ICM version at API version public release, lowest ICM version required by the Commonalities version declared in x-camara-commonalities)`. 
Therefore, this formula ensures that releasing a new version of such an API always raises its `x-camara-min-icm` to a Supported ICM version.

### 6.5 CAMARA validation support

A CAMARA linting rule, run at API version release, reads the current ICM lifecycle state (from the latest ICM release's notes) and verifies:
1. `x-camara-min-icm` is present in the API definition.
2. Its value is a syntactically valid SemVer 2.0 version.
3. The value refers to a Supported ICM version at API version public release.

This rule depends on the ICM lifecycle state being published in machine-readable form (see §5.4.1).

## 7. API deployment ICM-compatibility - details

This section describes the governance of API deployment ICM-compatibility (runtime).

An API definition might technically work against an ICM version that the compatibility matrix (§9) does not record as ICM-compatible — for example, a Retired or Revoked ICM version still running somewhere. Such pairings are outside CAMARA governance and are not supported by CAMARA.

### 7.1 API Provider responsibilities

To achieve ICM-compatibility of their API deployment, API Providers MUST:

1. Implement a Supported ICM version.
2. When a new major ICM version is published and is in Supported state, plan implementation of that ICM version. During the period in which the previous major ICM version remains in the Supported state, keep that major ICM version running in parallel, so that API Providers and Consumers can plan the migration of impacted API versions.
3. Announce the ICM versions they implement, in a form that API Consumers can discover (for example via Provider metadata or onboarding documentation).
4. Publish an **ICM-compatibility statement** covering:
   - **API version ICM-compatibility**: for each API version offered.
   - **API deployment ICM-compatibility**: the ICM versions implemented.

This statement declares the API Provider's ICM-compatibility baseline.

The mechanism by which an API Provider provides multiple major ICM versions concurrently is an implementation choice and is not prescribed by this guideline; what matters is that each implemented ICM version is clearly announced by the API Provider for use by API Consumers during the relevant migration period.

An API Provider cannot declare a newly deployed API version as ICM-compatible when offering only a Deprecated or Retired ICM version, even if the API version would technically work with those older ICM versions.

### 7.2 API Consumer responsibilities

Successful API deployments requires the API Consumer to implement its side of the ICM deployment info — auth flows, grant types, assertion format and lifetime, token processing — consistently with the ICM version implemented by the API Provider it interacts with. 

The API Consumer determines the applicable ICM version through Provider metadata or onboarding artifacts, not through the API version alone. API Consumers are not bound by this guideline directly.

The API Consumer is responsible for ensuring that its own implementation matches both the announced ICM version and the API version.

## 8. ICM version release cadence

### 8.1 Signal / Sync meta-release alignment

The Signal meta-release is used to 
- plan and release a new ICM version per evolving requirements
- decide and record previous ICM version lifecycle transitions (lifecycle state table)

New ICM versions MAY be introduced outside Signal meta-releases (out-of-cycle) if required.

ICM releases are done at Signal meta-release (first half of each year); API releases primarily at Sync meta-release (second half of each year). This cadence provides lead time as follows:

1. **Signal Year N**: ICM version published with updated ICM version lifecycle state table. API Sub Projects plan a new API version as needed for Sync Year N. API Providers plan to move their ICM implementation to the newer ICM version.
2. **Signal → Sync (~6 months)**: API Providers move their ICM implementation forward; API Sub Projects produce new API versions.
3. **Sync Year N**: new API versions are released, declaring in their `x-camara-min-icm` the newly Supported ICM version if the API version uses new features that the ICM version introduces.

### 8.2 Out-of-cycle ICM releases

ICM releases outside of the Signal meta-release are allowed and sometimes required, e.g., for security patches, defect corrections, or urgent regulatory changes. These changes impact the ICM version as per SemVer guidelines. 

ICM version lifecycle state transitions may occur off-cycle in security-driven cases, or on explicit governance decision.

## 9. ICM-compatibility matrix

The ICM-compatibility matrix records compatibility by design between API versions and ICM versions. The matrix is maintained as a **derived artifact**, computed automatically from:
- API definition declarations (`x-camara-min-icm` in each published API version).
- ICM version lifecycle state table (from the latest ICM version release notes), including any per-version overrides.
- Exception records (if any).
  - Governance decisions may exceptionally extend an API version's ICM-compatibility to cover an additional major ICM version.
  - Governance decisions may exceptionally extend the duration of an ICM version's Supported or Deprecated lifecycle state. This extends the duration of API version ICM compatibility accordingly.

The matrix lists one row per released public API version and one column per released public ICM version. It records which pairs (API version, ICM version) are ICM-compatible.

### 9.1 ICM-compatibility matrix derivation

The following rule defines how the matrix entries (ICM-compatibility for a pair (API version, ICM version)) are calculated:

```
ICM-compatibility (API vX, ICM vY) =
  ( ICM vY.major == API vX x-camara-min-icm.major
    AND ICM vY >= API vX x-camara-min-icm
    AND ICM vY is in state {Supported, Deprecated} )
  OR a governance decision extends ICM-compatibility to (API vX, ICM vY.major)
  OR a governance approved, time-bound ICM-compatibility exception exists for (API vX, ICM vY)
```

The lifecycle state condition applies to the specific ICM version `vY`, inherited from its major ICM version, unless a per-version override is in place. 

ICM versions in the Retired or Revoked state are excluded from the ICM-compatibility matrix, unless an approved exception has been decided.

The matrix of ICM-compatible pairs (API version, ICM version) are the CAMARA-supported combinations that API Providers may offer and API Consumers may consume.

### 9.2 ICM-compatibility matrix - updates

ICM-compatibility matrix updates are triggered by:
- New ICM version public release (lifecycle state of other ICM versions may change).
- New API version public release (new row added to the matrix; existing rows unchanged).
- Exception granted, modified, or expired.

### 9.3 ICM-compatibility matrix - ownership

The ICM-compatibility matrix is published by Release Management. It is computed, not hand-edited. Only exceptions require human governance action.

## 10. Exception mechanism

Exceptions are time-bound ICM-compatibility authorizations granted by governance. 

Exceptions shall be documented by Release Management using exception decision records with the following information:

- **Scope**: specific (API version, ICM version) pair, or a range.
- **Justification**: required — operational necessity, regulatory requirement, or security consideration.
- **Time bound**: explicit expiry date or condition.
- **Owner**: named API Sub Project or provider responsible for remediation by expiry.
- **Expiry**: automatic. No "ongoing exception" mechanism.

Exceptions are the only mechanism by which an (API version, ICM version) pair can be considered ICM-compatible despite violating the ICM-compatibility rules. Exceptions will appear in the ICM-compatibility matrix with an explicit annotation.

## 11. ICM 0.x handling

This guideline's SemVer-based rules take effect starting with ICM version 1.0.0. For the pre-1.0.0 ICM versions, the one-time historical table below documents which ICM version 0.x.y introduced client-facing breaking changes:

| ICM transition | Client-facing forward break? | Source PRs |
|---|---|---|
| 0.2.0 → 0.3.0 | Yes — client-assertion lifetime cap | [#216](https://github.com/camaraproject/IdentityAndConsentManagement/pull/216) |
| 0.3.0 → 0.4.0 | Yes — mandatory signed-request fields; error-code rename | [#285](https://github.com/camaraproject/IdentityAndConsentManagement/pull/285), [#287](https://github.com/camaraproject/IdentityAndConsentManagement/pull/287) |
| 0.4.0 → 0.5.0 | No — additive | — |

The lifecycle state for pre-1.0.0 ICM versions is assigned by governance also as a one-time exercise. The full SemVer discipline does not apply retroactively to pre-1.0.0 ICM versions.

## 12. Open governance points for discussion/decision

The following require WG agreement before this guideline is adopted:

1. **Exact durations** for the Supported and Deprecated state durations (§5.3).
2. **Transition to ICM 1.0.0** — what constitutes the scope baseline (declaring the then-current definitions of the ICM documents as the stable starting point); when it is declared; who signs off. Pre-1.0.0 versions are handled by the previous section (§11).
3. **Signal vs. out-of-cycle policy** — which ICM changes can be out-of-cycle vs. must align with Signal.
4. **Exception grant process** — who requests, who approves, how documented.
5. **ICM-compatibility statement**; define templates for API version ICM-compatibility and API implementation ICM-compatibility statements; audit process.
6. **Interaction with GSMA certification** — does this decomposition map onto GSMA's processes; alignment discussion required.
7. **Handling of the ICM 0.x transition** — state assignments for existing 0.x versions; end date for 0.x support.
8. **Maximum number of concurrent non-Retired major ICM versions** — whether to cap this to bound API Provider operational complexity when major ICM versions arrive in quick succession (for example, in a security-driven scenario), and how Retirement acceleration would be triggered if the cap is exceeded.
9. **ICM ↔ Commonalities coupling** — ICM design info reaches API definitions through the CAMARA Commonalities API Design Guide (§3.4). Open question: how tightly must the Commonalities and ICM lifecycles couple? Options include mandating a new Commonalities release for each ICM design info change, moving ICM design artifacts into the ICM repository to decouple, or letting Commonalities itself declare a `x-camara-min-icm`. This is a coordination question between the ICM and Commonalities Working Groups.
10. **Example content for the §5.4.2 release-note tables** — Tables A and B in §5.4.2 are stubs awaiting concrete examples from ICM governance. The exact column layout will be refined once examples are filled in.
11. **Cross-major ICM-compatibility assessment — process and timing** — when in the meta-release cycle is the cross-major-ICM versions assessment performed for existing API versions (Signal? Sync? at the moment the new major ICM version is announced/released?), who is responsible for the technical evaluation (API Sub Project? Release Management? ICM WG?), and how is the resulting decision recorded in the ICM-compatibility matrix.
12. **ICM release notes template** request to Release Management to define a machine-readable template with formatting for required sections with e.g. lifecycle state table, breaking changes table A and B, standard CHANGELOG section (Add, Changed, Removed), etc.
13. **ICM info descriptions**: Add detailed list of ICM design and deployment info.

---

## Appendix A: Key positions

- **ICM-compatibility has two distinct aspects** — design-time (API version, governed by CAMARA via Commonalities) and runtime (deployment, governed by API Provider). See §3.
- **A meta-release is not the unit of ICM-compatibility.** ICM-compatibility of individual (API version, ICM version) pairs are constrained by lifecycle states and by governance decisions / exceptions.
- **`x-camara-min-icm`** is introduced as an OpenAPI extension carried by each API version definition, independent of `x-camara-commonalities`.
- **API Provider ICM-compatibility must cover both **API version ICM-compatibility** and **API deployment ICM-compatibility**.
- **The ICM-compatibility matrix is derived by automation**, not hand-maintained.
- **Signal/Sync cadence is a lead-time mechanism**, not a governance gate.
- **ICM design info reaches API definitions via Commonalities**, not directly (§3.4).
