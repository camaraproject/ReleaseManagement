# Releasing an API Repository

This guide walks you through releasing an API repository in CAMARA.

## Quick Process Overview

- [ ] Update `release-plan.yaml`
- [ ] Ensure all intended changes are merged to `main`
- [ ] APIs meet their declared target statuses (Checks on `main` should be green)
- [ ] `/create-snapshot` in Release Issue
- [ ] Edit `CHANGELOG-rX.md` on the release-review branch, get approvals, merge Release PR
- [ ] `/publish-release`
- [ ] Merge post-release sync PR → Done

## The Release Process

### 1. Plan Your Release

**What you do:**
- Update `release-plan.yaml` on `main` with your release intentions
- Set `target_release_tag`, `target_release_type`, and, for each API, the `target_api_version` and `target_api_status`.

**What you see:**
- CI validates every PR on `release-plan.yaml`
- Release Issue appears with PLANNED state, after a change of release-plan.yaml is merged with a `target_release_type` other than `None`

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
1. Go to the automatically created Release Issue (cf. Step 1) for your target release (rX.Y)
2. Post `/create-snapshot` as a comment

**What you see:**
- Automation validates your repository
- If successful: Release PR created, issue shows "SNAPSHOT ACTIVE"
- If failed: Error message with what to fix

**What can block you:**
- Validation errors → fix on `main`, then `/create-snapshot` again
- Dependency not published → wait or update `release-plan.yaml`

---

### 4. Edit and Review

**What you do:**

1. **Edit `CHANGELOG-rX.md` on the release-review branch.**
   - Automation generates the following input in the CHANGELOG-rX.md for this release:
     - a temporary section (removed on release) listing all the PRs merged since the relevant previous release, and, for each API, 
     - a first sentence describing the API version
     - when available, a second sentence stating the comparison target for this API (matching the `Comparison target` value in the Release PR's "Release contents" table). This line should not be changed.
     - the "update" sections: Breaking changes / Added / Changed / Fixed / Removed (by defaulting set to `N/A`).
   - Codeowners complete the Breaking changes, Added, Changed, Fixed, and Removed sections for each API during release review as follows:
     - copy or move the relevant entries from the temporary section into that API's update sections, replacing `N/A`, or leave `N/A` when a section has no changes. In particular for breaking changes:
       - list breaking changes both in the Breaking changes section and in their normal update section.
       - leave `N/A` in the Breaking changes section only when there are no breaking changes or compatibility risks for that API.
       - for stable post-1.0.0 minor or patch releases, the Breaking changes section may also disclose compatibility risks (without implying any SemVer-breaking change).
     - for first-time APIs or APIs without a comparison target, typically fill only the Added section.
     - adjust the generated first sentence if needed.
     - commit these changes directly to the release-review branch.

2. **Ensure required approvals are in place** (codeowner and release reviewer). After the release reviewer reviews the Release PR, the codeowners address any feedback with further commits to the release-review branch, until release reviewer approval is obtained.

3. **Merge the Release PR.**

> **Do not** open a separate PR to `main` for the CHANGELOG — the post-release sync PR (step 6) carries it back to `main` automatically.

**What you see:**
- After merge: Draft release created, issue shows "DRAFT READY"

**What can block you:**
- Issue found in API specification (or anything beyond `CHANGELOG-rX.md` and `README.md`):
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
- Pointer branch (`release/rX.Y` or `pre-release/rX.Y`) created at the tag commit
- Snapshot and release-review branches deleted automatically
- Post-release sync PR opened
- Release Issue closed

**What can block you:**
- Issue found in draft:
  1. Post `/delete-draft <reason>` on the Release Issue
  2. Fix the issue on `main`
  3. Post `/create-snapshot` to start fresh

---

### 6. Post-Release Sync

**What you do:**
1. Review and merge the post-release sync PR. It carries `CHANGELOG-rX.md` and the automation-updated `README.md` back to `main`.
2. Delete the source branch `pr-to-main/rX.Y` — you can use GitHub's "Delete branch" button on the merged PR.

**What you see:**
- `main` is in sync with the published release. The pointer branch (`release/rX.Y` or `pre-release/rX.Y`) remains as the browseable view of the release.

---

## Quick Reference

This section is a summary only. For explanations, see the sections above.

| Command | When to use | Effect |
|---------|-------------|--------|
| `/create-snapshot` | Ready to release | Creates Release PR |
| `/discard-snapshot <reason>` | Problem found during review | Returns to start |
| `/delete-draft <reason>` | Problem found in draft | Returns to start |
| `/publish-release --confirm rX.Y` | Ready to publish | Publishes the release |

| Release State | Meaning | Next step |
|-------|---------|-----------|
| PLANNED | Release is planned and ready | `/create-snapshot` |
| SNAPSHOT ACTIVE | Release PR under review | Review and merge PR |
| DRAFT READY | Draft awaiting publication | `/publish-release --confirm rX.Y` |
| PUBLISHED | Done | — |

---

## Learn More

- [How automation works](../automation/how-automation-works.md) — what the system does for you
- [Terminology](terminology.md) — definitions of key terms
