=================
Local Development
=================

Working on the OpenBook source code is easy if you know Python, Poetry, Django, npm, ...
Fear not if you don't remember all the details. This page serves as a cheat sheet that
documents day-to-day commands.

.. contents:: Page Content
   :local:

--------------------------
Required Development Tools
--------------------------

Local Installation
..................

Besides your favorite code editor or IDE, the following development tools are
required to build OpenBook. Make sure to install all of them to be able to
build and run the source code. Alternatively, use the provided dev container
configuration, if you have Docker or Podman installed but cannot or don't want
to install additional packages (see next section).

- Python
- Poetry package manager
- Node.js and npm (workspace builds)
- Redis for local integrated runs
- Java for OpenAPI generator tooling

Using Dev Containers
....................

If you prefer a containerised development environment, the repository includes a
dev container configuration that pre-installs all required tools. You only need
an IDE that supports dev containers, such as `Visual Studio Code <https://code.visualstudio.com/>`_
with the `Remote - Containers <https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers>`_
extension, and either `Docker <https://www.docker.com/>`_ or `Podman <https://podman.io/>`_.

On Windows, both Podman and Docker use Windows Subsystem for Linux, which is not
installed by default. If you prefer a graphical application, like Docker Desktop,
for container management, Podman Desktop is usually the better choice. It avoids
the licensing problems attached to Docker Desktop. To configure it:

1. Install Windows Subsystem for Linux: :command:`wsl --update`
2. Install Podman Desktop from `podman-desktop.io <https://podman-desktop.io/>`_.
3. Open Podman Desktop and install both Podman and Podman Compose.
4. In VS Code settings, set *Remote - Containers: Docker Path* to :command:`podman`.
5. Still in settings, set the Docker Compose path to :command:`podman compose`.
6. Restart VS Code.

Once the prerequisites are in place, open the project in VS Code and either
accept the "Reopen in Container" prompt or run *Remote-Containers: Reopen in
Container* from the command palette. Be very patient. The first build takes
quite a while; subsequent starts are fast, though.

All required tools come pre-installed in the containers, including the `Pi Coding Agent <pi.dev>`_
as a little extra. The container uses the same ports as the local development environment,
so you can access the application as usual.

.. note::

   The dev container configuration lives in the :file:`.devcontainer` directory at
   the root of the repository.


------------------------
Frequently Used Commands
------------------------

The npm scripts in the repository root are the primary interface for day-to-day
development tasks. Each of the following subsections covers one workflow.

Install Dependencies
....................

First, you need to install the Python and Node.js dependencies. To do so, run the
following commands from the repository root:

.. code-block:: bash

    poetry install --no-interaction --with docs
    npm install

.. warning::

   Always run :command:`npm install` from the repository root, because otherwise nested
   :file:`node_modules` directories can shadow central dependencies, leading to all kinds
   of hard-to-debug errors. If this already happened, clean up with
   :command:`npm run fix:frontend-install`.


Starting the Development Server
...............................

The standard integrated development command is:

.. code-block:: bash

    npm start

This starts the following components together:

- **Daphne** --- the ASGI web server, running in watch mode
- **Redis** --- the key/value store
- **Maildev** --- a local mail sink for testing email flows
- **MockSAML** --- a local dummy SAML identity provider for testing SSO flows
- **Esbuild** --- frontend and library bundles, rebuilt on every change

The setup closely mirrors a typical production environment, except for the SQLite database,
which follows Django's defaults, and the fake mail and SAML servers.

Once everything is built and running, you can edit the source files. All relevant
parts should automatically rebuild when you save a file. For testing, you can then
reload the page in the browser (e.g. by pressing :kbd:`F5` in most browsers).

Running Tests
.............

Run the full Python test suite, including a coverage report at the end:

.. code-block:: bash

   npm run test

This is a shortcut for:

.. code-block:: bash

   cd src
   poetry run coverage run --rcfile=../pyproject.toml manage.py test
   poetry run coverage report --rcfile=../pyproject.toml -m

If coverage fails, review the ``Missing`` column in the report and add tests for
the flagged lines or branches before opening a PR.


Quality Checks
..............

Run project-wide linting and static analysis checks:

.. code-block:: bash

   npm run check


Building Documentation
......................

To continuously rebuild the documentation when sources change and serve it with
hot-reloading on port ``8885``:

.. code-block:: bash

   npm run docs

To build the documentation once without a live server:

.. code-block:: bash

   npm run docs:build

In both cases, the generated HTML is written to :file:`docs/_build`. Under the hood,
these commands run:

.. code-block:: bash

   poetry run sphinx-autobuild -T -v --port 8885 docs/ docs/_build
   poetry run sphinx-build -T -v docs/ docs/_build

