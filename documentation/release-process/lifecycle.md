# Releasing an API Repository

This guide walks you through releasing an API repository in CAMARA.

## Quick Process Overview

- [ ] Update `release-plan.yaml`
- [ ] Ensure all intended changes are merged to `main`
- [ ] APIs meet their declared target statuses (Checks on `main` should be green)
- [ ] `/create-snapshot` in Release Issue
- [ ] Review, approve and merge Release PR
- [ ] `/publish-release` → Done

## The Release Process

### 1. Plan Your Release

**What you do:**
- Update `release-plan.yaml` on `main` with your release intentions
- Set `target_release_tag`, `target_release_type`, and API statuses

**What you see:**
- CI validates every PR on `release-plan.yaml`
- Release Issue appears with PLANNED state

→ [release-plan.yaml reference](../metadata/release-plan.md)

---

### 2. Develop on `main`

This phase is ongoing until you decide to release.

**What you do:**
- Develop API specifications toward your planned release
- Keep version fields set to `wip`
- Respond to CI validation feedback

**What you see:**
- CI will validate every PR on `main` against the plan 

**What can block you:**
- Validation errors → fix and re-push

---

### 3. Create the Release

**What you do:**
1. Go to the automatically created Release Issue for your target release (rX.Y)
2. Post `/create-snapshot` as a comment

**What you see:**
- Automation validates your repository
- If successful: Release PR created, issue shows "SNAPSHOT ACTIVE"
- If failed: Error message with what to fix

**What can block you:**
- Validation errors → fix on `main`, then `/create-snapshot` again
- Dependency not published → wait or update `release-plan.yaml`

---

### 4. Review and Approve

**What you do:**
1. Review the Release PR (CHANGELOG)
2. Refine documentation if needed
3. Ensure required approvals are in place (codeowner and release reviewer)
4. Merge the Release PR

**What you see:**
- After merge: Draft release created, issue shows "DRAFT READY"

**What can block you:**
- Issue found in API specification:
  1. Post `/discard-snapshot <reason>` on the Release Issue
  2. Fix the issue on `main`
  3. Post `/create-snapshot` to start fresh

---

### 5. Publish

**What you do:**
1. Review the draft release in GitHub Releases
2. Post `/publish-release --confirm rX.Y` on the Release Issue (with your release tag)

> **Tip:** If you forget `--confirm`, automation shows a confirmation message with the exact command to copy.

**What you see:**
- Release tag `rX.Y` created
- Post-release sync PR created (merge it to update `main`)
- Release Issue closed

**What can block you:**
- Issue found in draft:
  1. Post `/delete-draft <reason>` on the Release Issue
  2. Fix the issue on `main`
  3. Post `/create-snapshot` to start fresh

---

## Quick Reference

This section is a summary only. For explanations, see the sections above.

| Command | When to use | Effect |
|---------|-------------|--------|
| `/create-snapshot` | Ready to release | Creates Release PR |
| `/discard-snapshot <reason>` | Problem found during review | Returns to start |
| `/delete-draft <reason>` | Problem found in draft | Returns to start |
| `/publish-release --confirm rX.Y` | Ready to publish | Publishes the release |

| State | Meaning | Next step |
|-------|---------|-----------|
| PLANNED | Release is planned and ready | `/create-snapshot` |
| SNAPSHOT ACTIVE | Release PR under review | Review and merge PR |
| DRAFT READY | Draft awaiting publication | `/publish-release --confirm rX.Y` |
| PUBLISHED | Done | — |

---

## Learn More

- [How automation works](../automation/how-automation-works.md) — what the system does for you
- [Terminology](terminology.md) — definitions of key terms
