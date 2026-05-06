=============
How To Guides
=============

This page collects various tutorials for often-needed development activities. The tutorials
build upon each other, as usually for each new feature all the below documented steps need
to be carried out.

.. note::

   The repository contains AI agent definitions to assist with these tasks. You can read
   them for additional information. When using AI agents, please still manually check the
   outcome against nearby code and the documentation on this page.

.. contents:: Page Content
   :local:


-----------------
Creating New Apps
-----------------

Domain-specific features for OpenBook live in separate Django apps within the OpenBook Django project,
in line with best-practices recommended by the Django developers. Technically speaking, both are Python
project directories with pre-defined sub-modules (either single Python files or directories with an
``__init__.py`` file --- from Python or Django's point of view, there is no difference). And theoretically
a Django project doesn't need to be split into smaller apps. But the split improves clarity, separation
of concerns and code reuse. Imagine the difference like this:

A Django project is the full server application, while a Django app is a focused domain module inside
that project. In OpenBook, apps are the unit for organizing data models, admin integration, REST API
endpoints, and migration history around one bounded topic. Therefore, the first step, when implementing
a new feature is either to find the right app to extend or to create a new app from scratch. This tutorial
shows how to do the latter.

Create and register a new app
.............................

Create the app with Django, then place it under ``src/openbook`` with a short, domain-specific name.
After that, register it in ``INSTALLED_APPS`` in ``src/openbook/settings.py`` so migrations, admin
discovery, and app startup hooks run automatically.

Imagine, we wanted to create a new app for tracking learning progress. The typical process would be:

.. code-block:: bash

   cd src
   python manage.py startapp learning_goals src/openbook/progress

Then add the app import path to ``INSTALLED_APPS``:

.. code-block:: python

   INSTALLED_APPS = [
       "openbook.core",
       "openbook.auth",
       "openbook.content",

       # New entry for the new app
       "openbook.learning_progress",

       # Existing entries for 3rd-party apps ...
   ]

A typical app layout looks like this:

.. code-block:: text

   src/openbook/learning_progress/
   ├── __init__.py
   ├── apps.py
   ├── routes.py
   ├── migrations/
   │   ├── __init__.py
   │   └── 0001_initial.py
   ├── models/
   ├── __init__.py
   │   └── learning_goal.py
   ├── admin/
   ├── __init__.py
   │   └── learning_goal.py
   ├── viewsets/
   │   ├── __init__.py
   │   └── learning_goal.py
   └── fixtures/
       └── openbook_learning_progress/
           └── example_learning_goals.yaml

In practice, model-heavy apps often grow with additional modules such as tests, custom management
commands, signals, or service classes. Start with the structure above and extend it only when needed.

.. note::

   Note the many files named ``learning_goal.py`` or similar. As we will see in the sub-sequent
   tutorials, most feature apps resolve around database models which are exposed in the Django
   admin and the REST API. The three directories ``models/``, ``admin/`` and ``viewsets/`` serve
   exactly this purpose. To simplify navigation, each file is concerned with exactly one model
   (from a user's perspective) and we mirror the file-structure between most directories.

   .. graphviz::
      :align: center
      :caption: One domain model is mirrored across the main packages of an OpenBook app.

      digraph app_layout {
         graph [bgcolor=transparent, rankdir=TB, nodesep=0.35, ranksep=0.6];
         node [shape=box, style="rounded,filled", fontname="Sans"];

         model  [label="models/learning_goal.py\nDjango model", fillcolor="#e3f2fd", color="#1e88e5"];
         admin  [label="admin/learning_goal.py\nAdmin integration", fillcolor="#e8f5e9", color="#43a047"];
         api    [label="viewsets/learning_goal.py\nREST API integration", fillcolor="#fff3e0", color="#fb8c00"];
         routes [label="routes.py\nRegisters API endpoints", fillcolor="#fce4ec", color="#d81b60"];

         model -> admin [label="same domain object", color="#43a047", fontcolor="#43a047"];
         model -> api   [label="same domain object", color="#fb8c00", fontcolor="#fb8c00"];
         api -> routes  [label="API wiring", color="#d81b60", fontcolor="#d81b60"];
      }

Define ``apps.py`` with explicit metadata
.........................................

Next you need to expose an ``AppConfig`` with a stable ``name`` and explicit ``label``.
Though not strictly required, the label is important because OpenBook uses app labels
in places like fixture model names and generic scope references.

Create the file `app.py` (inside the app directory) with following content:

.. code-block:: python

   from django.apps              import AppConfig
   from django.utils.translation import gettext_lazy as _


   class ProgressApp(AppConfig):
       name = "openbook.learning_progress"
       label = "learning_progress"
       verbose_name = _("Learning Progress")

.. note::

   Note the pattern for the class attribute values. The app name and label must follow
   similar conventions as module names in Python: No spaces, start with a letter,
   `snake_case` capitalization, etc. The name is always ``openbook.<app_label>`` and
   the app label the package name.

   The verbose name is used in the Admin and in other places in the UI. So it must be
   marked with ``_()`` as a translatable text.

Register API routes in ``routes.py``
....................................

OpenBook app structure focuses on models, admin, and REST APIs. We do not define server-rendered
pages and thus typically don't have app-level ``urls.py`` files. Instead, each app provides
API routes through ``routes.py``, and the project registers them from ``src/openbook/urls.py``.
To this end, each app must expose a ``register_api_routes(router, prefix)`` function in
``routes.py``, that registers the URL routes for the REST API endpoints.

Example:

.. code-block:: python

   from .viewsets.goal import GoalViewSet


   def register_api_routes(router, prefix):
       # Will be filled-in later, when REST API viewsets are defined
       pass

Then wire the app-level route registration into ``src/openbook/urls.py`` like so:

.. code-block:: python

   # Existing imports ...
   from .learing_progress.routes import register_api_routes as register_learning_progress_api_routes

   # Existing register_<app_label>_api_routes
   register_learning_progress_api_routes(api_router, "learning_progress")

.. note ::

   Note again the pattern, where the app label is used for consistent naming.

Checklist Before Moving On
..........................

Before implementing models and APIs, verify that:

1. The app lives under ``src/openbook/<app_name>``.
2. The app is listed in ``INSTALLED_APPS``.
3. ``apps.py`` defines ``name``, ``label``, and ``verbose_name``.
4. ``routes.py`` exposes ``register_api_routes(router, prefix)``.
5. ``src/openbook/urls.py`` imports and calls your route registration function.


-------------------
# Creating New Models
-------------------

.. NOTE: The mixins are central to the OpenBook architecture
.. Readers must know their relevance and how to use them for what to be able to write correct code.
.. Please read their source to understand the background, before drafting the documentation.

- Procedure to add new model classes
- Example: ``src/openbook/auth/models/enrollment_method.py`` → read to understand the patterns before you document!
- One major model per source file plus closely related models (e.g. translatable texts)
- Mixin-classes from core app:
   - Important to use them
   - especially UUIDMixin
   - Short overview list
- Additional mixin-classes from auth app → overview list and when used (to allow scoped permissions e.g. within a course)
- Meta class, typical methods like ``str()``
- Import in ``__init__.py``.
- Example code


--------------------------
# Adding Models to the Admin
--------------------------

.. make sure that the tutorial follows a logical progression from simple to more complete
.. because, getting this part right, including all the custom classes is central to the OpenBook architecture
.. Each model NEEDS a viewset, serzializers, filters
.. Start with simple example codes and expand from there with ever increasing examples

.. NOTE: The mixins are central to the OpenBook architecture
.. Readers must know their relevance and how to use them for what to be able to write correct code.
.. Please read their source to understand the background, before drafting the documentation.

- Building upon the previous tutorial, exposing models in the admin
- Every major model should be exposed in the admin
   - To allow administrators to analyze and fix data-related problems
   - To create test data until a full UI has been built
- Example: ``src/openbook/auth/admin/enrollment_method.py`` → read to understand the patterns before you document!
- Absolute minimum steps:
   - File-structure in ``admin/`` matching the ``models/`` structure
   - Minimal class derived from ``CustomModelAdmin`` within a new source file
   - Class derived from ``ScopeResourceMixin`` to allow import/export to various file formats
      - Important to thoroughly test the export/import
   - Import and registration in ``__init__.py``
- Fine-tuning the result: Properties and mixins for fine-tuning
      - list_display
      - list_display_links
      - list_select_related
      - ordering
      - search_fields
      - readonly_fields
      - list_filter
      - fieldsets → field groups via (sets), tabs (Django Unfold extension)
      - add_fieldsets → no fields with automatically created values, most importantly created_modified_by_fieldset, to avoid crashes
- Example codes


-------------------------------
Exposing Models in the REST API
-------------------------------

.. make sure that the tutorial follows a logical progression from simple to more complete
.. because, getting this part right, including all the custom classes is central to the OpenBook architecture
.. Each model NEEDS a viewset, serzializers, filters
.. Start with simple example codes and expand from there with ever increasing examples

.. NOTE: The mixins are central to the OpenBook architecture
.. Readers must know their relevance and how to use them for what to be able to write correct code.
.. Please read their source to understand the background, before drafting the documentation.

- Building upon the previous tutorials, making models available to clients and the SPA via the REST API
- Example: ``src/openbook/auth/viewsets/enrollment_method.py`` → read to understand the patterns before you document!
- File-structure in ``viewsets/`` matching the ``models/`` structure
- At least minimal ``ViewSet`` class extending ``ModelViewSetMixin``
   - Optionally actions and OpenAPI extensions
- Mixins in package ``openbook.drf.viewsets``
   - Important to use them
   - Especially ``ModelViewSetMixin``
   - Short overview list
- No import in ``__init__.py``, but in ``../routes.py`` to define the URL routes.
- For each model also a custom serializers
   - derived from ``FlexFieldsModelSerializer``
   - ``drf_flex_fields2``: Client can choose the fields and whether to receive foreign keys or deep structures
- For each model also custom filter class to support querying (searching)
   - derived from ``FilterSet`` (must come last after all mixins)
   - mixins in core and auth apps → overview (when to add which)
- Example codes for each class (simple viewset, full viewset, serializer, filter class)


-----------------
Creating Fixtures
-----------------

Fixtures provide a reproducible baseline of data for local development and first-time deployments.
Use YAML fixtures to keep the data readable, reviewable, and easy to maintain in version control.

.. rst-class:: spaced-list

1. Create and prepare the data first in Django Admin or the application UI until it reflects the state you
   want to ship as a fixture.

2. Then export only the data you need into a dedicated files under ``fixtures/<app>/`` using the following
   command --- including natural keys, to avoid unstable references with some of the external models:

   .. code-block:: bash

      python manage.py dumpdata --format yaml --natural-foreign --natural-primary myapp

2. After export, treat the fixture as source code. Reorder entries logically, remove unnecessary ``null``
   values, and add comments where relationships are not obvious.

3. When the fixture is stable, integrate it into the initial data loading workflow so other developers
   can bootstrap a complete project state with one command. The related management command lives in
   ``src/openbook/core/management/commands/load_initial_data.py``.

.. important::

   Keep the file extension as ``.yaml``, because Django does not discover other extensions as fixtures.

.. note::

   Natural keys are useful for export stability, but we do not use them as model-wide primary references.
   Adding natural keys across all models considerably increases model and manager complexity and often
   requires new uniqueness constraints that do not fit the domain model.

   But generic relations remain the deciding limitation. Even with natural keys, ``object_id`` values in
   generic relations still point to concrete object identifiers. In practice, this means UUIDs remain part
   of the fixture data and quite heavy-weight custom serializers would be required to remove them consistently.

   UUIDs keep this trade-off manageable. Unlike auto-increment IDs, UUIDs are stable enough for fixture
   exchange across environments and significantly reduce import collisions.


------------------
# Writing Unit Tests
------------------

.. NOTE: The mixin is important to use to ensure baseline test coverage.
.. Readers must know their relevance and how to use them for what to be able to write correct code.
.. Please read their source to understand the background, before drafting the documentation.

- Expanding on the previous examples, test coverage is important to ensure quality and ensure future maintenance
- Example: ``src/openbook/auth/tests/test_enrollment_method.py`` → read to understand the patterns before you document!
- Unit tests usually organized around models, therefore same directory structure as in ``models``
- Basic example for creating unit tests with the Django test framework
- Try to test contract and behaviour and not implementation
- For models:
   - Naming convention / typically required classes:
      - ``<Model>_Test_Mixin``: Shared setup logic, e.g. creating mock database entries
      - ``<Model>_Model_Tests``: Testing the low-level database model
      - ``<Model>_ViewSet_Tests``: Testing the higher-level REST application
   - Mixin-class ``ModelViewSetTestMixin`` defines baseline tests for all models
      - Tests derived from class properties
         - Document what each property does
      - Additional test methods as needed, especially for viewset actions
