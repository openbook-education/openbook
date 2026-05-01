GitHub Development Process
==========================

This page describes the expected repository workflow from issue triage to merge.

Issue to branch
---------------

1. Confirm scope and expected behavior in an issue.
2. Create a feature branch from ``main`` (ideally from within the GitHub issue).
3. Keep branch changes focused to one logical change.

Suggested branch naming (note, that this requires manually changing the
suggested branch name when creating the branch within an issue):

- ``<issue>/feature/<short-description>``
- ``<issue>/bugfix/<short-description>``
- ``<issue>/docs/<short-description>``
- ``<issue>/quality/<short-description>``
- …

Pull request
------------

1. Link relevant issue in the PR description. Ideally open an issue, first.
2. Describe behavior changes and optionally test coverage, if not obvious from the issue.
3. Add or update documentation for user-facing changes.
4. Update :doc:`/reference/changelog` for notable user-facing updates.
5. Keep backend coverage at or above the configured threshold in ``pyproject.toml``.

Checks and review
-----------------

- Required CI checks must pass.
- The ``tests`` status check from ``.github/workflows/run-tests.yml`` is the
  required branch protection check.
- For changes under ``src/``, ``run-tests.yml`` routes to
  ``run-tests-full.yml``.
- For non-relevant changes, the dummy workflow path satisfies branch
  protection without running the full suite.
- The full workflow runs linting, security checks, backend tests, and related
  quality gates.
- Copilot review is requested automatically.
- Manual maintainer review confirms behavior, tests, and documentation quality.

Review focus areas:

- Correctness and regression risk
- Test completeness
- API/documentation consistency
- Clarity and maintainability

Runtime dependency update flow
------------------------------

OpenBook uses dedicated Renovate workflows rather than ad-hoc local updates.

1. ``.github/workflows/renovate-minor.yml`` handles patch/minor updates.
2. ``.github/workflows/renovate-major.yml`` handles major updates in separate PRs.
3. Review each PR with the same quality bar as feature work.
4. Use manual dispatch commands when an out-of-band update is required.

Do not bypass this process with broad manual ``poetry update`` or
``npm update`` runs. The Renovate workflow keeps update intent, review, and CI
evidence connected in one place.

Release handoff
---------------

The step-by-step release checklist (version bump, tagging, PyPI publish) is in
:doc:`/maintainers/versioning-and-releases`. Repository-level and external
service configuration is documented in :doc:`/maintainers/repository-setup`.
