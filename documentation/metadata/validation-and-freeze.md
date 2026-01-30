# Validation and Configuration Lock

This document explains which validation checks apply in different situations and when release configuration changes are blocked.

## When Validation Runs

Validation always checks repository content against the declared intent in `release-plan.yaml`. Which checks apply depends on what is being changed or triggered.

## Pull Requests Changing `release-plan.yaml`

When a pull request modifies `release-plan.yaml`, validation ensures that:

* The file follows the expected schema
* The declared release intent is internally consistent
* The repository content already matches the newly declared intent

This makes changes to release intent explicit and reviewable.

## Pull Requests to `main` (No Changes to `release-plan.yaml`)

When a pull request does not modify `release-plan.yaml`, validation ensures that:

* Repository content remains compatible with the currently declared release intent
* API definitions, tests, and documentation do not violate declared API statuses
* Version placeholders and formatting remain valid

Implementation changes are free to evolve, as long as they stay within the declared intent.


## Creating a Snapshot

When creating a snapshot (via `/create-snapshot`), validation ensures that:

* The current HEAD of the base branch satisfies the declared release intent
* All required dependencies are published
* No other snapshot is active for the same release

No new rules are introduced at this stage. This is a final consistency check before creating an immutable snapshot.


## Configuration Lock During Active Snapshot

While a snapshot is active, changes to `release-plan.yaml` for that release are blocked.

This applies only to release configuration. Normal development on `main` can continue.

Configuration becomes editable again when the snapshot is discarded, the draft is deleted, or the release is published.

## Post-Public-Release Lock

After a public release, APIs at the released version are locked to preserve release integrity. Further changes require updating `target_api_version` in `release-plan.yaml`.

## Common Validation Errors

| Error | Fix |
|-------|-----|
| "API at draft status cannot be released" | Promote API to `alpha` or higher |
| "Dependency not found" | Wait for dependency or update version |
| "Status does not match release type" | Promote API status or change release type |
| "Configuration frozen for active snapshot" | Discard snapshot first |
| "Mixed PR: metadata and implementation" | Split into separate PRs |
