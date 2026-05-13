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

- **ICM design info**: information defined by an ICM version that applies to API definitions at API design time — scope format, `securitySchemes` syntax, mandatory `info.description` text, schemas, operations, and similar OAS-level constructs. Codified by CAMARA Commonalities (the API Design Guide and related artifacts) for use by API Sub Projects. CAMARA-governed.
- **ICM deployment info**: information defined by an ICM version that applies to deployments at runtime — auth flows, grant types, assertion format and lifetime, token processing, claim handling, and similar runtime behaviors negotiated between an API Provider and API Consumer. API-Provider-governed in the contractual relationship with API Consumers.
- **API version ICM-compatibility**: the guarantee that an API version's OAS definition respects the ICM design info of a given ICM version. A property of the API definition relative to an ICM version.
- **Deployment ICM-compatibility**: the guarantee that an API Provider's or API Consumer's deployment (a) deploys ICM-compatible API versions and (b) implements the ICM deployment info of the ICM version it claims to operate under.
- **ICM-compatibility** (umbrella): both aspects together. Successful integration of an API Consumer with an API Provider requires both to hold.
- **ICM version**: a Semantic Versioning (SemVer 2.0) compliant version number with major, minor and patch components, identifying a specific set of ICM artefacts. Starting with ICM 1.0.0, major-version increments indicate breaking changes for API definitions, API deployments, or both — changes that cannot be expressed additively.
- **ICM lifecycle states**: Supported / Deprecated / Retired / Revoked are the four possible lifecycle states of an ICM version (see §6). Lifecycle states apply per ICM version.
- **ICM governance**: the decision process to transition an ICM version to a different lifecycle state (see §6).
- **Exception (waiver)**: a time-bound, governance-approved authorization that permits a specific (API version, ICM version) pair outside the normal ICM-compatibility guarantee.
- **Compatibility matrix**: the derived artifact listing which (API version, ICM version) pairs are ICM-compatible at a given point in time (see §11).

## 3. ICM-compatibility — two aspects, two responsibilities

ICM-compatibility has two distinct aspects. Each has its own scope, governance, and signaling mechanism, and each can be impacted by a given ICM change independently of the other.

### 3.1 API version ICM-compatibility (design-time)

**An API version is ICM-compatible with an ICM version when its OAS definition respects the ICM design info of that ICM version** — its scope format, `securitySchemes` shape, schemas, operations, and `info.description` text use constructs and conventions defined by the ICM version.

- **Owned and governed by CAMARA.** ICM design info is codified by the CAMARA Commonalities API Design Guide, which mandates how an API definition must align with ICM. API Sub Projects produce API versions that conform.
- **Signaled by `x-camara-min-icm`** (§7) declared in the API version's OAS file at API public release time.
- **Maintained in the compatibility matrix** (§11) — published, governed at CAMARA level, and authoritative for which (API version, ICM version) pairs are CAMARA-compliant from the design-time perspective.

### 3.2 Deployment ICM-compatibility (runtime)

**An API Provider's or API Consumer's deployment is ICM-compatible with an ICM version when (a) it deploys ICM-compatible API versions, and (b) the runtime interactions between API Consumer and API Provider implement the ICM deployment info of that ICM version** — auth flows, grant types, assertion format and lifetime, token processing, and claim handling.

- **Owned and governed by the API Provider.** Deployment ICM-compatibility is a contractual matter between API Provider and API Consumer, communicated by the Provider through onboarding documentation, Provider metadata (for example via OIDC discovery), and similar mechanisms. The mandatory `info.description` text in every CAMARA API spec already states that "the specific authorization flows to be used will be agreed upon during the onboarding process."
- **Discovered at runtime.** An API Consumer determines which ICM version's deployment info applies by inspecting Provider metadata and onboarding artifacts; the API version alone does not pin a specific ICM version on the deployment side.
- **Not recorded in the CAMARA compatibility matrix.** The matrix governs API version ICM-compatibility (design-time). Deployment compliance is the API Provider's responsibility.

### 3.3 The combined view for the API Consumer

For successful integration, both aspects must hold: the API version must be ICM-compatible with some ICM version (design-time), and the Provider's deployment must implement a compatible ICM version (runtime). The API Consumer is responsible for ensuring its own implementation matches the deployment ICM version actually in operation.

The two aspects can be impacted independently:

