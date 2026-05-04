=====================
# Development Process
=====================

This page describes the expected repository workflow from issue triage to merge.

.. contents:: Page Content
   :local:
   :depth: 1


---------------
Issue to Branch
---------------

1. Collect ideas, feature requests, bugs, and general development tasks in an issue.
2. Confirm scope and expected behavior in the issue discussion.
3. Add the issue to the GitHub Project board and assign a milestone where relevant.
4. Create a feature branch from ``main`` (ideally from within the GitHub issue).
5. Keep branch changes focused to one logical change.

Suggested branch naming (note, that this requires manually changing the
suggested branch name when creating the branch within an issue):

- ``<issue>/feature/<short-description>``
- ``<issue>/bugfix/<short-description>``
- ``<issue>/docs/<short-description>``
- ``<issue>/quality/<short-description>``
- …


------------
Pull Request
------------

1. Link relevant issue in the PR description. Ideally open an issue, first.
2. Describe behavior changes and optionally test coverage, if not obvious from the issue.
3. Add or update documentation for user-facing changes.
4. Update :doc:`/administrators/changelog` for notable user-facing updates.
5. Keep backend coverage at or above the configured threshold in ``pyproject.toml``.

For larger developments, split work into smaller pull requests when this reduces risk or improves
review quality. Early merges are acceptable even if a feature is not yet end-user complete, as long
as the intermediate state is safe.


-----------------
Checks and Review
-----------------

- Required CI checks must pass.
- The ``tests`` status check from ``.github/workflows/run-tests.yml`` is the required branch protection check.
- For changes under ``src/``, ``run-tests.yml`` routes to ``run-tests-full.yml``.
- For non-relevant changes, the dummy workflow path satisfies branch protection without running the full suite.
- The full workflow runs linting, security checks, backend tests, and related quality gates.
- Copilot review is requested automatically.
- Manual maintainer review confirms behavior, tests, and documentation quality.

Review focus areas:

- Correctness and regression risk
- Test completeness
- API/documentation consistency
- Clarity and maintainability


---------------
Release Handoff
---------------

The step-by-step release checklist (version bump, tagging, release automation) is in
:doc:`/developers/versioning-and-releases`. Repository-level and external
service configuration is documented in :doc:`/developers/repository-setup`.