What these options do:

- :option:`-T`: Print tracebacks on errors
- :option:`-v`: Verbose output (``-v -v`` for even more detail)

:option:`--keep-going` is deliberately omitted because it can swallow errors silently.


---------------------
Other Useful Commands
---------------------

Poetry Package Management
.........................

Python dependencies are managed with `Poetry <https://python-poetry.org/>`_, which handles
installation and upgrades of all required external Python packages. All dependencies are declared
in :file:`pyproject.toml`; Poetry also fully automates the use of virtual environments. It is roughly
comparable to npm in the Node.js world. The most important commands are:

- :command:`poetry install` --- Install all dependencies specified in :file:`pyproject.toml`
- :command:`poetry add xyz` --- Add a dependency on library ``xyz``
- :command:`poetry remove xyz` --- Remove the dependency on library ``xyz``
- :command:`poetry lock` --- Update the lock file after manual dependency changes
- :command:`poetry show --tree` --- Display the full dependency graph
- :command:`poetry run xyz` --- Run console command ``xyz`` inside the Python environment
- :command:`poetry env activate` --- Print the shell command to activate the Python environment
- :command:`poetry env use $(which python)` --- Create a new virtual Python environment
- :command:`poetry env list` --- List available environments
- :command:`poetry env remove xyz` --- Delete environment ``xyz``

Run :command:`poetry env activate` to activate the environment directly, and
:command:`deactivate` to leave it.


Django Web Framework
....................

`Django <https://www.djangoproject.com/>`_ is the main server-side framework. It ships with its
own CLI, :command:`django-admin`, and a project-specific wrapper :file:`manage.py` inside the
:file:`src/` directory. Both are functionally identical, but :file:`manage.py` pre-configures the environment
for the current project.

**Root-level commands** --- Run these from outside a Django project directory:

- :command:`django-admin startproject xyz` --- Create a new Django project ``xyz``

.. hint::

   We already created the Django project called ``openbook`` that contains all backend code.
   Normally, you shouldn't need to create another project while working on OpenBook.

**Project directory commands** --- Run these from inside :file:`src/`:

- :command:`./manage.py startapp xyz` --- Add Django app ``xyz`` to the project
- :command:`./manage.py runserver` --- Start the built-in development server
- :command:`./manage.py test` --- Run the unit test suite
- :command:`./manage.py collectstatic` --- Collect static files into :file:`_static/`
- :command:`./manage.py dbshell` --- Open a database shell

After each change to the data model, create and apply migrations:

- :command:`./manage.py makemigrations` --- Generate migration files from model changes
- :command:`./manage.py migrate` --- Apply pending database migrations
- :command:`./manage.py squashmigrations` --- Condense multiple migrations into one before committing


SQLite Shell
............

The command :command:`./manage.py dbshell` drops you into a SQLite shell for direct SQL inspection.
The default SQLite prompt is minimal: it shows no column headers and wraps lines. The following
built-in commands make it more usable:

- :command:`.tables` --- List all available tables
- :command:`.mode column` --- Align output in fixed-width columns
- :command:`.headers on` --- Show column names in query output
- :command:`.quit` --- Exit the SQLite shell (and use a proper tool 😛)

Use a wide terminal window to avoid wrapped lines.

.. tip::

   As a graphical alternative, the VS Code extension *SQLite Viewer* by Florian Klampfer lets
   you browse the database without leaving the editor.


npm and esbuild
...............

OpenBook uses both server-side rendering (Django views and templates) and client-side rendering
(a single-page application for the main UI). Both rely on the npm package registry for client-side
dependencies, which are bundled into distribution files with `esbuild <https://esbuild.github.io/>`_.

The root :file:`package.json` defines an npm workspace so all sub-projects share a single
:file:`node_modules` directory. Each sub-project has its own :file:`package.json` for runtime dependencies,
additional development dependencies and run scripts.

Frequently used scripts in each sub-project:

- :command:`npm run build` --- Build distribution files
- :command:`npm run clean` --- Delete distribution files
- :command:`npm run watch` --- Start watch mode for automatic rebuilds
- :command:`npm run check` --- Run all checks: ESLint, TypeScript, unit tests, security
- :command:`npm start` --- Run from built distribution files

Less commonly used scripts:

- :command:`npm run test` --- Run unit tests only
- :command:`npm run tsc` --- Type-check source code with TypeScript
- :command:`npm run lint` --- Check source code with ESLint
- :command:`npm run lintfix` --- Auto-correct ESLint findings (use with caution)
- :command:`npm run prettier` --- Check source code formatting with Prettier
- :command:`npm run format` --- Auto-correct Prettier findings (use with caution)