- **An ICM change to design info** (for example, a new scope format) → the API definition may need updating → triggers a new API version for impacted APIs (see §4). API Consumers consuming the new API version must adapt their requests to the new format.
- **An ICM change to deployment info** (for example, tightening assertion lifetime) → API Provider deployments and API Consumer implementations must update → does NOT by itself trigger a new API version. The API definition is unchanged; only the runtime behavior changes.
- **An ICM change to both** → both consequences apply.

### 3.4 Path from ICM through Commonalities into API definitions

ICM design info changes do not reach API definitions directly. The path is:

1. ICM defines or updates design info (security schemas, scope format, mandatory text, etc.).
2. Commonalities updates the API Design Guide (and other relevant artifacts) to mandate the new design info for API definitions.
3. API Sub Projects update their API versions to align with the new Commonalities API Design Guide.

This means an ICM design info change typically also triggers a Commonalities update. How tightly ICM and Commonalities lifecycles must be coupled is an open item (see §14).

## 4. Minimum ICM version — rule for API version ICM-compatibility

This section governs the design-time aspect of ICM-compatibility (§3.1). Rules for the deployment-time aspect are in §8.

An API version declares its minimum ICM version via the `x-camara-min-icm` field in its API definition. This floor expresses the oldest ICM version that the API definition relies on and which is Supported at the time of release of the API version. Subject to ICM's SemVer discipline (§5), the API version is guaranteed ICM-compatible with any ICM version at or above that floor, at least within the same major ICM version.

When ICM crosses a major-version boundary, each API definition is assessed by governance at that boundary. API definitions that do not rely on ICM-version-specific constructs may be declared ICM-compatible with the new major through an explicit governance decision recorded in the compatibility matrix. Definitions that do rely on such constructs must be re-released as a new API major targeting the new major ICM version.

Example: `x-camara-min-icm: 1.2.0` declared in an API definition means the API depends on ICM 1.x design info from version 1.2.0 onward. The definition is guaranteed ICM-compatible with any Supported or Deprecated ICM version ≥ 1.2.0 in the 1.x major. Whether it remains ICM-compatible with a future 2.x version is a governance assessment made at the time of the ICM 2.0 release.

## 5. ICM SemVer commitment (starting at 1.0.0)

This guideline assumes ICM adopts strict SemVer versioning starting with its 1.0.0 release. The discipline applies to two distinct classes of information changes, mapping to the two aspects of ICM-compatibility (§3):

- changes that break **API version ICM-compatibility** — affecting ICM design info (scope format, `securitySchemes` syntax, schemas, operations) and requiring API definitions to be updated;
- changes that break **deployment ICM-compatibility** — affecting ICM deployment info (auth flows, grant types, assertion format and lifetime, token processing) and requiring Provider and Consumer implementations to be updated, independently of any API definition.

Both classes are governed by the same SemVer rules:

- **Minor versions (1.x → 1.y)**: additive only. No breaking change to ICM design info (preserves API version ICM-compatibility) and no breaking change to ICM deployment info (preserves deployment ICM-compatibility). New optional flows, new optional claims, new recommendations permitted. Removals, replacements, and tightenings that reject previously-legal API definitions or deployment behavior may only appear at a major-version boundary.
- **Major versions (1.x → 2.0)**: reserved for breaking changes that cannot be expressed additively. These may affect ICM design info (for example, replacement of a mandatory security schema, an incompatible scope format, removal of a required claim), affect ICM deployment info (for example, mandatory new authentication rules, an assertion lifetime cap that rejects existing Consumers), or both. Majors should be deliberately rare and driven by security or regulatory necessity.
- **Patch versions (1.2.3 → 1.2.4)**: editorial or defect corrections with no impact on either aspect.

An ICM change that invalidates existing deployment implementations is a major-version event even if no API definition requires re-release. Semver discipline is not satisfied by preserving API version ICM-compatibility alone.

The transition to 1.0.0 should coincide with a scope-baseline review of the ICM documents, declaring the then-current definitions as the stable starting point. Pre-1.0 versions are handled by the Legacy section (§12).

## 6. ICM lifecycle states and governance

### 6.1 State model

Each ICM version is in exactly one lifecycle state at any given time. States apply per ICM version, with the major ICM version as the primary grain: a new major enters the Supported state at its public release, and sub-major versions (minor and patch) inherit their major's state by default. Governance MAY explicitly transition a specific sub-major version to a different state.

