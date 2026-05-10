---
name: ob-django-create-app
description: >
  Use when creating a new OpenBook Django app or deciding whether a backend
  feature belongs in an existing app. Triggers: create app, startapp,
  bounded context, AppConfig, routes.py, INSTALLED_APPS,
  register_api_routes.
argument-hint: Description of the app to be created
user-invocable: true
---

# OpenBook Django App Structure

OpenBook organizes domain features into separate Django apps under
`src/openbook/`. Apps are the unit of ownership for models, admin integration,
REST API endpoints, fixtures, and migration history.

Before creating a new app, first determine whether the feature belongs in an
existing app. Create a new app only for a clearly separate bounded domain.

## Required App Conventions

- All apps live under `src/openbook/<app_label>/`.
- App names and labels use `snake_case`.
- The Django app name is always `openbook.<app_label>`.
- Keep app names short, domain-focused, and stable.
- Register every new app in `INSTALLED_APPS`.
- Every app must provide:
  - `apps.py`
  - `routes.py`
  - `models/`
  - `admin/`
  - `viewsets/`
  - `migrations/`

## Standard App Layout

Use this structure as the default starting point:

```text
src/openbook/<app_label>/
├── __init__.py
├── apps.py
├── routes.py
├── migrations/
│   └── __init__.py
├── models/
│   └── __init__.py
├── admin/
│   └── __init__.py
├── viewsets/
│   └── __init__.py
└── fixtures/
```

Only introduce additional modules such as `services/`, `signals/`,
`management/commands/`, or custom utilities when complexity justifies them.

## Mirrored File Structure

OpenBook organizes feature code around user-visible models.

For each primary model, mirror filenames across layers, e.g.:

* models/learning_goal.py
* admin/learning_goal.py
* viewsets/learning_goal.py

This convention is mandatory unless there is a strong architectural reason not to follow it.

Rules:

* One primary model concern per file.
* Keep filenames aligned across directories.
* Match imports, class names, and route names consistently.
* Prefer discoverability and navigability over abstraction.

## Creating a New App

Create the app under `src/openbook/`:

```bash
cd src
python manage.py startapp <app_name> src/openbook/<app_label>
```

Then immediately:

1. Rename generated placeholders if necessary.
2. Add the app to `INSTALLED_APPS`.
3. Create a proper `AppConfig`.
4. Add `routes.py`.
5. Register routes from `src/openbook/urls.py`.

## apps.py Requirements

Every app must expose an explicit `AppConfig`.

Required pattern:

```python
from django.apps              import AppConfig
from django.utils.translation import gettext_lazy as _


class ExampleApp(AppConfig):
    name  = "openbook.example"
    label = "example"
    verbose_name = _("Example")
```

Rules:

* `name` must equal `openbook.<app_label>`.
* `label` must equal the package name.
* `verbose_name` must be translatable using `_()`.
* Do not omit `label`.
* Use stable identifiers. Renaming labels later is expensive.

## API Route Registration

OpenBook does not use app-local `urls.py` modules for REST APIs.

Instead:

* Each app exposes `register_api_routes()` in `routes.py`.
* Project-level routing happens in `src/openbook/urls.py`.

Required pattern:

```python
def register_api_routes(router, prefix):
    pass
```

Rules:

* Route registration function names follow: `register_<app_label>_api_routes`
* Use the app label consistently in prefixes and imports.
* Register all app routes centrally from `src/openbook/urls.py`.

## Definition of Done

A new app is not complete until all of the following are true:

* App exists under `src/openbook/<app_label>/`
* App is listed in `INSTALLED_APPS`
* `apps.py` defines: `name`, `label`, `verbose_name`
* `routes.py` exists
* `register_api_routes()` exists
* App routes are wired into `src/openbook/urls.py`
* Directory structure follows OpenBook conventions
* Mirrored model/admin/viewset filenames are used consistently

## Anti-Patterns

DO NOT:

* Put unrelated domains into the same app.
* Create apps with vague or overly broad names.
* Introduce compatibility aliases for renamed apps.
* Create deeply nested feature structures prematurely.
* Use inconsistent filenames between models/admin/viewsets.
* Add app-local `urls.py` for REST APIs.
* Omit explicit `AppConfig.label`.
* Mix multiple unrelated models into one large module.
