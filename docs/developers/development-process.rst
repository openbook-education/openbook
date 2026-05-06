===================
Development Process
===================

This page describes the expected repository workflow from issue triage to merge.

.. contents:: Page Content
   :local:


---------------
Issue to Branch
---------------

All development work begins with an issue. Collect ideas, feature requests, bugs, and general
development tasks as GitHub issues. Once created, discuss scope and expected behavior with the
team in the issue comments to ensure alignment. Add approved issues to the GitHub Project board
and assign a milestone where relevant.

When you are ready to work on an issue, create a feature branch from ``main`` (ideally using
GitHub's branch creation feature directly within the issue). Use a descriptive branch name that
indicates the issue number and type of work, e.g.

- ``<issue>/feature/<short-description>`` for new features,
- ``<issue>/bugfix/<short-description>`` for bug fixes,
- ``<issue>/docs/<short-description>`` for documentation updates, and
- ``<issue>/quality/<short-description>`` for refactoring or tooling work.

The patterns are no hard rules. You might especially find a better word for the second part,
depending on the work you plan to do. Throughout development, try to keep branch changes focused
to one logical change (though this may not be always possible).

.. note::

   You need to manually adjust the suggested branch name when creating the branch from GitHub.


------------
Pull Request
------------

When you are ready to merge your work, open a pull request. Your PR should be complete and
self-contained, with clear documentation of what changed and why. Use the following checklist
to ensure quality:

1. Link the relevant issue in the PR description. Ideally open an issue first.
2. Describe behavior changes and optionally test coverage if not obvious from the issue.
3. Add or update documentation for any user-facing changes.
4. Update :doc:`/administrators/changelog` for notable user-facing updates.
5. Keep backend test coverage at or above the configured threshold in ``pyproject.toml``.

For larger developments, split work into smaller pull requests when this reduces risk or improves
review quality. Early merges are acceptable even if a feature is not yet end-user complete, as
long as the intermediate state is safe and the changes are well-tested and documented.


-----------------
Checks and Review
-----------------

All pull requests must pass automated checks and receive manual review before merging.

**Automated Checks** --- The ``tests`` status check from ``.github/workflows/run-tests.yml``
is the required branch protection check. For changes under ``src/``, this workflow routes to
``run-tests-full.yml``, which runs linting, security checks, backend tests, and related quality
gates. For non-relevant changes, the dummy workflow path satisfies branch protection without
running the full suite.

**Manual Review** --- Copilot review is requested automatically. A maintainer then reviews the
pull request, examining correctness and regression risk, test completeness, API and documentation
consistency, and overall clarity and maintainability.


.. seealso::

   For the step-by-step release checklist (version bump, tagging, release automation), see
   :doc:`/developers/versioning-and-releases`. For repository-level and external service
   configuration, see :doc:`/developers/repository-setup`.
