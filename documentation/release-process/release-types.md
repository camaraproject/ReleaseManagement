# Release Types

This page describes release types and constraints. Guidance on how to release is in [lifecycle.md](lifecycle.md).

## Release Types

| Type | Purpose | Required API Status |
|------|---------|---------------------|
| `pre-release-alpha` | Early feedback | `alpha` or higher |
| `pre-release-rc` | Release candidate | `rc` or higher |
| `public-release` | Production-ready | `public` only |
| `maintenance-release` | Patch release | `public` only |

## API Status Levels

| Status | Meaning | Releasable? |
|--------|---------|-------------|
| `draft` | Declared, not implemented | No |
| `alpha` | Early implementation | Yes (alpha+) |
| `rc` | Feature-complete | Yes (rc+) |
| `public` | Production-ready | Yes |

## Public Release Variants

| Variant | API Version | Meta-release | Breaking Changes |
|---------|-------------|--------------|------------------|
| Initial | `0.y.z` | Optional | May occur |
| Stable | `x.y.z` (x≥1) | Required | Major versions only |

## Maintenance Releases

Maintenance releases provide patches to existing public releases:

- Bug fixes and security patches only
- Based on a maintenance branch (`maintenance-rX`)
- Patch version increment only (e.g., `1.0.0` → `1.0.1`)

→ [Maintenance release details](maintenance-releases.md)
