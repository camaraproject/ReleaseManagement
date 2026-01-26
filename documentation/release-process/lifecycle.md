# Release Lifecycle

This document describes the lifecycle of a release from planning to publication.

---

## Overview

A release progresses through these phases:

1. **Planning** — Codeowners declare release intent and scope in `release-plan.yaml`
2. **Development** — Work happens on `main` toward the planned release
3. **Snapshot creation** — Automation creates an immutable release snapshot
4. **Review** — Humans review documentation; approve the Release PR
5. **Publication** — Human publishes the draft release, creating the final tag
6. **Post-release** — Cleanup and preparation for the next cycle

---

## Phase 1: Planning

A release cycle begins when codeowners declare their intent in `release-plan.yaml`.

**When this happens:**
- When a new release cycle is decided (e.g., participation in a meta-release)
- When a release scope issue is created
- At the start of development toward a specific release target

**What happens:**
- Codeowners set the `release_track` (independent or meta-release) and `meta_release` cycle if applicable
- Codeowners set the target release tag, release type, and target API statuses
- New APIs may be declared with `draft` status while implementation is planned
- The release plan establishes the scope and goals for upcoming work
- CI validates that the plan is well-formed (but does not yet require readiness)

**What is expected of you:**
- Update `release-plan.yaml` to declare your release intentions early
- Set `release_track` and `meta_release` appropriately for your participation
- Set realistic target statuses based on planned work
- Adjust the plan as scope evolves during development

**Key principle:** The release plan declares *intent* before implementation is complete. It is a planning tool, not a release trigger.

For details on the file format, see [metadata/release-plan.md](../metadata/release-plan.md).

---

## Phase 2: Development on `main`

With the release plan established, development proceeds on the `main` branch.

**What happens:**
- API specifications are developed and refined toward the planned release
- Version fields remain set to `wip` (work-in-progress)
- APIs at `draft` status receive basic validation while implementation continues
- APIs at `alpha` or higher receive full validation for their status level
- CI validates changes against CAMARA guidelines
- PRs are reviewed and merged normally

**What is expected of you:**
- Keep API specifications in `wip` state throughout development
- Promote APIs from `draft` to `alpha` when implementation is ready for feedback
- Respond to CI validation feedback
- Maintain release assets (tests, documentation) alongside the API
- Update `release-plan.yaml` if scope or targets change

**Key principle:** The `main` branch is always in a work-in-progress state. The release plan guides development but does not block it. APIs at `draft` status allow declaration without full validation.

---

## Phase 3: Snapshot creation

When development is complete and the repository meets the declared targets, a maintainer triggers snapshot creation via the `/create-snapshot` command in the Release Issue.

**What happens:**
1. Automation validates the current HEAD of `main` against the release plan
2. CI confirms that all APIs meet their declared target statuses (no `draft` APIs allowed)
3. If validation passes:
   - A **snapshot branch** is created (`release-snapshot/rX.Y-<sha>`)
   - Mechanical changes (version numbers, URLs) are applied to the snapshot
   - `release-metadata.yaml` is generated with the source commit SHA
   - A **release-review branch** is created (`release-review/rX.Y-<sha>`)
   - CHANGELOG and README updates are committed to the release-review branch
   - A **Release PR** is opened (release-review → snapshot)
4. The Release Issue state changes from OPEN to SNAPSHOT ACTIVE

**What is expected of you:**
- Create a Release Issue for the target release (`rX.Y`)
- Ensure all intended changes are merged to `main` before triggering
- Verify that APIs meet their declared target statuses
- Run `/create-snapshot` in the Release Issue
- If validation fails, address the issues and run `/create-snapshot` again

**Key principle:** The snapshot is immutable. If issues are found in the API specification, they must be fixed on `main`, the snapshot discarded with `/discard-snapshot`, and a new snapshot created.

---

## Phase 4: Review and finalization

The Release PR allows review of documentation before publication. The PR merges the release-review branch (human-editable) into the snapshot branch (automation-owned).

