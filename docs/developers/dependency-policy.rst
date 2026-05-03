=================
Dependency Policy
=================

This page documents how OpenBook evaluates, adds, and updates dependencies.
The policy is intentionally practical: it favors maintainability and
traceability over fast but opaque upgrades.

.. contents::
   :local:
   :depth: 1


----------------
Guiding Approach
----------------

Dependencies save development time but introduce maintenance risk. OpenBook
therefore keeps dependency growth deliberate.

A dependency is a good candidate when it provides clear value that would be
costly to reimplement and when its scope stays understandable enough to be
replaced if needed.

Before introducing a new dependency, open a tracking issue and document the
selection process.


--------------------
Baseline Eligibility
--------------------

Each dependency must satisfy all of the following:

- It has a clear, license-compatible distribution model.
- It provides tagged releases in a package registry.
- It shows active maintenance within the last 12 months.
- It has no known unpatched security advisories at introduction time.

If any baseline criterion fails, the dependency is rejected.


---------------------------
Evaluation Depth and Impact
---------------------------

Not every dependency requires the same depth of evaluation. OpenBook uses a
lightweight impact-driven approach:

- Low impact: short assessment is enough.
- Medium impact: compare candidates with objective metrics.
- High impact: prototype finalists before deciding.

When uncertainty remains after scoring, prefer a smaller dependency with lower
replacement cost.


------------------------
Non-Runtime Dependencies
------------------------

Development and documentation dependencies are updated more aggressively than
runtime dependencies, because they are not part of a public API contract.

Typical examples:

- test and coverage tooling
- Sphinx and documentation extensions
- GitHub Actions dependencies


------------------------------------
Semi-Automated Updates With Renovate
------------------------------------

`Renovate <https://docs.renovatebot.com/>`_ regularly checks the repository for
dependency updates. For maintainers, this means:

1. Normally, let Renovate open and scope update PRs.
2. Review change impact and migration notes.
3. Run CI and fix integration breakage in the same PR.
4. Merge only when checks pass and behavior is verified.

Use the provided manual-dispatch scripts when an out-of-band update is needed.
Avoid untracked bulk updates from local shells, because they bypass the
repository's review and audit trail.


------------------------------------
Test Strategy For Dependency Updates
------------------------------------

Dependency update validation is enforced through the normal CI checks. But still
it makes sens to run tests locally before merging, and especially to manually test
that that everything is still working from a user's point-of-view.
