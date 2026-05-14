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

.. list-table::
    :width: 100%
    :header-rows: 1

    * - Tool
      - Needed for
    * - Python
      - Running the Django backend and management commands
    * - Poetry
      - Managing Python dependencies and virtual environments
    * - Node.js and npm
      - Workspace orchestration and building frontend assets
    * - Redis
      - Task queue and worker communication
    * - Java Runtime
      - OpenAPI generator tooling
    * - Graphviz
      - Rendering diagrams in the manual

To get from a fresh machine to a working OpenBook setup, use this short workflow.
First you need to install the required tools:

.. tabs::

   .. tab:: Windows

      Download and install these tools from their official pages:

      - `Python <https://www.python.org/downloads/>`_
      - `Node.js (LTS) <https://nodejs.org/en/download>`_
      - `Redis (unofficial Windows port) <https://github.com/redis-windows/redis-windows/releases>`_
      - `Graphviz <https://graphviz.org/download/>`_

      Use the **Python**, **Node.js** and **Graphviz** installers and keep default settings.
      When installing Python and Graphviz, enable  the option to add each to the :envvar:`PATH`
      environment variable.

      Install **Poetry** in PowerShell:

      .. code-block:: powershell

         (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

      Next, add Python's scripts directory to the system :envvar:`PATH` (typically ``%APPDATA%\Python\Scripts``)
      so you can run :command:`poetry` from any directory:

      1. Open the Start menu and search for ``Edit environment variable``.
      2. In the *System variables* section, select ``Path`` and click *Edit*.
      3. Click *New* and add ``%APPDATA%\Python\Scripts``.
      4. Confirm all dialogs with *OK*, then open a new PowerShell window.
      5. Verify the setup with :command:`poetry --version`.

      **Redis** has no official open-source Windows port, but an unofficial port is available.
      Download the ZIP file from the GitHub release page and extract it, for example, to :file:`C:\Program Files\Redis`.
      Add this directory to the system :envvar:`PATH` variable as described above.

      **Java** can be installed using the Windows Package Manager. First, search for the most recent version
      of Microsoft OpenJDK:

      .. code-block:: powershell

         winget search Microsoft.OpenJDK

      Then install the latest version (25 in this example), e.g.:

      .. code-block:: powershell

         winget install Microsoft.OpenJDK.25

   .. tab:: macOS

      macOS requires Homebrew for Redis, which has no official native macOS installer.
      Thus the simplest option is to install the other tools with Homebrew, too.

      .. code-block:: bash

         brew install python@3.12 poetry node redis openjdk@21 graphviz
         brew services start redis

      If you don't have Homebrew installed, visit `brew.sh <https://brew.sh>`_ for setup instructions.

   .. tab:: Linux

      On Debian/Ubuntu, this is a good baseline setup:

      .. code-block:: bash

         sudo apt update
         sudo apt install -y python3 python3-poetry nodejs npm redis-server default-jre graphviz

      If you use another distribution, install equivalent packages with your package manager.

Verify that all tools are available in your shell:

.. code-block:: bash

   python --version || python3 --version
   poetry --version
   node --version
   npm --version
   redis-server --version
   java -version
   dot --version

Set up OpenBook dependencies and initial data from the repository root:

.. code-block:: bash

   poetry install --no-interaction --with docs
   npm install
   npm run init:db

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

All required tools come pre-installed in the containers, including the `Pi Coding Agent <https://pi.dev>`_
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


Initialize Database
...................

Before starting the development server for the first time, or after deleting the :file:`db.sqlite`
file, a new database must be set up. This can be done by running the following command from the
project root:

.. code-block:: bash

   npm run init:db

This executes the following commands in sequence, to create the database, load all fixtures,
install HTML libraries and create a super user with full permissions.

.. code-block:: bash

   cd src
   python manage.py migrate
   python manage.py load_initial_data
   python manage.py install_html_library
   python manage.py createsuperuser

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
   poetry run coverage run --rcfile=../pyproject.toml manage.py test --parallel auto
   poetry run coverage report --rcfile=../pyproject.toml -m

If coverage fails, review the ``Missing`` column in the report and add tests for
the flagged lines or branches before opening a PR.

When hunting down failed tests, it can be useful to run :command:`manage.py test` manually
with one of the following arguments:

.. list-table::
   :width: 100%

   * - **Argument**
     - Description
   * - ``--failfast``
     - Immediately abort after the first failed test
   * - ``openbook_...``
     - Module path to a single test module or class or method

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

- ``-T``: Print tracebacks on errors
- ``-v``: Verbose output (``-v -v`` for even more detail)

``--keep-going`` is deliberately omitted because it can swallow errors silently.

When working on the documentation with :command:`npm run docs` or :command:`npm run docs:build`,
the OpenAPI schemas included in the documentation are automatically regenerated. If needed, the
OpenAPI schemas can also be manually regenerated with :command:`npm run docs:sync-openapi`.

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

