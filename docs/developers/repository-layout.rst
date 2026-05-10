=================
Repository Layout
=================

This page describes the directory layout of the OpenBook source repository. It answers questions
like where to find the different parts, what goes where, and why it is structured like this.

.. contents:: Page Content
   :local:


---------
Top Level
---------

.. code-block:: text

   openbook/
   ├── bin/                         # Build and development tooling scripts
   ├── docker/                      # Docker Compose and web server configuration
   ├── docs/                        # Documentation source (Sphinx / RST)
   └── src/                         # All runtime source code
       ├── manage.py
       ├── openbook/                # Django project (backend)
       │   ├── auth/
       │   ├── content/
       │   ├── core/
       │   ├── local_settings.py    # Site-specific settings (not under version control)
       │   └── settings.py          # Fixed settings for all installations
       ├── frontend/                # TypeScript / Svelte frontend packages
       │   ├── admin/               # Django admin client code
       │   └── app/                 # User-facing SPA
       └── libraries/               # Reusable content block libraries
           ├── core/
           └── ls-compat/

The repository root contains configuration files and four notable directories. :file:`src/` holds all
runtime code, backend, frontend, and libraries, while :file:`docs/` contains the documentation source.
The :file:`bin/` directory holds build scripts, and :file:`docker/` provides container and web server
configuration for deployment.

:file:`docs/`
.............

This directory is the source location for the documentation site. It contains the user guide,
API reference pages, changelog, and maintainer notes.

:file:`src/`
............

All runtime source code lives here. It is home to the Django project, the frontend packages, and
the component libraries. See the sections below for a detailed breakdown.

:file:`bin/`
............

Build and development tooling scripts. These entry points drive the frontend build pipeline
for both the frontend application and the component libraries, as well as the mock SAML identity
provider used in local development.

:file:`docker/`
...............

Example Docker Compose configuration and supporting files for running OpenBook in a containerised
environment. This includes the application :file:`Dockerfile`, the entrypoint script, and Caddy web
server configuration.


-------
Backend
-------

The Django project lives in :file:`src/openbook/`. It is the authoritative entry point for all
server-side logic and is structured as a standard Django project with multiple apps.

:file:`src/manage.py`
.....................

The standard Django management entry point. Use this to run management commands, apply
migrations, and start the development server.

:file:`src/openbook/settings.py`
................................

Base application settings shared across all environments. Treat this as part of the
application code, as administrators normally should not change these settings.


:file:`src/openbook/local_settings.py`
......................................

Deployment-specific settings like database URLs, secret keys, and similar.
This file is not checked into version control.


--------
Frontend
--------

The frontend source lives under :file:`src/frontend/` and is split into two distinct packages.
Both are built with esbuild and TypeScript.

:file:`src/frontend/admin/`
...........................

Client-side code for the Django admin interface. This package enhances the default Django admin
with custom JavaScript and CSS, when a feature cannot be achieved with backend code alone.

:file:`src/frontend/app/`
.........................

The main user-facing single-page application (SPA). This is the primary interface for students and
educators, built with Svelte and TypeScript. It communicates with the Django backend through the
REST API.


---------
Libraries
---------

:file:`src/libraries/` contains component libraries that define reusable content blocks for use in learning
materials. Libraries are npm workspace packages and are consumed by the frontend SPA and, where applicable,
pre-rendered in the backend.

:file:`src/libraries/core/`
...........................

The primary component library, providing the base set of interactive and static content block types
available to educators when authoring textbooks.

:file:`src/libraries/ls-compat/`
................................

A compatibility layer for content blocks originating from earlier versions of the platform, ensuring
that legacy learning materials continue to render correctly.
