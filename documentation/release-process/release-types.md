# Release Types

This document explains the available release types and their intended use.

---

## Overview

CAMARA defines five release types (including `none`), each serving a different purpose in the API lifecycle:

| Release type | Purpose | When to use |
|--------------|---------|-------------|
| `none` | Not ready | No release planned, or repository not yet releasable |
| `pre-release-alpha` | Early feedback | Initial implementation ready for review |
| `pre-release-rc` | Release candidate | Feature-complete, ready for testing |
| `public-release` | Public release | Production-ready, meets all quality gates |
| `maintenance-release` | Patch release | Bug fixes to an existing public release |

The release type is declared in `release-plan.yaml` via the `target_release_type` field.

---

## API status progression

Before discussing release types, it's important to understand how APIs progress through maturity levels:

```
draft → alpha → rc → public
```

| Status | Meaning | Can be released? |
|--------|---------|------------------|
| `draft` | Declared but implementation in progress | No — development only |
| `alpha` | Early implementation ready for feedback | Yes — in alpha or RC releases |
| `rc` | Feature-complete, ready for testing | Yes — in RC or public releases |
| `public` | Production-ready | Yes — in public or maintenance releases |

The `draft` status is special: it allows APIs to be declared in `release-plan.yaml` while still under development. APIs at `draft` status cannot be released—they must reach at least `alpha` before inclusion in any release.

---

## Pre-release vs public release

### Pre-releases

Pre-releases are **work-in-progress** releases intended for feedback and testing:

- They are publicly available in the CAMARA GitHub
- They are **not** included in meta-releases
- They may change without notice
- They should be used **at the user's own risk**

There are two pre-release types:

#### Alpha (`pre-release-alpha`)

- First release of a new API version for early feedback
- Implementation may be incomplete
- API surface may still change
- All APIs must be at `alpha` status or higher

**Typical use:** After initial development is complete enough for external review.

#### Release candidate (`pre-release-rc`)

- Feature-complete implementation
- Ready for integration testing
- API surface should be stable (changes only for bug fixes)
- All APIs must be at `rc` or `public` status

**Typical use:** When approaching a milestone (e.g., M3 for meta-releases) and the API is ready for broader testing.

### Public releases

Public releases are **production-ready** releases where all APIs are at `public` status. There are two categories:

#### Initial public API versions (`0.y.z`)

Initial public API versions represent APIs in early production use:

- API version number starts with `0` (e.g., `0.1.0`, `0.5.0`)
- Can be released **outside** the meta-release process for rapid iteration
- Can also participate in meta-releases if desired
- Breaking changes may still occur in subsequent API versions
- Fewer readiness checklist requirements than stable API versions

**Typical use:** First production-ready release of a new API, when rapid evolution is still expected.

#### Stable public API versions (`x.y.z` where `x >= 1`)

Stable public API versions represent mature, production-grade APIs:

- API version number starts with `1` or higher (e.g., `1.0.0`, `2.1.0`)
- **Must** participate in the meta-release process
- Backward compatibility is expected for subsequent minor/patch API versions
- Full readiness checklist requirements apply
- Recommended for commercial applications

**Typical use:** When the API has proven itself and users need stability guarantees.

#### Initial vs stable comparison

| Aspect | Initial (`0.y.z`) | Stable (`x.y.z`, x≥1) |
|--------|-------------------|----------------------|
| Meta-release participation | Optional | Mandatory |
| Backward compatibility expectation | Not guaranteed | Expected |
| Readiness checklist | Partial requirements | Full requirements |
| Breaking changes | May occur | Only in major API versions |
| Commercial use recommendation | Use with caution | Recommended |

---

## Maintenance releases

Maintenance releases provide **patch updates** to existing public releases:

- They contain only bug fixes, not new features
- They are released from a maintenance branch, not `main`
- They increment the patch API version (e.g., `1.0.0` → `1.0.1`)
- All APIs must be at `public` status

**Typical use:** Critical bug fix or security patch for a released API version.

### When to use maintenance releases

