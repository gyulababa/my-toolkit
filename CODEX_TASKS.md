# CODEX_TASKS.md — Persistence API Inversion + Deprecation Enforcement

Repo state: refactor already completed.  
Goal now: enforce helpers.persist as canonical and deprecate catalogloader safely.

Global rules:
- helpers/persist/* is canonical
- helpers/catalogloader/* is deprecated facade only
- Mechanical refactor only
- Run pytest -q after each phase

---

# Phase 0 — Baseline Audit

Run:

    pytest -q

Search for deprecated imports:

    rg -n "helpers\.catalogloader" .

Classify hits:
- tests → allowed
- helpers/catalogloader itself → allowed
- anywhere else → must migrate

Commit:
    chore(audit): catalogloader usage inventory

---

# Phase 1 — Import Migration to helpers.persist

For every non-test module importing helpers.catalogloader:

Replace:

    from helpers.catalogloader.X import Y

With helpers.persist equivalent.

Rules:
- Do not change behavior
- Only change import paths
- Keep symbol names same where possible

Verify:

    pytest -q

Commit:
    refactor(imports): migrate to helpers.persist API

---

# Phase 2 — Catalogloader → Thin Facade

helpers/catalogloader/* must become thin wrappers.

Allowed contents:

- import from helpers.persist
- forward calls
- optional DeprecationWarning

Not allowed:

- new logic
- persistence rules
- path building
- schema validation

Pattern:

    from helpers.persist.foo import Bar as Bar

or wrapper function that calls persist layer.

Verify:

    pytest -q

Commit:
    refactor(catalogloader): convert to deprecated facade

---

# Phase 3 — Deprecation Warnings

Add DeprecationWarning in catalogloader public entrypoints.

Pattern:

    import warnings
    warnings.warn("helpers.catalogloader is deprecated; use helpers.persist", DeprecationWarning, stacklevel=2)

Do not change behavior.

Verify:

    pytest -q

Commit:
    feat(deprecation): catalogloader warnings

---

# Phase 4 — Persistence Boundary Enforcement

Ensure:

- No scattered persist path literals outside helpers.persist
- No index schema logic outside helpers.persist
- No revision promotion inside read-only loaders

Search:

    rg -n "persist_root\s*/" helpers

Move logic into helpers.persist if found.

Verify:

    pytest -q

Commit:
    refactor(persist): enforce persistence boundaries

---

# Deliverable Summary

Report:

- migrated imports
- facade modules
- warnings added
- violations fixed
- test results
