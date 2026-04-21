# ICM Lifecycle and API Compatibility Governance

**Version:** Draft 1 (2026-04-21)
**Status:** Draft for Release Management WG discussion.
**Scope:** Response to the ICM WG request to Release Management (per [ICM#324](https://github.com/camaraproject/IdentityAndConsentManagement/issues/324), [ICM#340](https://github.com/camaraproject/IdentityAndConsentManagement/issues/340), [ReleaseManagement#351](https://github.com/camaraproject/ReleaseManagement/issues/351)) to define governance for ICM version evolution and its dependencies with CAMARA API versions.

---

## 1. Scope and Purpose

This guideline defines how Identity and Consent Management (ICM) evolves as an independent Working Group and how CAMARA APIs declare and maintain compatibility with ICM versions. It answers the question posed by the ICM Working Group to Release Management: under what rules can API versions and ICM versions co-evolve while still providing clear compatibility guarantees to API Consumers, aggregators, and certification authorities?

The guideline recognizes operational reality: providers offer the same API version against multiple ICM versions, aggregators depend on this flexibility, and API Consumers combine an API version and an ICM version into a single usage contract — if either side changes in a way that affects them, their integration must adapt.

## 2. Glossary

Terms defined in the CAMARA Commonalities glossary (API, API Consumer, API Provider, meta-release, semantic versioning, scope, etc.) are not repeated here. This section defines terms specific to this guideline.

- **ICM↔API contract**: the set of ICM-defined rules that shape how APIs are specified — scope format, `securitySchemes` syntax, sub claim format, token structure assumed by the API. Distinct from the contract between API Consumer and API (operations, schemas) and the contract between API Consumer and Authorization Server (flows, grants, assertions).
- **Orthogonal API**: an API whose specification is not affected by differences between ICM major versions — its `securitySchemes`, scopes, and operational semantics are valid under any ICM major currently in the Supported tier. The majority of current CAMARA APIs are orthogonal.
- **ICM major version**: the major component of an ICM semantic version (e.g., "1.x"). Starting with ICM 1.0.0, major-version increments indicate client-facing changes that cannot be expressed additively.
- **Supported / Deprecated / Retired**: the three lifecycle tiers for an ICM major version (see §6).
- **Preferred**: a designation — not a tier — applied to exactly one Supported ICM major at a time, identifying it as the current baseline for new API development (see §6).
- **Overlap window**: the period during which a previous ICM major remains in the Supported tier after the Preferred designation has moved to a newer major.
- **Exception (waiver)**: a time-bound, governance-approved compatibility authorization that permits a specific (API version, ICM version) pair outside the normal rules.
- **Compatibility matrix**: the derived artifact listing which (API version, ICM version) pairs are compatible at a given point in time (see §12).

## 3. The three contracts

Three distinct contracts determine how CAMARA APIs and ICM interact. Each evolves on its own cadence and is owned by a different actor.

| Contract | Between | Content | Owner |
|---|---|---|---|
| **API Consumer ↔ API** | API Consumer and the API | Operations, request/response schemas, required scopes by name, error codes | API Sub Project |
| **API Consumer ↔ AS** | API Consumer and Authorization Server | Flows, grant types, assertion format, claim rules, signed-request requirements | ICM Working Group |
| **ICM ↔ API** | AS behavior and API specification | Scope format, `securitySchemes` syntax, sub claim format, token shape the API may rely on | ICM defines; APIs follow |

These three contracts are largely independent:

- An API spec change that does not alter its scope format or `securitySchemes` declarations does not affect contracts 2 or 3.
- An ICM change to flow mechanics (e.g., tightening assertion lifetime) affects contract 2 only — the API is unaffected.
- An ICM change to scope format or `securitySchemes` syntax affects contract 3; API specs written against the prior syntax remain valid against AS implementations that honor that prior syntax, but cannot be published as new specs once the syntax has changed.

**From the API Consumer's perspective, the combined contract is what matters**: they integrate against both a specific API version and a specific ICM version. A change in either side that affects them requires their integration to adapt. The independence of the three contracts is analytical — useful for governance — but does not relieve the API Consumer of having to manage the pair.

## 4. Core rule

**An API version is bound to the ICM major version whose ICM↔API contract it was written against.**

For APIs whose contract is not affected by differences between ICM majors — *orthogonal APIs*, which make up the large majority of current CAMARA APIs — the binding has no operational effect: such an API remains compatible with any ICM major currently in the Supported tier.

For APIs whose ICM↔API contract IS affected (e.g., an API that uses a specific scope format introduced in an ICM major, or relies on an operator-token mechanism), the binding is explicit and operational: the API can only be served by AS implementations that honor its ICM major's contract.

Concretely: `x-camara-min-icm-version: 1.2.0` declared in an API spec means the API was written against the ICM 1.x ICM↔API contract and requires features introduced from ICM version 1.2.0 onward within that major.

## 5. Prerequisite: ICM semver commitment at 1.0.0

This guideline assumes ICM adopts strict semver starting with its 1.0.0 release:

- **Minor versions (1.x → 1.y)**: additive only. No client-facing change to any of the three contracts. New flows, new claims, new recommendations permitted. Removals, replacements, and tightenings that reject previously-legal behavior are not permitted within a major.
- **Major versions (1.x → 2.0)**: reserved for client-facing changes that cannot be expressed additively — e.g., replacement of a mandatory security schema with a new one, an incompatible scope format, removal of a required claim. Majors should be deliberately rare and driven by security or regulatory necessity.
- **Patch versions (1.2.3 → 1.2.4)**: editorial or defect corrections with no contract impact.

The transition to 1.0.0 should coincide with a scope-baseline review of the ICM documents, declaring the then-current definitions as the stable starting point. Pre-1.0 versions are handled by the Legacy section (§13).

## 6. ICM lifecycle governance

### 6.1 Tier model

Each ICM major version moves through three lifecycle tiers:

| Tier | Meaning |
|---|---|
| **Supported** | Active; APIs may declare and operate against this major |
| **Deprecated** | Sunset announced; migration window active; no new APIs should declare this major |
| **Retired** | Terminal; APIs bound to a Retired major are no longer CAMARA-compliant and must transition or be Retired at the API level |

Tier transitions follow the sequence Supported → Deprecated → Retired. A new ICM major enters the Supported tier at its public release.

**Preferred** is not a lifecycle tier but a designation applied to exactly one Supported ICM major at a time, identifying it as the current baseline for new API development. The Preferred designation is assigned by governance and MAY be reassigned to a newer Supported major at its public release or at a later governance decision. Reassignment of the Preferred designation is an explicit governance action, not automatic. A major that loses the Preferred designation remains in the Supported tier until governance moves it to Deprecated.

Tiers primarily apply to ICM major versions. Governance MAY additionally mark specific minor versions within a major as Deprecated when they should no longer be used as a floor (for example, when known ambiguities or defects are resolved in later minors). Such sub-major deprecations do not introduce incompatibility — later minors remain compatible with earlier ones by semver — but they influence the "lowest Supported minor" used in §7.2.

The term "Retired" aligns with the API lifecycle terminology proposed in [ReleaseManagement#459](https://github.com/camaraproject/ReleaseManagement/issues/459), so that ICM and API lifecycles use the same vocabulary for the terminal state.

### 6.2 Governance parameters

| Parameter | Suggested starting value | Notes |
|---|---|---|
| Supported duration (overlap window) | ≥ 18 months | Time a major remains Supported after losing the Preferred designation before it enters Deprecated; providers plan AS upgrades during this period |
| Deprecated duration | ≥ 12 months | Active migration period before the major is Retired |
| Concurrent support requirement | Major holding the Preferred designation + most recent other Supported major | Applies to CAMARA-compliant providers during the overlap window |
| Security kill-switch | Conditions permitting acceleration of any tier transition | Explicit governance action per incident; see §14 |

These values are starting points for WG discussion. With the suggested minimums, an ICM major's lifetime in the Supported tier after losing the Preferred designation is at least ~18 months, followed by ≥12 months in Deprecated before it is Retired. The duration during which a major holds the Preferred designation is a separate governance decision, typically set by when the next major is ready for introduction.

### 6.3 Publication of tier state

Tier state is published in each ICM release's notes, as a standard table in the release notes template. No separate governance artifact is required — each ICM release carries the current tier state for all active ICM majors. Between ICM releases, the tier state from the latest release is authoritative. Tier transitions are committed at ICM release time unless an out-of-cycle governance action specifies otherwise.

A machine-readable YAML file published alongside the release notes supports automated tooling. Suggested structure:

```yaml
icmLifecycle:
  publishedAt: "2026-03-15T10:00:00Z"
  publishedBy: "CAMARA ICM Working Group"
  majors:
    - major: 1
      tier: Supported
      preferred: true
      since: "2026-03-01"
      lowestSupportedMinor: "1.0.0"
    - major: 0
      tier: Supported
      preferred: false
      since: "2026-03-01"
      lowestSupportedMinor: "0.5.0"
      plannedTransition:
        toTier: Deprecated
        notBefore: "2027-09-01"
```

The YAML is advisory; the authoritative source remains the ICM release notes. The exact schema is an open governance decision (§15).

## 7. API spec declaration: `x-camara-min-icm-version`

### 7.1 Declaration

Every CAMARA API specification declares a single top-level extension field:

```yaml
info:
  x-camara-min-icm-version: 1.2.0
```

- Three-part semantic version matching the ICM release versioning scheme.
- Names the lowest ICM version against which this API's ICM↔API contract is satisfied.
- Implicitly names the ICM major: `1.2.0` binds the API to the ICM 1.x contract.
- Publication-time fixed. Does not change after the API version is released.

### 7.2 Rule for choosing the value at release

At each API release (new major, minor, or patch), the API Sub Project sets the value as:

```
x-camara-min-icm-version := max(
  lowest "Supported" tier ICM version at release time,
  lowest ICM version containing all features this API's contract requires
)
```

For orthogonal APIs the second operand is trivially zero; the rule collapses to "lowest fully Supported ICM version at release time." This maximizes the supplier set without requiring ICM infrastructure upgrades to publish new API versions.

Past API versions retain their published value; the floor is publication-time fixed even if the lowest Supported ICM version moves upward over time. Such "stale" declarations remain functionally valid because the lower bound is still ≤ any Supported ICM version — the API is compatible with any currently-Supported ICM version that also satisfies its feature dependencies.

### 7.3 No structured block

This guideline does not define a structured `x-camara-icm` block with additional fields (supported access profiles, consent models, etc.). Virtually all CAMARA APIs need only the flat minimum-version declaration.

If specific APIs require additional ICM dependency declarations — for example, NumberVerification's dependency on operator tokens — they may propose per-API extensions in their repositories. Centralized definition of such fields in this guideline is premature.

### 7.4 Validation

A CAMARA linting rule, run at API release time, fetches the current ICM tier state (from the latest ICM release's notes) and verifies:
1. `x-camara-min-icm-version` is present.
2. Its value is a syntactically valid semver.
3. Its ICM major is in the Supported tier at release time.
4. The value is ≥ the lowest Supported ICM version at release time (or the feature-dependency floor, whichever is higher).

## 8. Provider responsibilities

CAMARA-compliant providers MUST:

1. Run AS implementations that honor the ICM major currently holding the Preferred designation.
2. During the overlap window, also run AS implementations honoring the other Supported ICM major — supporting both API versions written against the Preferred-designated major and against the other Supported major.
3. Advertise supported ICM majors via AS metadata (OIDC discovery document or equivalent).
4. Publish **two separate compliance statements**:
   - **API-spec compliance**: for each API version offered, which API version specification is implemented.
   - **AS compliance**: for each ICM major supported, at what strictness level, served at which endpoint.

These two statements together constitute the provider's "CAMARA Compliant" posture. They are not bundled by meta-release.

The typical deployment pattern is a **multi-endpoint Authorization Server**: separate endpoints (separate issuers, separate metadata documents) for each supported ICM major. Clients discover and select via metadata. Providers MAY use alternative implementations — a single AS that natively honors multiple majors is equally valid — provided the compliance statements accurately describe the behavior.

## 9. Aggregator role

Aggregators accept suppliers offering (API version, ICM version) pairs across a spectrum and present API Consumers with a narrower, consistent set of offerings — typically one API version and one or two ICM majors.

Aggregators operate as ecosystem normalizers:
- They MAY wrap or transform between ICM majors (for example, accepting ICM 2.x assertions from API Consumers while calling ICM 1.x suppliers, or vice versa).
- They MAY narrow the supplier pool to those operating at specific ICM majors they choose to offer.
- They MAY encourage convergence among their suppliers toward a common set of (API, ICM) pairs by aligning their commercial onboarding and support processes accordingly.

This guideline recognizes aggregators as a first-class actor in the CAMARA ecosystem. The N×M matrix across raw suppliers is a consequence of the three-contract independence; aggregators handle matrix reduction for their API Consumers, and CAMARA governance provides the outer envelope within which both suppliers and aggregators operate.

## 10. API-side lifecycle cascade

ICM tier transitions propagate to the API side according to this table:

| ICM governance event | API-side consequence |
|---|---|
| New Supported major designated Preferred (previous Preferred loses the designation, remains Supported) | No immediate action. Both majors remain in Supported; APIs continue to operate against both during the overlap window. |
| Supported → Deprecated | API Sub Projects with APIs bound to this ICM major plan new API majors against the Preferred-designated ICM major. Original API majors bound to the Deprecated major SHOULD have a new-major replacement published before the Deprecated → Retired transition; they MAY be marked Deprecated at the API level as part of the migration. |
| Deprecated → Retired | API majors bound to the Retired ICM major MUST be Retired at the API level ([ReleaseManagement#459](https://github.com/camaraproject/ReleaseManagement/issues/459)). New API majors carry the ecosystem forward. |

For **orthogonal** APIs (majority), the cascade does not require spec changes: the API spec remains valid against any Supported ICM major, and when its originally-declared ICM major reaches Retired status, the API continues to operate against any still-active major that satisfies its `x-camara-min-icm-version` floor. The floor declaration becomes formally stale but functionally harmless.

For APIs with genuine ICM-major binding (minority), the cascade acts as a forcing function: a new API major must be available before the bound ICM major is Retired.

## 11. Release governance cadence

### 11.1 Signal / Sync alignment

ICM releases are announced primarily at Signal meta-releases (H1 each year); API releases primarily at Sync meta-releases (H2). This natural cadence provides lead time:

1. **Signal Year N**: ICM version published with tier table. Providers plan AS upgrades. API Sub Projects plan any new majors.
2. **Signal → Sync gap (~6 months)**: providers upgrade AS; API Sub Projects produce new API majors.
3. **Sync Year N**: new API majors land, declaring `minIcmVersion` in the newly Preferred-designated ICM major if they use new features.

### 11.2 Out-of-cycle ICM releases

Out-of-cycle ICM releases are permitted and sometimes required — e.g., for security patches, defect corrections, or urgent regulatory changes. These follow the same semver discipline. Tier state may transition off-cycle in security-driven cases, with explicit governance record.

### 11.3 Signal is not a gate

Signal timing is an announcement and coordination anchor, not a mandatory gate. ICM versions MAY be introduced outside Signal when necessary. API versions MAY be released outside Sync. Governance focuses on content discipline (semver correctness, tier assignments) rather than calendar alignment.

## 12. Compatibility matrix as derived artifact

The API–ICM compatibility matrix is maintained as a **derived artifact**, computed automatically from:
- API version declarations (`x-camara-min-icm-version` in each published API spec).
- ICM tier state (from the latest ICM release notes).
- Exception waivers (if any).

### 12.1 Compatibility computation

```
compatible(API vX, ICM version vY) :=
  vY's major == API vX's minIcmVersion's major
  AND vY >= API vX's minIcmVersion
  AND vY's major is in tier {Supported, Deprecated}
  OR an approved, time-bound compatibility waiver exists
```

Cells that are "compatible" represent legitimate (API, ICM) pairs that providers may offer and API Consumers may consume.

### 12.2 Ownership

The matrix is published by Release Management. It is computed, not hand-edited. Only exception waivers require human governance action.

### 12.3 Scope

Matrix update triggers are:
- New ICM release (tier state may change).
- New API release (new row added; old rows unchanged).
- Exception granted, modified, or expired.

## 13. Legacy ICM 0.x handling

This guideline's semver-based rules take effect with ICM 1.0.0. Pre-1.0 ICM versions pre-date the commitment. For the transition period, Release Management publishes a one-time historical record documenting which ICM 0.x transitions were client-facing-breaking:

| ICM transition | Client-facing forward break? | Source PRs |
|---|---|---|
| 0.2.0 → 0.3.0 | Yes — client-assertion lifetime cap | [#216](https://github.com/camaraproject/IdentityAndConsentManagement/pull/216) |
| 0.3.0 → 0.4.0 | Yes — mandatory signed-request fields; error-code rename | [#285](https://github.com/camaraproject/IdentityAndConsentManagement/pull/285), [#287](https://github.com/camaraproject/IdentityAndConsentManagement/pull/287) |
| 0.4.0 → 0.5.0 | No — additive | — |

Tier state for 0.x versions is assigned by ICM governance as a one-time exercise. The full semver discipline does not apply retroactively — 0.x versions were permitted to break by virtue of pre-1.0 status.

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

1. **Exact durations** for the Supported and Deprecated tier windows (§6.2).
2. **Transition to ICM 1.0.0** — what constitutes the scope baseline; when it is declared; who signs off.
3. **Signal vs. out-of-cycle policy** — which ICM changes can be out-of-cycle vs. must align with Signal.
4. **Exception grant process** — who requests, who approves, how documented.
5. **CAMARA-compliance statement content** — exact templates for API-spec and AS compliance; audit process.
6. **Interaction with GSMA certification** — does this decomposition map onto GSMA's processes; alignment discussion required.
7. **Handling of the ICM 0.x transition** — tier assignments for existing 0.x versions; end date for 0.x support.

---

## Appendix A: What this guideline changes relative to the current state

- **ICM#324's "strict bundling" conclusion is withdrawn.** Replaced with the per-major binding rule in §4.
- **Meta-release is no longer the unit of compatibility.** Individual (API, ICM) pairs are, constrained by governance tiers.
- **`x-camara-min-icm-version` is introduced as an OpenAPI extension.** Replaces implicit assumption that `x-camara-commonalities` defines the corresponding ICM version.
- **Provider compliance is decomposed** into API-spec and AS components.
- **Compatibility matrix is automated**, not hand-maintained.
- **Signal/Sync cadence is recognized as lead-time mechanism**, not a governance gate.

## Appendix B: What this guideline intentionally does not do

- Does not define a detailed state-machine lifecycle with per-minor-version tier assignments. Tiers are per-major.
- Does not require any `x-camara-icm` structured block with multiple fields. Single flat string.
- Does not introduce a "re-release without `info.version` change" mechanism. `minIcmVersion` is publication-time fixed.
- Does not mandate that ICM majors align with Signal meta-releases. Strongly suggested, not required.
- Does not prescribe technology choices for AS implementation (single vs. multi-endpoint, specific OAuth libraries, etc.). Only behavioral requirements.
- Does not attempt to unify the Client↔AS and ICM↔API contracts. They are treated as distinct throughout.