The table below summarizes each state's meaning for the ICM version itself and its consequences for API versions and API deployments (mapping the two-axis decomposition of §3 onto the state model).

| State | ICM version | API version | API deployment |
|---|---|---|---|
| **Supported** | OK to use | may be used as `x-camara-min-icm` | may operate against this ICM version |
| **Deprecated** | Sunset announced; migration window active | SHOULD NOT be used as `x-camara-min-icm` | may continue to operate against this ICM version |
| **Retired** | Terminal (planned end of life) | is no longer ICM-compatible; MUST evolve to a Supported ICM version or be Retired at the API level | MUST migrate to an ICM-compatible deployment with a Supported ICM version |
| **Revoked** | Terminal (exceptional); replaced by a later minor or patch version due to defects or security issues and MUST NOT be used; governance names the replacement version | MUST re-establish ICM-compatibility with a Supported ICM version | MUST migrate to a Supported ICM version and ICM-compatible deployment |

Note: the "API version" and "API deployment" columns describe consequences within CAMARA governance scope — i.e., for API versions published in the CAMARA catalog and for CAMARA-compliant API Provider deployments. Use outside that scope is not governed by this guideline.

The planned state-transition sequence is Supported → Deprecated → Retired. Revoked is entered as an exceptional action outside this sequence and requires an explicit replacement version.

For Supported major ICM versions, governance MAY transition specific minor or patch versions to Deprecated, Retired, or Revoked when they should no longer be used as a floor — for example, when known ambiguities or defects are resolved in a later minor version, or when a critical defect requires replacing a specific patch version. Such per-version transitions do not impact ICM-compatibility of API versions or API deployments — later minor ICM versions remain compatible with earlier ones by SemVer — but they influence the "lowest Supported minor" used in §7.2 and are relevant for API deployments.

