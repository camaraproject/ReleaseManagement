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

## Key Differences in the Process

Compared to a regular release:

- Development and fixes are done on a maintenance branch (`maintenance-rX`) rather than `main`
- The release is declared with `target_release_type: maintenance-release`
- Only patch versions are produced (e.g., `1.0.0` → `1.0.1`)


→ [Full release process](lifecycle.md)