| Scenario | Use maintenance release? |
|----------|-------------------------|
| Critical bug in production API | Yes |
| Security vulnerability | Yes |
| Minor enhancement | No — use next regular release |
| New feature | No — use next regular release |
| Alignment with new Commonalities (patch-level) | Yes |

### Maintenance vs regular releases

| Aspect | Regular release | Maintenance release |
|--------|-----------------|---------------------|
| Source branch | `main` | `maintenance-rX` |
| API version change | Any (major, minor, patch) | Patch only |
| New features | Allowed | Not allowed |
| Release numbering | Continues from last meta-release | Continues from patched release |

---

## How release type constrains readiness

The declared `target_release_type` determines what API statuses are allowed:

| Release type | Minimum API status | Allowed statuses |
|--------------|-------------------|------------------|
| `pre-release-alpha` | `alpha` | `alpha`, `rc`, `public` |
| `pre-release-rc` | `rc` | `rc`, `public` |
| `public-release` | `public` | `public` only |
| `maintenance-release` | `public` | `public` only |

### What this means in practice

**For `pre-release-alpha`:**
- You can have a mix of `alpha`, `rc`, and `public` APIs
- At least one API should be at `alpha` (otherwise, why not RC?)
- Unchanged APIs from a previous public release may remain `public`

**For `pre-release-rc`:**
- All APIs must be at least `rc`
- APIs still under development must reach `rc` status
- Unchanged public APIs may remain `public`

**For `public-release`:**
- Every API must be `public`
- No pre-release APIs allowed
- This is the gate for meta-release inclusion

**For `maintenance-release`:**
- Every API must be `public`
- Only patch-level API version changes
- Must be released from a maintenance branch

---

## Progression through release types

A typical progression for a new API version:

```
Development (wip)
       │
       ▼
pre-release-alpha  ──► r4.1 (0.5.0-alpha.1)
       │
       ▼
pre-release-alpha  ──► r4.2 (0.5.0-alpha.2)  [optional additional alphas]
       │
       ▼
pre-release-rc     ──► r4.3 (0.5.0-rc.1)
       │
       ▼
pre-release-rc     ──► r4.4 (0.5.0-rc.2)     [optional additional RCs]
       │
       ▼
public-release     ──► r4.5 (0.5.0)
       │
       ▼
maintenance-release ──► r4.6 (0.5.1)         [if patch needed]
```

Each step requires meeting the constraints for that release type.

---

## Choosing the right release type

| Question | If yes... |
|----------|-----------|
| Is this the first implementation for feedback? | Use `pre-release-alpha` |
| Is the API feature-complete and ready for testing? | Use `pre-release-rc` |
| Is this a new API ready for initial production use? | Use `public-release` with initial API version (`0.y.z`) |
| Is this a mature API ready for stable production use? | Use `public-release` with stable API version (`x.y.z`, x≥1) |
| Is this a bug fix to an existing public release? | Use `maintenance-release` |

---

## Common questions

**Can I skip alpha and go straight to RC?**
Yes. If your API is already feature-complete and tested, you can release directly as `pre-release-rc`.

**Can I have multiple APIs at different statuses?**
Yes, for pre-releases. A repository can contain APIs at `alpha`, `rc`, and `public` in the same `pre-release-alpha` or `pre-release-rc` release. For public releases, all APIs must be `public`.

**What if I need to fix a bug during RC phase?**
Create additional RC releases (e.g., `rc.2`, `rc.3`). Each increments the release number but keeps the same base API version.

**When does a maintenance branch get created?**
After a public release, if patch updates are needed. The maintenance branch is created from the commit that was released.

**When should I move from initial API version (`0.y.z`) to stable (`1.0.0`)?**
When the API has proven itself in production, the interface is mature, and you're ready to commit to backward compatibility. Moving to `1.0.0` signals to users that the API is stable and suitable for commercial applications. This transition requires participating in the meta-release process.

**Can an initial public API version be part of a meta-release?**
Yes. Initial API versions can optionally participate in meta-releases. However, stable API versions (`x.y.z` with x≥1) must always go through the meta-release process.

---

## See also

- [../README.md](../README.md) for documentation index