**What happens:**
- Reviewers examine the CHANGELOG, README, and readiness checklist
- Codeowners can refine documentation directly on the release-review branch
- Contributors and maintainers submit PRs from forks to the release-review branch
- Both codeowner(s) and Release Management reviewer(s) must approve
- The Release PR is merged into the snapshot branch
- Release Issue state changes from SNAPSHOT ACTIVE to DRAFT READY

**What is expected of you:**
- Review the generated CHANGELOG for accuracy
- Add any additional release notes or context
- Approve the Release PR when satisfied
- If API issues are discovered:
  1. Run `/discard-snapshot <reason>` to abandon the snapshot
  2. Fix issues on `main` via normal PRs
  3. Run `/create-snapshot` to start a fresh attempt

**Key principle:** Only documentation is reviewable. Mechanical changes (version numbers) on the snapshot branch are protected and cannot be edited directly.

---

## Phase 5: Publication

After the Release PR is merged, the release proceeds through draft creation and publication.

**Draft creation (automatic):**
- Automation creates a draft GitHub release
- The `release_date` field is set in `release-metadata.yaml`
- The draft contains the release artifacts
- Release Issue state is DRAFT READY

**Publication (manual):**
- A codeowner reviews the draft release
- The codeowner publishes the release via GitHub Releases UI
- Publication creates the final Git tag (e.g., `r4.1`)
- Release Issue state changes to PUBLISHED and is closed

**What is expected of you:**
- Review the draft release before publishing
- Verify the release notes and artifacts are correct
- Publish the release when ready
- If issues are found before publication:
  1. Run `/delete-draft <reason>` to remove the draft and snapshot
  2. Fix issues on `main`
  3. Run `/create-snapshot` to start fresh

**Key principle:** Automation creates drafts; humans publish. This provides a final checkpoint before the release becomes permanent. The tag is only created at publication.

---

## Phase 6: Post-release actions

After publication, several actions complete the cycle.

**What happens:**
- A reference tag (`src/X.Y`) is created on `main` at the commit that was released
- An automated PR merges selective updates back to `main`:
  - CHANGELOG entries for the release
  - README updates with latest version links
  - API version fields remain `wip` (not updated)
- For public releases, CI locks APIs at the released version
- Snapshot branch is deleted (the release tag preserves the content)
- Release-review branch is kept for reference

**What is expected of you:**
- Review and merge the post-release PR to `main`
- Update `release-plan.yaml` for the next release cycle
- For public releases, update `target_api_version` before making changes

**Key principle:** After a public release, explicit planning is required before the next change. The `src/X.Y` tag marks the branch point for potential future maintenance releases.

---

## What happens next

After completing a release cycle:

- For **pre-releases**: Continue development on `main`, update the release plan for the next target, and create the next release when ready
- For **public releases**: Plan the next version in `release-plan.yaml` and begin the next cycle
- For **maintenance releases**: Apply patches to the maintenance branch and follow the same release process

---

## Common questions

**When should I update `release-plan.yaml`?**
Early—when you decide to participate in a release cycle or when scope is established. The release plan is a planning tool, not something you fill in at the last moment.

**Can I make changes to the API after creating a snapshot?**
No. Snapshots are immutable. Run `/discard-snapshot <reason>`, fix issues on `main`, and run `/create-snapshot` again.

**What if I need to change the CHANGELOG after the snapshot?**
The release-review branch allows documentation edits. Refine the CHANGELOG there before merging the Release PR.

**How many snapshots can I create?**
As many as needed. Each attempt gets a unique branch with SHA-based naming. Discarding snapshots is normal and expected.

**When does the release tag get created?**
Only at publication. The tag `rX.Y` is created when a codeowner publishes the draft release.

**What if I find an issue after the Release PR is merged but before publication?**
Run `/delete-draft <reason>` to delete the draft release and return to OPEN state. Fix issues on `main`, then run `/create-snapshot` again.

**Can I change the release plan while a snapshot is active?**
No. While a snapshot is active, `release-plan.yaml` changes for that release are blocked (scoped configuration freeze). Discard the snapshot first if you need to change the plan.

**Can I change the release plan during development?**
Yes. The release plan should evolve as understanding improves. Update target statuses or release type as needed—just not while a snapshot is active.
