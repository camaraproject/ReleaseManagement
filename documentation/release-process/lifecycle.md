# Release Lifecycle

This document describes the lifecycle of a release from planning to publication.

---

## Overview

A release progresses through these phases:

1. **Development** — Work happens on `main`, version fields set to `wip`
2. **Planning** — Codeowners declare intent in `release-plan.yaml`
3. **Snapshot creation** — Automation creates an immutable release snapshot
4. **Review** — Humans review documentation; approve the Release PR
5. **Publication** — Human publishes the draft release, creating the final tag
6. **Post-release** — Cleanup and preparation for the next cycle

---

## Phase 1: Development on `main`

All API development happens on the `main` branch.

**What happens:**
- API specifications are developed and refined
- Version fields remain set to `wip` (work-in-progress)
- CI validates changes against CAMARA guidelines
- PRs are reviewed and merged normally

**What is expected of you:**
- Keep API specifications in `wip` state until ready for release
- Respond to CI validation feedback
- Maintain release assets (tests, documentation) alongside the API

**Key principle:** The `main` branch is always in a work-in-progress state. It never contains release-ready version numbers outside of release preparation.

---

## Phase 2: Declaring release intent

When ready to release, codeowners update `release-plan.yaml` on `main`.

**What happens:**
- Codeowners set the target release tag, release type, and API statuses
- CI validates that declared statuses match actual API readiness
- The repository becomes eligible for release creation

**What is expected of you:**
- Update `release-plan.yaml` with your release intentions
- Ensure all APIs meet the requirements for their declared status
- Address any CI validation errors before proceeding

**Key principle:** The release plan declares *intent*. CI validates that reality matches the declaration.

For details on the file format, see [metadata/release-plan.md](../metadata/release-plan.md).

---

## Phase 3: Snapshot creation

A maintainer triggers snapshot creation when ready.

**What happens:**
- Automation validates the current state of `main`
- If validation passes, a snapshot branch is created
- Mechanical changes (version numbers, URLs) are applied to the snapshot
- A release-review branch is created for documentation
- A Release PR is opened for review

**What is expected of you:**
- Ensure all intended changes are merged to `main` before triggering
- Wait for the snapshot to be created successfully
- If validation fails, address the issues and trigger again

**Key principle:** The snapshot is immutable. If issues are found in the API specification, they must be fixed on `main` and a new snapshot created.

---

## Phase 4: Review and finalization

The Release PR allows review of documentation before publication.

**What happens:**
- Reviewers examine the CHANGELOG, README, and readiness checklist
- Documentation can be refined on the release-review branch
- Both codeowner(s) and release reviewer(s) must approve
- The Release PR is merged into the snapshot branch

**What is expected of you:**
- Review the generated CHANGELOG for accuracy
- Add any additional release notes or context
- Approve the Release PR when satisfied
- If API issues are discovered: fix them on `main`, discard the snapshot, and create a new one

**Key principle:** Only documentation is reviewable. Mechanical changes (version numbers) are protected and cannot be edited.

---

## Phase 5: Publication

After the Release PR is merged, a draft release is created.

**What happens:**
- Automation creates a draft GitHub release
- The draft contains the release artifacts
- A human reviews the draft and publishes it
- Publication creates the final Git tag (e.g., `r4.1`)

**What is expected of you:**
- Review the draft release before publishing
- Verify the release notes and artifacts are correct
- Publish the release when ready

**Key principle:** Automation creates drafts; humans publish. This provides a final checkpoint before the release becomes permanent.

---

## Phase 6: Post-release actions

After publication, several actions complete the cycle.

**What happens:**
- A reference tag is created on `main` at the branch point
- CHANGELOG and README updates are merged back to `main`
- For public releases, CI locks APIs at the released version
- Snapshot branches are cleaned up (the tag preserves the content)

**What is expected of you:**
- Merge the post-release PR to `main`
- Update `release-plan.yaml` for the next release cycle
- For public releases, update target API versions before making changes

**Key principle:** After a public release, explicit planning is required before the next change. This ensures intentional version progression.

---

## What happens next

After completing a release cycle:

- For **pre-releases**: Continue development on `main`, update the release plan, and create the next release when ready
- For **public releases**: Plan the next version, update `release-plan.yaml`, and begin the next cycle
- For **maintenance releases**: Apply patches to the maintenance branch and follow the same release process

---

## Common questions

**Can I make changes to the API after creating a snapshot?**
No. Snapshots are immutable. Fix issues on `main`, discard the snapshot, and create a new one.

**What if I need to change the CHANGELOG after the snapshot?**
The release-review branch allows documentation edits. Refine the CHANGELOG there before merging the Release PR.

**How many snapshots can I create?**
As many as needed. Each attempt gets a unique branch. Discarding snapshots is normal and expected.

**When does the release tag get created?**
Only at publication. The tag `rX.Y` is created when a human publishes the draft release.
