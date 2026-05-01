Local Development
=================

This page documents day-to-day local workflows for maintainers.
Repository-level and external service setup remains in
:doc:`/maintainers/repository-setup`.

Prerequisites
-------------

- Python ``3.12`` or newer
- Poetry package manager
- Node.js and npm (workspace builds)
- Redis for local integrated runs
- Java for OpenAPI generator tooling

Install dependencies
--------------------

Run dependency installation from the repository root:

.. code-block:: bash

    poetry install --no-interaction --with docs
    npm install

Always run ``npm install`` in the repository root. Do not run it inside
``src/frontend`` because nested ``node_modules`` directories can shadow
workspace dependencies.

Start local development
-----------------------

The standard integrated development command is:

.. code-block:: bash

    npm start

This command starts Django (via Daphne), Redis, frontend/library watch builds,
and local helper services used by authentication flows.

Run tests
---------

Run the full backend test suite:

.. code-block:: bash

    npm run test:backend

Run project-wide quality checks:

.. code-block:: bash

    npm run check

Run test coverage
-----------------

Coverage is configured in ``pyproject.toml`` and enforced with a
``fail_under`` threshold of **75%**.

Run coverage from the repository root:

.. code-block:: bash

    cd src
    poetry run coverage run --rcfile=../pyproject.toml manage.py test
    poetry run coverage report --rcfile=../pyproject.toml -m

If coverage fails, review the ``Missing`` column and add tests for the
reported lines or branches before opening a PR.

Build documentation
-------------------

Continuously rebuild the documentation when sources change and start a
webserver on port `8885` for hot-reloading:

.. code-block:: bash

    npm run docs

Or build documentation just once:

.. code-block:: bash

    npm run docs:build

In both cases, the generated HTML files will be saved in `docs/_build`.
In background the above commands are shortcuts for:

.. code-block:: bash

    poetry run sphinx-autobuild -W -T -v --port 8885 docs/ docs/_build
    poetry run sphinx-build -W -T -v docs/ docs/_build

What these options do:

- ``-W``: Treat warnings as errors (to catch broken references)
- ``-T``: Print tracebacks
- ``-v``: Verbose output (``-v -v`` even more verbose)

Deliberately not included is ``--keep-going``, because it may swallow errors.

Common maintenance commands
---------------------------

- Show dependency graph: ``poetry show --tree``
- Update lock file after dependency changes: ``poetry lock``
- Start all local services: ``npm start``
- Build frontend and libraries once: ``npm run build``
- Run dependency security checks: ``npm run check:security``

Daily checklist
---------------

1. Pull latest ``main``.
2. Run ``npm run check``.
3. Run coverage and confirm it stays at or above 75%.
4. Run docs build if public behavior or docs changed.
5. Keep changelog updates in :doc:`/reference/changelog` for user-visible
   changes.
