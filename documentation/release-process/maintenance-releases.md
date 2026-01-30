# Maintenance Releases

Maintenance releases provide patches to existing public releases.

## When to Use

| Use maintenance release | Don't use |
|------------------------|-----------|
| Critical bug fix | New features |
| Security vulnerability | Enhancements |
| Commonalities alignment (patch) | Breaking changes |

## How They Differ

| Aspect | Regular Release | Maintenance Release |
|--------|-----------------|---------------------|
| Source branch | `main` | `maintenance-rX` |
| Version change | Any | Patch only |
| Release type | Any | `maintenance-release` |

## Process

The release process is identical to regular releases, but:

1. Work on the `maintenance-rX` branch instead of `main`
2. Set `target_release_type: maintenance-release` in `release-plan.yaml`
3. Increment patch version only (e.g., `1.0.0` → `1.0.1`)

→ [Full release process](lifecycle.md)
