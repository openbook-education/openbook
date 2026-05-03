=========================
# Architecture and Design
=========================

This page gives maintainers a practical architecture map for OpenBook. It does
not try to be an exhaustive design specification. Instead, it connects the
main components so you can reason about changes, deployment behavior, and
where to place new code.


----------------
Technology Stack
----------------

TODO: Major dependencies:
    - Backend: Django, DRF, Cellery, Redis, Django-supported SQL database
    - Frontend: TypeScript, Esbuild and Svelte


.. TODO: Rewrite complete document. The text below is not very good.


---------------
System overview
---------------

OpenBook combines a Django backend with a frontend stack that is built and
managed in the same repository.

- The backend is a Django project in ``src/openbook``.
- The frontend assets are split into workspace packages under
  ``src/frontend`` and ``src/libraries``.
- Runtime deployment typically uses Daphne behind a front web server such as
  Caddy, plus PostgreSQL and Redis.

The design intentionally keeps the number of runtime moving parts low while
still supporting APIs, asynchronous communication, and modern frontend builds.


-----------------
Backend structure
-----------------

The backend follows Django's project/app model:

- ``src/manage.py`` is the management entry point.
- ``src/openbook/settings.py`` contains base configuration.
- ``src/openbook/local_settings.py`` is used for deployment-specific overrides.
- Functional units live in app modules such as ``openbook.core``,
  ``openbook.auth``, and ``openbook.content``.

Authentication and API behavior are centered on Django REST Framework,
drf-spectacular, and django-allauth headless flows.


------------------------------
Frontend and library structure
------------------------------

OpenBook uses npm workspaces to coordinate frontend and component library
packages from the repository root:

- ``src/frontend/admin`` for admin-facing frontend assets.
- ``src/frontend/app`` for the user-facing SPA.
- ``src/libraries/core`` for the core textbook runtime.
- ``src/libraries/ls-compat`` for compatibility with legacy lecture-slide.js
  structures.

Build orchestration happens through root ``npm`` scripts and the scripts in
``bin``.


-------------------
Deployment topology
-------------------

Production-like deployments generally follow this pattern:

1. A front web server terminates TLS and serves static/media files.
2. Daphne runs the ASGI application.
3. Django persists data in PostgreSQL.
4. Redis provides channel-layer support and background coordination.

The Docker example under ``docker/`` demonstrates this topology and is a
useful baseline for debugging environment-specific issues.


-----------------
Design principles
-----------------

OpenBook prefers conservative, well-understood infrastructure decisions and
clear separation of concerns. New features should avoid introducing heavy
infrastructure dependencies unless they provide clear operational value and
fit the dependency policy.
