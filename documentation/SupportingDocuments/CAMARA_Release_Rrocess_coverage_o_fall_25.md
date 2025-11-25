# CAMARA Release Process – Coverage of Fall25 Release PR Checks

NOTE: this is a markdown snapshot of https://lf-camaraproject.atlassian.net/wiki/spaces/CAM/pages/134447129/CAMARA+Release+Process+-+Coverage+of+Fall25+Release+PR+checks as of 2025-11-25 (v19).

Originally based on [Automate release PR checking for release version updates · Issue #9 · camaraproject/tooling](https://github.com/camaraproject/tooling/issues/9), and updated with the validation and generation phases defined in [CAMARA Release Workflow and Metadata Concept](https://github.com/camaraproject/ReleaseManagement/blob/main/documentation/SupportingDocuments/CAMARA-Release-Workflow-and-Metadata-Concept.md).

---

## Release Workflow Categories

The CAMARA release process is structured into five **workflow categories (C1–C5)**. Each category defines what is validated or generated, where it happens (main, release, or maintenance branch), and how automation enforces consistency. Together, they form the backbone of the automated release process.

| **Category** | **Description** | **`main` content rule** |
|---------------|-----------------|--------------------------|
| **C1 – Continuous Validation on `main`** | Full linting and schema checks (YAML + OpenAPI), enforcing the work‑in‑progress rule. CI ensures `main` always contains placeholders and never concrete release values. | Placeholders only: `info.version: "wip"`, `{{version}}`, `{{api_version}}`; placeholder server URLs. |
| **C2 – Automated Release Branch Generation** | On release trigger, tooling creates the release branch, replaces placeholders with computed values (exact versions, server URLs), and writes `release-metadata.yaml`. | Concrete values are set only in the release branch. |
| **C3 – Release Preparation & Review** | Manual review through PRs to the release branch; branch protection enforces CODEOWNERS and reviewer approvals. | — |
| **C4 – Tagging & Post‑Release Sync** | Create tag, publish artifacts (including `release-metadata.yaml`), and open a sync PR to `main`. `main` stays with placeholders. | — |
| **C5 – Maintenance / Patch Release** | Apply the same C2–C4 flow on `maintenance‑rX` branches for hot‑fix releases (`release_readiness: patch‑release`). | — |

---

## Topic‑by‑Topic Coverage

| **Topic / Expected Check** | **How It’s Addressed** | **Category** |
|-----------------------------|-------------------------|---------------|
| **YAML and OpenAPI schema validity** | CI runs MegaLinter + schema checks on every PR to `main`. | C1 |
| **Version field handling (`info.version`)** | Must be `"wip"` on `main`; real value is computed from `target_version` with auto‑incremented suffix (e.g. `‑rc.2`) in the release branch. | C1 → C2 |
| **Server URL pattern enforcement (“Version in URL path”)** | Placeholder format validated on `main`; concrete `vX.Y` replaced during release generation. | C1 + C2 |
| **API status / repository readiness coherence** | CI cross‑checks `release_readiness` vs each `api_status`. | C1 |
| **Existence of API definitions and tests** | Required for all `alpha` or higher APIs; CI fails if missing. | C1 |
| **No changes to `unchanged` APIs** | CI diff against previous release tag; reference point on `main` marked by `src/X.Y`. | C1 |
| **Dependency references (Commonalities / ICM)** | Only meta‑release references on `main`; concrete tag refs inserted in release branch. | C1 + C2 |
| **Mutual exclusivity of PR types** | CI blocks PRs that change both `release‑plan.yaml` and OpenAPI/test files. | C1 |
| **Placeholder replacement** | Done automatically for `{{api_version}}`, `{{commonalities_version}}`, etc. in release branch. | C2 |
| **Generation of `release‑metadata.yaml`** | Scripted from `release‑plan.yaml` + commit SHA. | C2 |
| **CHANGELOG generation** | Auto‑generated (as far as possible), edited and reviewed via Release Preparation PR. | C2 + C3 |
| **Readiness checklist validation** | Evaluated from metadata; results shown in Release Preparation PR summary. | C2 + C3 |
| **Approval and branch protection** | Required CODEOWNER approval before tag creation. | C3 |
| **Tag creation and artifact publishing** | After approval, CI creates `rX.Y` tag and GitHub Release with artifacts, including `release‑metadata.yaml`. | C4 |
| **Post‑release PR to `main`** | After tagging, automation opens a PR to `main` that adds new `CHANGELOG.md` and README entries. All specs remain with `"wip"` placeholders; for public releases, `release‑plan.yaml` is updated to set APIs to `unchanged`. | C4 |
| **`src/X.Y` tag creation** | Marks branch point on `main` for maintenance tracking. | C4 |
| **Maintenance / patch releases** | Executed on `maintenance‑rX` branches with same validation logic as main releases. | C5 |

---

## Summary Table

| **Category** | **Main Focus** | **When Applied** | **Key Artifacts** |
|---------------|----------------|------------------|------------------|
| **C1 – Validation on `main`** | Ensure structure, placeholder (“wip”) state, and metadata correctness. | All PRs to `main`. | CI reports, schema lint logs. |
| **C2 – Release Branch Generation** | Replace placeholders, compute versions, generate metadata + CHANGELOG. | On release trigger (issue label). | `release‑metadata.yaml`, `CHANGELOG.md`. |
| **C3 – Review & Approval** | Manual review of release branch artifacts. | PRs to `release/rX.Y`. | Reviewed PRs, branch protection checks. |
| **C4 – Tag & Sync Back** | Tag, publish, open sync PR to `main` (`CHANGELOG`, README, update `release‑plan.yaml` to `unchanged` where applicable). | After approval / tag. | GitHub Release, `src/X.Y` tag, sync PR to `main`. |
| **C5 – Maintenance** | Patch releases on older cycles, same checks as main flow. | When needed. | `maintenance‑rX` branches, patch tags. |

---

## Backup — Original Release PR Topics and How They Map

The following list retains the wording of the original Fall25 Release PR check topics, mapped to their handling within the defined categories.

### **API YAML**
- `externalDocs:` section → lint rule on `main` (C1).
- `CHANGELOG.md` release section → auto‑generated on release branch (C2).
- **API Readiness Checklist** → complete list generated on release branch (C2).
- **Test files** → required for all `alpha` or higher APIs (C1).
- `info.version` → must be `"wip"` on `main`; set only in release branch (C1 → C2).
- `info.description` (ICM auth text / error codes) → linted or placeholder (C1 → C2).
- Version in URL path → placeholder validated on `main`, set on release (C1 + C2).
- `x‑camara‑commonalities` version → placeholder on `main`, set on release (C1 + C2).
- YAML filename syntax → lint rule (C1).
- Presence of `securitySchemes` in `components` → schema check (C1).
- Presence/pattern of `x‑correlator` schema → schema check (C1).
- `contact` section should be removed → lint rule (C1).
- Release number in headings/links → replaced by template generation (C2).
- API version, name, Commonalities/ICM references → derived from `release‑plan.yaml`.
- API description wiki linked → visible only during release review process (C3).
- Check `operationId` usage → lint rule (C1).
- Check version occurrences (top + background) → replaced in release branch (C2).

### **README**
- Complete **Release Information** section (re)generated on release branch (C2) and again on `main` (C4).
- Release number in links → updated on release branch (C2).
- Link to CAMARA website → optional in Release Information section on `main` (C4).

### **Review Process**
- Generate release PR → handled by automation (C2 + C3).
- Manage progress for M3/M4 reviews → derived from metadata and shown in meta‑release overview (C2 + C3).

### **Other Automation Needs / Ideas**
- Spelling checker → additional lint rule (C1).

---

**Document scope:** provides traceable alignment between the Fall25 Release PR checks and the new automated release workflow to ensure uniform validation, generation, and synchronization across repositories.