Note: the term "Retired" aligns with the API lifecycle terminology proposed in [ReleaseManagement#459](https://github.com/camaraproject/ReleaseManagement/issues/459), so that ICM and API lifecycles use the same vocabulary for the terminal state.

Note: Deprecation or Retirement of an ICM major does not by itself Deprecate or Retire API versions referencing it — only the corresponding cells in the compatibility matrix change. API version lifecycle (Deprecation, Retirement at the API level) is governed independently by CAMARA's API lifecycle process (see [ReleaseManagement#459](https://github.com/camaraproject/ReleaseManagement/issues/459)).

### 6.2 Governance parameters

| Parameter | Suggested starting value | Notes |
|---|---|---|
| Duration of Supported state for an ICM major after its successor is published | ≥ 18 months | After a newer major ICM version is published, the previous major remains Supported for at least this period before governance transitions it to Deprecated. During this period, API Providers plan to migrate to the newer ICM major. |
| Duration of Deprecated state | ≥ 12 months | Active migration period for deployments before the major is Retired. |
| Concurrent support requirement | Latest published Supported major ICM version + most recent previous Supported major (during overlap) | Applies to CAMARA-compliant API Providers during this period. |
| Security kill-switch | Conditions permitting acceleration of any state transition | Explicit governance action per incident; see §13. |

These values are starting points for WG discussion.

### 6.3 Publication of state

State is published in each ICM release's notes, as a standard table in the release notes template. No separate governance artifact is required — each ICM release carries the current state for all active ICM majors. Between ICM releases, the state from the latest release is authoritative. State transitions are committed at ICM release time unless an out-of-cycle governance action specifies otherwise.

A machine-readable schema for the published state may be defined later to support automated tooling, once the state-model concepts in this section are settled. Until then, the ICM release notes are the single authoritative source.

### 6.4 ICM release notes — design info and deployment info change tables

In addition to the state table, each ICM release SHOULD document **breaking changes** introduced in that ICM version, split by the two aspects of ICM-compatibility (§3). Non-breaking changes (additive features, clarifications) are documented in the regular CHANGELOG and do not require entries in the tables below.

**Table A — Breaking ICM design info changes** (impacting API definitions; see §3.1). Used by API Sub Projects to assess whether their API versions need a new release.

| ICM version | Breaking design info change | Affected construct | Impact on API definitions |
|---|---|---|---|
| _example to fill in: e.g., "1.x → 2.0 introduces new scope format X"_ | _what changed_ | _where it appears in an API definition_ | _what API teams need to do_ |

**Table B — Breaking ICM deployment info changes** (impacting runtime deployments; see §3.2). Used by API Providers and API Consumers to plan deployment updates.

| ICM version | Breaking deployment info change | Affected runtime behavior | Impact on deployments |
|---|---|---|---|
| _example to fill in: e.g., "0.3.0 introduces 300s client-assertion lifetime cap"_ | _what changed_ | _which deployment behavior_ | _what Provider and Consumer need to do_ |

The exact column layout is subject to refinement once concrete examples are filled in (see §14).

## 7. API spec declaration: `x-camara-min-icm`

### 7.1 Declaration

Every CAMARA API definition declares a single top-level extension field naming the minimum required version of the CAMARA Identity and Consent Management specification:

```yaml
info:
  # Minimum version of the CAMARA Identity and Consent Management (ICM)
  # specification this API definition is built against.
  x-camara-min-icm: 1.2.0
```

- Three-part semantic version matching the ICM release versioning scheme.
- Names the lowest ICM version against which the API definition is ICM-compatible.
- Names the major ICM version family this API is initially compatible with (e.g., `1.2.0` → ICM 1.x). Cross-major compatibility may be extended via §4 governance assessment.
- Publication-time fixed. Does not change after the API version is released.
- The field name follows the CAMARA convention for ICM-related extensions (parallel to `x-camara-commonalities`), with no `-version` suffix; the field name itself denotes a version.

### 7.2 Rule for choosing the value at release

At each API release (new major, minor, or patch), the API Sub Project sets the value as:

```
x-camara-min-icm := max(
  lowest Supported ICM version at release time,
  lowest ICM version containing all features this API's definition requires,
  lowest ICM version required by the Commonalities version declared in `x-camara-commonalities`
)
```

For APIs with no ICM-version-specific feature dependencies beyond what Commonalities mandates, the second operand collapses to zero and the rule reduces to `max(lowest Supported ICM version at release time, ICM floor required by the declared Commonalities version)`. Publishing a new API version therefore always raises its floor to a Supported ICM major. An API Provider cannot declare a newly published API version as CAMARA compliant while offering only a Deprecated or Retired ICM major, even if the definition would technically work with those older versions.

Past API versions retain their published value; the floor is publication-time fixed even if the lowest Supported ICM version moves upward over time. Such declarations remain functionally valid within their original ICM major; cross-major compatibility is assessed by governance per §4.

### 7.3 Validation

A CAMARA linting rule, run at API release time, reads the current ICM state (from the latest ICM release's notes) and verifies:
1. `x-camara-min-icm` is present.
2. Its value is a syntactically valid SemVer 2.0 version.
3. The value is a Supported ICM version at release time (the feature-dependency floor and the Commonalities-required floor per §7.2 may raise the minimum).

## 8. API Provider responsibilities — deployment ICM-compatibility

This section governs the deployment-time aspect of ICM-compatibility (§3.2). Rules for the design-time aspect (API version ICM-compatibility) are in §4.

An API definition might technically work against an ICM version that the compatibility matrix (§11) does not record as CAMARA-compliant — for example, a Retired or Revoked ICM version still running somewhere. Such pairings are outside CAMARA governance and cannot be claimed as CAMARA compliant.

CAMARA-compliant API Providers MUST:

1. Implement the latest published Supported major ICM version.
2. During the period in which a previous ICM major remains in the Supported state, also implement that major, so that API versions targeting either Supported major can be served.
3. Publish the ICM versions they implement, in a form that API Consumers can discover (for example via Provider metadata, onboarding documentation, or the standard `info.description` template mandated by Commonalities).
4. Publish **two separate compliance statements**:
   - **API-specification compliance**: for each API version offered (the API-version-ICM-compatibility side, §4).
   - **ICM-implementation compliance**: which major ICM versions the Provider implements (the deployment-ICM-compatibility side).

These two statements together constitute the API Provider's CAMARA-compliance posture.

The mechanism by which an API Provider implements multiple ICM majors concurrently is an implementation choice and is not prescribed by this guideline; what matters is that each implemented major ICM version is discoverable and usable by API Consumers during the relevant period.

### 8.1 API Consumer responsibilities

Successful end-to-end integration requires the API Consumer to implement its side of the ICM deployment info — auth flows, grant types, assertion format and lifetime, token processing — consistently with the ICM version implemented by the API Provider it interacts with. The API Consumer determines this ICM version through Provider metadata and onboarding artifacts, not through the API version alone. API Consumers are not bound by this guideline directly; this section describes what an API Consumer needs to do to integrate with a CAMARA-compliant API Provider.

## 9. Aggregator role

Aggregators accept suppliers offering (API version, ICM version) pairs across a spectrum and present API Consumers with a narrower, consistent set of offerings — typically two or three API versions and one or two ICM majors, giving API Consumers time to migrate on both axes.

Aggregators operate as ecosystem normalizers:
- They MAY wrap or transform between ICM majors (for example, accepting ICM 2.x assertions from API Consumers while calling ICM 1.x suppliers, or vice versa).
- They MAY narrow the supplier pool to those operating at specific ICM majors they choose to offer.
- They MAY encourage convergence among their suppliers toward a common set of (API, ICM) pairs by aligning their commercial onboarding and support processes accordingly.

This guideline recognizes aggregators as a first-class actor in the CAMARA ecosystem. The matrix of (API version, ICM version) pairs across raw suppliers is a consequence of API and ICM versions evolving on independent cadences; aggregators handle matrix reduction for their API Consumers, and CAMARA governance provides the outer envelope within which both suppliers and aggregators operate.

## 10. Release governance cadence

### 10.1 Signal / Sync alignment

ICM releases are announced primarily at Signal meta-releases (H1 each year); API releases primarily at Sync meta-releases (H2). This natural cadence provides lead time:

1. **Signal Year N**: ICM version published with state table. API Providers plan to move to the newer ICM version. API Sub Projects plan their new API versions.
2. **Signal → Sync gap (~6 months)**: API Providers move their ICM implementation forward; API Sub Projects produce new API versions.
3. **Sync Year N**: new API versions land, declaring in `x-camara-min-icm` the newly Supported major ICM version if they use new features it introduces.

### 10.2 Out-of-cycle ICM releases

Out-of-cycle ICM releases are permitted and sometimes required — e.g., for security patches, defect corrections, or urgent regulatory changes. These follow the same SemVer discipline. State transitions may occur off-cycle in security-driven cases, with explicit governance record.

### 10.3 Signal is not a gate

Signal timing is an announcement and coordination anchor, not a mandatory gate. ICM versions MAY be introduced outside Signal when necessary. API versions MAY be released outside Sync. Governance focuses on content discipline (SemVer correctness, state assignments) rather than calendar alignment.

## 11. Compatibility matrix as derived artifact

The API–ICM compatibility matrix is maintained as a **derived artifact**, computed automatically from:
- API version declarations (`x-camara-min-icm` in each published API definition).
- ICM state per published ICM version (from the latest ICM release notes), including any per-version overrides.
- Exception waivers (if any).
- Governance decisions extending an API definition's ICM-compatibility across an ICM major boundary (per §4).

The matrix lists one row per published API version and one column per published ICM version. It records which (API version, ICM version) pairs are CAMARA-compliant.

### 11.1 Compatibility computation

```
compatible(API vX, ICM version vY) :=
  vY's major == major(API vX's x-camara-min-icm)
  AND vY >= API vX's x-camara-min-icm
  AND vY is in state {Supported, Deprecated}
  OR a governance decision extends the API's ICM-compatibility to vY's major
  OR an approved, time-bound compatibility waiver exists
```

The state condition applies to the specific ICM version `vY`, inheriting from its major unless a per-version override is in place. Versions in the Retired or Revoked state are excluded from all positive compatibility cells, except via an approved waiver.

Cells that are "compatible" represent legitimate (API, ICM) pairs that API Providers may offer and API Consumers may consume.

### 11.2 Ownership

The matrix is published by Release Management. It is computed, not hand-edited. Only exception waivers require human governance action.

### 11.3 Scope

Matrix update triggers are:
- New ICM release (state may change).
- New API release (new row added; old rows unchanged).
- Exception granted, modified, or expired.

## 12. Legacy ICM 0.x handling

This guideline's SemVer-based rules take effect with ICM 1.0.0. For the pre-1.0 transition period, Release Management publishes a one-time historical record documenting which ICM 0.x transitions were client-facing-breaking:

| ICM transition | Client-facing forward break? | Source PRs |
|---|---|---|
| 0.2.0 → 0.3.0 | Yes — client-assertion lifetime cap | [#216](https://github.com/camaraproject/IdentityAndConsentManagement/pull/216) |
| 0.3.0 → 0.4.0 | Yes — mandatory signed-request fields; error-code rename | [#285](https://github.com/camaraproject/IdentityAndConsentManagement/pull/285), [#287](https://github.com/camaraproject/IdentityAndConsentManagement/pull/287) |
| 0.4.0 → 0.5.0 | No — additive | — |

State for 0.x versions is assigned by ICM governance as a one-time exercise. The full SemVer discipline does not apply retroactively to pre-1.0 versions.

## 13. Exception mechanism

Exceptions are time-bound compatibility waivers granted by governance:

- **Scope**: specific (API version, ICM version) pair, or a range.
- **Justification**: required — operational necessity, regulatory requirement, or security consideration.
- **Time bound**: explicit expiry date or condition.
- **Owner**: named API Sub Project or provider responsible for remediation by expiry.
- **Expiry**: automatic. No "ongoing exception" mechanism.

Exceptions are the only mechanism by which a (API, ICM) pair can be deemed compatible despite violating the core rules in §4 and §6. They appear in the compatibility matrix with explicit annotation.

## 14. Open governance decisions

The following require WG agreement before this guideline is adopted:

1. **Exact durations** for the Supported and Deprecated state durations (§6.2).
2. **Transition to ICM 1.0.0** — what constitutes the scope baseline; when it is declared; who signs off.
3. **Signal vs. out-of-cycle policy** — which ICM changes can be out-of-cycle vs. must align with Signal.
4. **Exception grant process** — who requests, who approves, how documented.
5. **CAMARA-compliance statement content** — exact templates for API-specification compliance and ICM-implementation compliance; audit process.
6. **Interaction with GSMA certification** — does this decomposition map onto GSMA's processes; alignment discussion required.
7. **Handling of the ICM 0.x transition** — state assignments for existing 0.x versions; end date for 0.x support.
8. **Maximum number of concurrent non-Retired ICM majors** — whether to cap this to bound Provider operational complexity when ICM majors arrive in quick succession (for example, in a security-driven scenario), and how Retirement acceleration would be triggered if the cap is exceeded.
9. **ICM ↔ Commonalities coupling** — ICM design info reaches API definitions through the CAMARA Commonalities API Design Guide (§3.4). Open question: how tightly must the Commonalities and ICM lifecycles couple? Options include mandating a new Commonalities release for each ICM design info change, moving ICM design artifacts into the ICM repository to decouple, or letting Commonalities itself declare a `x-camara-min-icm`. This is a coordination question between the ICM and Commonalities Working Groups.
10. **Example content for the §6.4 release-note tables** — Tables A and B in §6.4 are stubs awaiting concrete examples from ICM governance. The exact column layout will be refined once examples are filled in.
11. **Cross-major ICM-compatibility assessment — process and timing** — when in the meta-release cycle is the cross-major assessment performed for existing API versions (Signal? Sync? at the moment the new ICM major is announced?), who is responsible for the technical evaluation (API Sub Project? Release Management? ICM WG?), and how is the resulting decision recorded in the compatibility matrix.

---

## Appendix A: Key positions

- **ICM-compatibility has two distinct aspects** — design-time (API version, governed by CAMARA via Commonalities) and runtime (deployment, governed by API Provider). See §3.
- **Meta-release is not the unit of compatibility.** Individual (API, ICM) pairs are, constrained by governance states and by the per-major binding rule in §4.
- **`x-camara-min-icm`** is introduced as an OpenAPI extension carried by each API definition, independent of `x-camara-commonalities`.
- **API Provider compliance is decomposed** into API-specification compliance and ICM-implementation compliance (§8).
- **The compatibility matrix is automated**, not hand-maintained.
- **Signal/Sync cadence is a lead-time mechanism**, not a governance gate.
- **ICM design info reaches API definitions via Commonalities**, not directly (§3.4).

## Appendix B: What this guideline intentionally does not do

- Does not define a detailed state-machine with per-minor-version state assignments. States are per-major.
- Does not require any `x-camara-icm` structured block with multiple fields. A single flat string suffices.
- Does not introduce a "re-release without `info.version` change" mechanism. The `x-camara-min-icm` value is publication-time fixed.
- Does not mandate that ICM majors align with Signal meta-releases. Strongly suggested, not required.
- Does not prescribe the implementation mechanism by which an API Provider serves multiple ICM majors. Only behavioral requirements apply.
