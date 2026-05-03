=================
Repository Layout
=================

This page describes the directory layout of the OpenBook source repository. It answers questions
like where do you find the different parts, what goes where and why is it structured like this.

.. code-block:: text

   openbook/
   ├── bin/                 # Build and development tooling scripts
   ├── docker/              # Docker Compose and web server configuration
   ├── docs/                # Documentation source (Sphinx / RST)
   └── src/                 # All runtime source code
       ├── manage.py
       ├── openbook/        # Django project (backend)
       │   ├── auth/
       │   ├── content/
       │   └── core/
       ├── frontend/        # TypeScript / Svelte frontend packages
       │   ├── admin/       # Django admin client code
       │   └── app/         # User-facing SPA
       └── libraries/       # Reusable content block libraries
           ├── core/
           └── ls-compat/


---------
Top Level
---------

The repository root contains configuration files and four notable directories. ``src/`` holds all
runtime code — backend, frontend, and libraries — while ``docs/`` contains the documentation source.
The ``bin/`` directory holds build scripts, and ``docker/`` provides container and web server
configuration for deployment.

``docs/``
.........

This directory is the source location for the documentation site. It contains the user guide,
API reference pages, changelog, and maintainer notes.

``src/``
........

All runtime source code lives here. It is home to the Django project, the frontend packages, and
the component libraries. See the sections below for a detailed breakdown.

``bin/``
........

Build and development tooling scripts. These entry points drive the frontend build pipeline
for both the frontend application and the component libraries, as well as the mock SAML identity
provider used in local development.

``docker/``
...........

Example Docker Compose configuration and supporting files for running OpenBook in a containerised
environment. This includes the application ``Dockerfile``, the entrypoint script, and Caddy web
server configuration.


-------
Backend
-------

The Django project lives in ``src/openbook/``. It is the authoritative entry point for all
server-side logic and is structured as a standard Django project with multiple apps.

``src/manage.py``
.................

The standard Django management entry point. Use this to run management commands, apply
migrations, and start the development server.

``src/openbook/settings.py``
............................

Base application settings shared across all environments. Treat this as part of the
application code, as administrators normally should not change these settings.


``src/openbook/local_settings.py``
..................................

Deployment-specific settings like database URLs, secret keys, and similar.
This file is not checked into version control.


--------
Frontend
--------

The frontend source lives under ``src/frontend/`` and is split into two distinct packages.
Both are built with esbuild and TypeScript.

``src/frontend/admin/``
.......................

Client-side code for the Django admin interface. This package enhances the default Django admin
with custom JavaScript and CSS, when a feature cannot be achieved with backend code alone.

``src/frontend/app/``
.....................

The main user-facing single-page application (SPA). This is the primary interface for students and
educators, built with Svelte and TypeScript. It communicates with the Django backend through the REST API.


---------
Libraries
---------

``src/libraries/`` contains component libraries that define reusable content blocks for use in learning
materials. Libraries are npm workspace packages and are consumed by the frontend SPA and, where applicable,
pre-rendered in the backend.

``src/libraries/core/``
.......................

The primary component library, providing the base set of interactive and static content block types
available to educators when authoring textbooks.

``src/libraries/ls-compat/``
............................

A compatibility layer for content blocks originating from earlier versions of the platform, ensuring
that legacy learning materials continue to render correctly.
