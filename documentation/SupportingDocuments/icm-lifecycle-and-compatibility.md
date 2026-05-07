# ICM Lifecycle and API Compatibility Governance

**Version:** Draft 1 (2026-04-21)
**Status:** Draft for Release Management WG discussion.
**Scope:** Response to the ICM WG request to Release Management (per [ICM#324](https://github.com/camaraproject/IdentityAndConsentManagement/issues/324), [ICM#340](https://github.com/camaraproject/IdentityAndConsentManagement/issues/340), [ReleaseManagement#351](https://github.com/camaraproject/ReleaseManagement/issues/351)) to define governance for ICM version evolution and its dependencies with CAMARA API versions.

---

## 1. Scope and Purpose

This guideline defines lifecycle management of Identity and Consent Management (ICM) versions and how CAMARA APIs declare and maintain compatibility with them. It answers the question posed by the ICM Working Group to Release Management: under what rules can API versions and ICM versions co-evolve while still providing clear compatibility guarantees to API Consumers?

The guideline recognizes operational reality: API Providers offer the same API version against multiple ICM versions, and API Consumers require an API version and an ICM version as part of a single usage contract — if either aspect changes in a way that affects them, their implementation must adapt.

## 2. Glossary

Terms defined in the CAMARA Commonalities glossary (API, API Consumer, API Provider, meta-release, semantic versioning, scope, etc.) are not repeated here. This section defines terms specific to this guideline.

- **ICM-compatibility**: the guarantee that an API version's specification is valid against a given ICM version — its scope format, `securitySchemes` syntax, schemas, and operations use constructs defined by that ICM version. ICM-compatibility is a property of the API specification relative to an ICM version.
- **ICM major version**: the major component of an ICM semantic version (e.g., "1" in "1.y.z"). Starting with ICM 1.0.0, major-version increments indicate breaking changes for API Consumers or API specifications that cannot be expressed additively.
- **Supported / Deprecated / Retired / Revoked**: the four lifecycle states for an ICM version (see §6). States apply per ICM version, with the ICM major version as the primary grain.
- **Preferred**: a designation — not a state — applied to exactly one Supported ICM major version at any given time, identifying it as the current baseline for newly published CAMARA API versions (see §6).
- **Exception (waiver)**: a time-bound, governance-approved authorization that permits a specific (API version, ICM version) pair outside the normal ICM-compatibility guarantee.
- **Compatibility matrix**: the derived artifact listing which (API version, ICM version) pairs are ICM-compatible at a given point in time (see §12).

## 3. ICM-compatibility

ICM-compatibility, as defined in the glossary, applies to an API version's specification. It is established by the API Sub Project at API publication time via the `x-camara-min-icm-version` field (§7) and verified by governance through the compatibility matrix (§12).

API Consumers use an API in combination with an API Provider's ICM implementation. To successfully integrate, a Consumer must implement the authentication and authorization behaviors — flows, grants, assertions, token processing — defined by the ICM version the Provider implements. This is independent of the API version being consumed: an ICM change that tightens authentication rules affects Consumers interacting with any Provider who moves to that ICM version, regardless of which APIs they consume. ICM-compatibility of the API specification and the Consumer's implementation readiness are separate concerns — both must be satisfied for a Consumer to successfully integrate.

An ICM change may affect the API specification (triggering an API release to restore ICM-compatibility), the API Consumer implementation (requiring Consumer-side updates), or both. The semver discipline in §5 applies to both kinds of breaking changes.

## 4. Core rule

An API version declares its minimum ICM version via `x-camara-min-icm-version`. This floor expresses the oldest ICM version whose constructs the API specification relies on and which is Supported at the release time of the API. Subject to ICM's semver discipline (§5), the API specification is guaranteed ICM-compatible with any ICM version at or above that floor, at least within the same ICM major.

When ICM crosses a major-version boundary, each API specification is assessed by governance at that boundary. API specifications that do not rely on ICM-version-specific constructs may be declared ICM-compatible with the new major through an explicit governance decision recorded in the compatibility matrix. Specifications that do rely on such constructs must be re-released as a new API major targeting the new ICM major. §7.3 describes an optional field that allows an API specification to declare compatibility with more than one ICM major explicitly.

Concretely: `x-camara-min-icm-version: 1.2.0` declared in an API specification means the API depends on ICM 1.x features from version 1.2.0 onward. The specification is guaranteed ICM-compatible with any Supported or Deprecated ICM version ≥ 1.2.0 in the 1.x major. Whether it remains ICM-compatible with a future 2.x version is a governance assessment made at the time of the ICM 2.0 release.

## 5. Prerequisite: ICM semver commitment at 1.0.0

This guideline assumes ICM adopts strict semver starting with its 1.0.0 release. The discipline applies to two distinct classes of breaking changes:

- changes that break **ICM-compatibility** — affecting API specifications (scope format, `securitySchemes` syntax, schemas, operations);
- changes that break **API Consumer implementations** — affecting authentication behaviors (flows, grants, assertions, token handling) independently of any API specification.

Both classes are governed by the same semver rules:

- **Minor versions (1.x → 1.y)**: additive only. No breaking change for API specifications (preserves ICM-compatibility) and no breaking change for API Consumer implementations. New optional flows, new optional claims, new recommendations permitted. Removals, replacements, and tightenings that reject previously-legal specifications or Consumer behavior are not permitted within a major.
- **Major versions (1.x → 2.0)**: reserved for breaking changes that cannot be expressed additively. These may affect ICM-compatibility (for example, replacement of a mandatory security schema, an incompatible scope format, removal of a required claim), affect API Consumer implementations (for example, mandatory new authentication rules, an assertion lifetime cap that rejects existing Consumers), or both. Majors should be deliberately rare and driven by security or regulatory necessity.
- **Patch versions (1.2.3 → 1.2.4)**: editorial or defect corrections with no impact on either ICM-compatibility or API Consumer implementations.

An ICM change that invalidates existing Consumer implementations is a major-version event even if no API specification requires re-release. Semver discipline is not satisfied by preserving ICM-compatibility alone.

The transition to 1.0.0 should coincide with a scope-baseline review of the ICM documents, declaring the then-current definitions as the stable starting point. Pre-1.0 versions are handled by the Legacy section (§13).

## 6. ICM lifecycle governance

### 6.1 State model

Each ICM version moves through lifecycle states. States apply per ICM version, with the ICM major version as the primary grain: a new major enters the Supported state at its public release, and sub-major versions (minor and patch) inherit their major's state by default. Governance MAY explicitly assign a different state to a specific sub-major version.

| State | Meaning |
|---|---|
| **Supported** | Active; APIs may declare and operate against this version |
| **Deprecated** | Sunset announced; migration window active; no new APIs should declare this version |
| **Retired** | Terminal (planned end of life); APIs bound to a Retired version are no longer CAMARA-compliant and must transition or be Retired at the API level |
| **Revoked** | Terminal (exceptional); the version has been replaced by a later patch or minor due to defects or security issues and MUST NOT be used. Governance names the replacement version. |

The planned state-transition sequence is Supported → Deprecated → Retired. Revoked is entered as an exceptional action outside this sequence and requires an explicit replacement version.

**Preferred** is not a lifecycle state but a designation applied to exactly one Supported ICM major version at any given time, identifying it as the current baseline for newly published CAMARA API versions. The Preferred designation is assigned by governance and MAY be reassigned to a newer Supported major at its public release or at a later governance decision. Reassignment of the Preferred designation is an explicit governance action, not automatic. A major that loses the Preferred designation remains in the Supported state until governance moves it to Deprecated.

Governance MAY mark specific minor or patch versions within a Supported major as Deprecated, Retired, or Revoked when they should no longer be used as a floor — for example, when known ambiguities or defects are resolved in later minors, or when a critical defect requires replacing a specific patch version. Such per-version markings do not introduce incompatibility for API clients — later minors remain compatible with earlier ones by semver — but they influence the "lowest Supported minor" used in §7.2 and are relevant for API Providers.

Note: the term "Retired" aligns with the API lifecycle terminology proposed in [ReleaseManagement#459](https://github.com/camaraproject/ReleaseManagement/issues/459), so that ICM and API lifecycles use the same vocabulary for the terminal state.

### 6.2 Governance parameters

| Parameter | Suggested starting value | Notes |
|---|---|---|
| Duration of Supported state after losing Preferred designation | ≥ 18 months | Time a major remains Supported after losing the Preferred designation before it enters Deprecated. During this period, API Providers plan to move to the newer ICM major. |
| Duration of Deprecated state | ≥ 12 months | Active migration period before the major is Retired |
| Concurrent support requirement | Major holding the Preferred designation + most recent other Supported major | Applies to CAMARA-compliant API Providers during this period |
| Security kill-switch | Conditions permitting acceleration of any state transition | Explicit governance action per incident; see §14 |

These values are starting points for WG discussion. With the suggested minimums, an ICM major's lifetime in the Supported state after losing the Preferred designation is at least ~18 months, followed by ≥12 months in Deprecated before it is Retired. The duration during which a major holds the Preferred designation is a separate governance decision, typically set by when the next major is ready for introduction.

### 6.3 Publication of state

State is published in each ICM release's notes, as a standard table in the release notes template. No separate governance artifact is required — each ICM release carries the current state for all active ICM majors. Between ICM releases, the state from the latest release is authoritative. State transitions are committed at ICM release time unless an out-of-cycle governance action specifies otherwise.

A machine-readable schema for the published state may be defined later to support automated tooling, once the state-model concepts in this section are settled. Until then, the ICM release notes are the single authoritative source.

## 7. API spec declaration: `x-camara-min-icm-version`

### 7.1 Declaration

Every CAMARA API specification declares a single top-level extension field:

```yaml
info:
  x-camara-min-icm-version: 1.2.0
```

- Three-part semantic version matching the ICM release versioning scheme.
- Names the lowest ICM version against which the API specification is ICM-compatible.
- Implicitly names the ICM major: `1.2.0` binds the API to the ICM 1.x family of features.
- Publication-time fixed. Does not change after the API version is released.

### 7.2 Rule for choosing the value at release

At each API release (new major, minor, or patch), the API Sub Project sets the value as:

```
x-camara-min-icm-version := max(
  lowest Supported ICM version at release time,
  lowest ICM version containing all features this API's specification requires
)
```

For APIs that do not depend on ICM-version-specific constructs, the second operand is trivially zero; the rule collapses to "lowest Supported ICM version at release time." Publishing a new API version therefore always raises its floor to a Supported ICM major. An API Provider cannot declare a newly published API version as CAMARA compliant while offering only a Deprecated or Retired ICM major, even if the specification would technically work with those older versions.

Past API versions retain their published value; the floor is publication-time fixed even if the lowest Supported ICM version moves upward over time. Such declarations remain functionally valid within their original ICM major; cross-major compatibility is assessed by governance per §4.

### 7.3 Optional: declaring compatibility across multiple ICM major versions

An API specification MAY replace `x-camara-min-icm-version` with a richer declaration that expresses compatibility with more than one ICM major:

```yaml
info:
  x-camara-icm-compatibility:
    - 0.4.0
    - 1.0.0
    - ">=2.0.0"
```

Each entry is the floor within its ICM major, as a three-part semantic version optionally prefixed with `>=`. Entries assert that the API specification is ICM-compatible with any ICM version at or above the given floor within the same major. If the field is present, it supersedes `x-camara-min-icm-version` for compatibility computation.

Each entry MUST resolve to a Supported ICM version at the moment of publication, following the same anti-dodge rule as §7.2.

This field MAY be added to or extended in a **patch release** of the API: claiming compatibility with a newly Supported ICM major (for example, adding `>=2.0.0` after ICM 2.0 is published) is a compatibility claim, not an API-contract change, and does not require a minor or major API version bump.

**Note:** adopting this field has implications for other parts of this guideline — the core rule (§4), the validation rule (§7.4), and the compatibility computation (§12) all need to read and apply the multiple entries when this field is present. These adjustments are part of the same governance change that would adopt the field.

### 7.4 Validation

A CAMARA linting rule, run at API release time, reads the current ICM state (from the latest ICM release's notes) and verifies:
1. `x-camara-min-icm-version` is present.
2. Its value is a syntactically valid semver.
3. Its ICM major is in the Supported state at release time.
4. The value is ≥ the lowest Supported ICM version at release time (or the feature-dependency floor, whichever is higher).

## 8. API Provider responsibilities

An API specification might technically work against an ICM version that the compatibility matrix (§12) does not record as CAMARA-compliant — for example, a Retired or Revoked ICM version still running somewhere. Such pairings are outside CAMARA governance and cannot be claimed as CAMARA compliant. This section defines what an API Provider MUST do to claim CAMARA compliance for the APIs it offers.

CAMARA-compliant API Providers MUST:

1. Implement the ICM version currently holding the Preferred designation.
2. During the period in which a previous ICM major remains in the Supported state, also implement that major — supporting both API versions written against the Preferred-designated major and against the other Supported major.
3. Publish the ICM versions they implement, in a form that API Consumers can discover.
4. Publish **two separate compliance statements**:
   - **API-specification compliance**: for each API version offered, which API version specification is implemented.
   - **ICM-implementation compliance**: which ICM major versions the Provider implements.

These two statements together constitute the API Provider's CAMARA-compliance posture.

The mechanism by which an API Provider implements multiple ICM majors concurrently is an implementation choice and is not prescribed by this guideline; what matters is that each implemented ICM major version is discoverable and usable by API Consumers during the relevant period.

## 9. Aggregator role

Aggregators accept suppliers offering (API version, ICM version) pairs across a spectrum and present API Consumers with a narrower, consistent set of offerings — typically two or three API versions and one or two ICM majors, giving API Consumers time to migrate on both axes.

Aggregators operate as ecosystem normalizers:
- They MAY wrap or transform between ICM majors (for example, accepting ICM 2.x assertions from API Consumers while calling ICM 1.x suppliers, or vice versa).
- They MAY narrow the supplier pool to those operating at specific ICM majors they choose to offer.
- They MAY encourage convergence among their suppliers toward a common set of (API, ICM) pairs by aligning their commercial onboarding and support processes accordingly.

This guideline recognizes aggregators as a first-class actor in the CAMARA ecosystem. The matrix of (API version, ICM version) pairs across raw suppliers is a consequence of API and ICM versions evolving on independent cadences; aggregators handle matrix reduction for their API Consumers, and CAMARA governance provides the outer envelope within which both suppliers and aggregators operate.

## 10. API-side lifecycle cascade

ICM state transitions propagate to the API side according to this table:

| ICM governance event | API-side consequence |
|---|---|
| New Supported major designated Preferred (previous Preferred loses the designation, remains Supported) | No immediate action. Both majors remain in Supported; APIs continue to operate against both during the Supported-state availability period of the previous major. |
| Supported → Deprecated | API Sub Projects with APIs bound to this ICM major plan new API majors against the Preferred-designated ICM major. Original API majors bound to the Deprecated major SHOULD have a new-major replacement published before the Deprecated → Retired transition; they MAY be marked Deprecated at the API level as part of the migration. |
| Deprecated → Retired | API majors bound to the Retired ICM major MUST be Retired at the API level ([ReleaseManagement#459](https://github.com/camaraproject/ReleaseManagement/issues/459)). New API majors carry the ecosystem forward. |

For APIs whose specifications do not depend on ICM-version-specific constructs, the cascade does not require spec changes: the specification remains ICM-compatible with any not-Retired ICM major (subject to the per-boundary governance assessment in §4). When the originally-declared ICM major reaches Retired status, the API continues to operate against any still-active major that satisfies its `x-camara-min-icm-version` floor.

For APIs that do depend on ICM-version-specific constructs, the cascade acts as a forcing function: a new API major must be available before the bound ICM major is Retired.

Deprecation or Retirement of an ICM major does not by itself Deprecate or Retire API versions bound to it — only the corresponding cells in the compatibility matrix change. API version lifecycle (Deprecation, Retirement at the API level) is a separate governance concern that must be defined independently by CAMARA's API lifecycle process (see [ReleaseManagement#459](https://github.com/camaraproject/ReleaseManagement/issues/459)).

## 11. Release governance cadence

### 11.1 Signal / Sync alignment

ICM releases are announced primarily at Signal meta-releases (H1 each year); API releases primarily at Sync meta-releases (H2). This natural cadence provides lead time:

1. **Signal Year N**: ICM version published with state table. API Providers plan to move to the newer ICM version. API Sub Projects plan any new majors.
2. **Signal → Sync gap (~6 months)**: API Providers move their ICM implementation forward; API Sub Projects produce new API majors.
3. **Sync Year N**: new API majors land, declaring `minIcmVersion` in the newly Preferred-designated ICM major if they use new features.

### 11.2 Out-of-cycle ICM releases

Out-of-cycle ICM releases are permitted and sometimes required — e.g., for security patches, defect corrections, or urgent regulatory changes. These follow the same semver discipline. State transitions may occur off-cycle in security-driven cases, with explicit governance record.

### 11.3 Signal is not a gate

Signal timing is an announcement and coordination anchor, not a mandatory gate. ICM versions MAY be introduced outside Signal when necessary. API versions MAY be released outside Sync. Governance focuses on content discipline (semver correctness, state assignments) rather than calendar alignment.

## 12. Compatibility matrix as derived artifact

The API–ICM compatibility matrix is maintained as a **derived artifact**, computed automatically from:
- API version declarations (`x-camara-min-icm-version` in each published API spec, or `x-camara-icm-compatibility` if §7.3 is adopted).
- ICM state per published ICM version (from the latest ICM release notes), including any per-version overrides.
- Exception waivers (if any).
- Governance decisions extending an API specification's ICM-compatibility across an ICM major boundary (per §4).

The matrix lists one row per published API version and one column per published ICM version. It records which (API version, ICM version) pairs are CAMARA-compliant.

### 12.1 Compatibility computation

```
compatible(API vX, ICM version vY) :=
  vY's major == API vX's minIcmVersion's major
  AND vY >= API vX's minIcmVersion
  AND vY is in state {Supported, Deprecated}
  OR a governance decision extends the API's ICM-compatibility to vY's major
  OR an approved, time-bound compatibility waiver exists
```

The state condition applies to the specific ICM version `vY`, inheriting from its major unless a per-version override is in place. Versions in the Retired or Revoked state are excluded from all positive compatibility cells (waivers aside).

Cells that are "compatible" represent legitimate (API, ICM) pairs that API Providers may offer and API Consumers may consume.

### 12.2 Ownership

The matrix is published by Release Management. It is computed, not hand-edited. Only exception waivers require human governance action.

### 12.3 Scope

Matrix update triggers are:
- New ICM release (state may change).
- New API release (new row added; old rows unchanged).
- Exception granted, modified, or expired.

## 13. Legacy ICM 0.x handling

This guideline's semver-based rules take effect with ICM 1.0.0. Pre-1.0 ICM versions pre-date the commitment. For the transition period, Release Management publishes a one-time historical record documenting which ICM 0.x transitions were client-facing-breaking:

| ICM transition | Client-facing forward break? | Source PRs |
|---|---|---|
| 0.2.0 → 0.3.0 | Yes — client-assertion lifetime cap | [#216](https://github.com/camaraproject/IdentityAndConsentManagement/pull/216) |
| 0.3.0 → 0.4.0 | Yes — mandatory signed-request fields; error-code rename | [#285](https://github.com/camaraproject/IdentityAndConsentManagement/pull/285), [#287](https://github.com/camaraproject/IdentityAndConsentManagement/pull/287) |
| 0.4.0 → 0.5.0 | No — additive | — |

State for 0.x versions is assigned by ICM governance as a one-time exercise. The full semver discipline does not apply retroactively — 0.x versions were permitted to break by virtue of pre-1.0 status.

## 14. Exception mechanism

Exceptions are time-bound compatibility waivers granted by governance:

- **Scope**: specific (API version, ICM version) pair, or a range.
- **Justification**: required — operational necessity, regulatory requirement, or security consideration.
- **Time bound**: explicit expiry date or condition.
- **Owner**: named API Sub Project or provider responsible for remediation by expiry.
- **Expiry**: automatic. No "ongoing exception" mechanism.

Exceptions are the only mechanism by which a (API, ICM) pair can be deemed compatible despite violating the core rules in §4 and §6. They appear in the compatibility matrix with explicit annotation.

## 15. Open governance decisions

The following require WG agreement before this guideline is adopted:

1. **Exact durations** for the Supported and Deprecated state durations (§6.2).
2. **Transition to ICM 1.0.0** — what constitutes the scope baseline; when it is declared; who signs off.
3. **Signal vs. out-of-cycle policy** — which ICM changes can be out-of-cycle vs. must align with Signal.
4. **Exception grant process** — who requests, who approves, how documented.
5. **CAMARA-compliance statement content** — exact templates for API-specification compliance and ICM-implementation compliance; audit process.
6. **Interaction with GSMA certification** — does this decomposition map onto GSMA's processes; alignment discussion required.
7. **Handling of the ICM 0.x transition** — state assignments for existing 0.x versions; end date for 0.x support.
8. **Adoption of §7.3** — whether to introduce the optional `x-camara-icm-compatibility` field for cross-major compatibility, and the corresponding adjustments to §4, §7.4, and §12 that this would entail.
9. **Maximum number of concurrent non-Retired ICM majors** — whether to cap this to bound Provider operational complexity when ICM majors arrive in quick succession (for example, in a security-driven scenario), and how Retirement acceleration would be triggered if the cap is exceeded.

---

## Appendix A: Key positions

- **Meta-release is not the unit of compatibility.** Individual (API, ICM) pairs are, constrained by governance states and by the per-major binding rule in §4.
- **`x-camara-min-icm-version`** is introduced as an OpenAPI extension carried by each API specification, independent of `x-camara-commonalities`.
- **API Provider compliance is decomposed** into API-specification compliance and ICM-implementation compliance (§8).
- **The compatibility matrix is automated**, not hand-maintained.
- **Signal/Sync cadence is a lead-time mechanism**, not a governance gate.

## Appendix B: What this guideline intentionally does not do

- Does not define a detailed state-machine with per-minor-version state assignments. States are per-major.
- Does not require any `x-camara-icm` structured block with multiple fields. A single flat string suffices.
- Does not introduce a "re-release without `info.version` change" mechanism. `minIcmVersion` is publication-time fixed.
- Does not mandate that ICM majors align with Signal meta-releases. Strongly suggested, not required.
- Does not prescribe the implementation mechanism by which an API Provider serves multiple ICM majors. Only behavioral requirements apply.
