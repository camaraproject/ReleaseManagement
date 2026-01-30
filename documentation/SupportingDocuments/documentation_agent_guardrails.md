# Documentation Guardrails for CAMARA Release Management

## Purpose

This document defines **guardrails** and **required practices** for maintaining the CAMARA Release Management documentation.

It ensures that the documentation:
- remains stable and scalable
- reflects user-facing behavior rather than internal implementation
- stays consistent with the agreed release process semantics

---

## Foundational Principle

**The Release Management documentation is the single user-facing contract.**

- Users must be able to operate the release process safely and predictably using only the documentation.
- Internal design documents (workflow concepts, detailed designs) are **inputs only** and must never be referenced, linked, or assumed by readers.

---

## Guardrails

### 1. Behavior over implementation

- Document **observable behavior, guarantees, and allowed actions**.
- Avoid committing to internal mechanics such as:
  - exact branch naming conventions
  - internal state derivation logic
  - bot message formatting contracts

Use invariant language (e.g. *"snapshots are immutable"*) instead of mechanism language (e.g. *"branch X is deleted"*).

---

### 2. Single navigational entry point

- `documentation/README.md` is the **only navigation hub**.
- Do not introduce folder-level README files or secondary indexes.
- Cross-link documents where needed, but avoid duplicating navigation structures.

---

### 3. Capability separation is intentional

The separation into the following areas must be preserved:

- `release-process`
- `metadata`
- `readiness`
- `automation`
- `roles`

Do not collapse these concerns into fewer documents or reintroduce monolithic documentation.

---

### 4. Happy path first

- Always explain the **normal, successful release flow** before:
  - discard
  - retry
  - recovery

Failure paths must be framed as **normal and expected**, not exceptional.

---

### 5. `release-plan.yaml` semantics are fixed

- `release-plan.yaml` declares **intent**, not readiness.
- It is updated **early**, when a release cycle is planned, not when a release is triggered.
- Documentation must not regress to late-stage or checklist-style interpretations of the file.

---

### 6. Scope issue vs release plan

- Each API repository has a **scope issue per release cycle** describing intended public API outcomes.
- `release-plan.yaml` describes the **next executable step(s)** within that cycle.
- These artifacts must not be conflated or blurred.

---

### 7. Release Issue authority boundary

- The Release Issue serves as:
  - user interface
  - trigger surface
  - audit trail

- The Release Issue is **not a source of truth**.
- All authoritative state is derived from repository artifacts.

This statement should be made explicit wherever Release Issues are introduced.

---

### 8. Readiness vs checklist boundary

- The API Readiness Checklist is a **documentation and review artifact**.
- Automation validation rules are derived from metadata and CAMARA guidelines, not from the checklist itself.
- Documentation must not imply that the checklist is machine-authoritative.

---

## Required Practices

### A. Lifecycle vs automation separation

- `release-process/lifecycle.md` answers: *In which phase does something happen?*
- Automation documents answer: *How users interact with the system during that phase.*

Avoid duplicating detailed mechanics (validation logic, internal steps) in lifecycle documents.

---

### B. Terminology consistency

- Use consistent terms across all documents:
  - release
  - snapshot
  - discard
  - publish
- Avoid synonyms that suggest failure or exception where the process is normal.

---

### C. Editorial checks before merging

Before merging documentation changes, verify that no wording suggests:

- `release-plan.yaml` is updated "when ready to release"
- scope issues are optional or informal
- abandoned release attempts are failures

---

## Working Mode

- Treat documentation changes as **contract changes**.
- Prefer minimal wording changes that restore guardrails over structural changes.
- Do not automatically apply feedback that suggests structural collapse or re-centralization.
- Escalate **conceptual or semantic changes** to the human maintainer.

---

This document is authoritative for all future documentation iterations.

