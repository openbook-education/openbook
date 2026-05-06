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
Creating New Models
-------------------

Models are the heart of each Django app. They define the database schema, enforce data integrity,
and provide the Python interface for all persistent data. In OpenBook, every major domain concept
gets its own model file inside the app's ``models/`` directory, mirroring the structure of the
``admin/`` and ``viewsets/`` directories that build on top of it.

Create a Model File
...................

Create one Python file per domain concept inside ``models/``. Closely related helper models ---
such as a translation companion for internationalised text fields --- live in the same file.
Continuing the learning progress example, let's add ``models/learning_goal.py``.

Each model class is built by inheriting the appropriate mixin classes together with any
domain-specific fields. A minimal starting point looks like this:

.. code-block:: python

      from django.db                          import models
      from django.utils.translation           import gettext_lazy as _

      from openbook.core.models.mixins.uuid   import UUIDMixin
      from openbook.core.models.mixins.text   import NameDescriptionMixin
      from openbook.core.models.mixins.active import ActiveInactiveMixin
      from openbook.auth.models.mixins.audit  import CreatedModifiedByMixin


      class LearningGoal(UUIDMixin, NameDescriptionMixin, ActiveInactiveMixin, CreatedModifiedByMixin):
         """A course-specific learning goal with a Bloom taxonomy level."""

         class LevelChoices(models.TextChoices):
            REMEMBER   = "remember",   _("Remember")
            UNDERSTAND = "understand", _("Understand")
            APPLY      = "apply",      _("Apply")
            ANALYZE    = "analyze",    _("Analyze")
            EVALUATE   = "evaluate",   _("Evaluate")
            CREATE     = "create",     _("Create")

         course = models.ForeignKey(
            "openbook_content.Course",
            verbose_name = _("Course"),
            on_delete    = models.CASCADE,
            related_name = "learning_goals",
         )

         level = models.CharField(
            verbose_name = _("Learning Level"),
            max_length   = 16,
            choices      = LevelChoices,
            default      = LevelChoices.UNDERSTAND,
         )

         class Meta:
            verbose_name        = _("Learning Goal")
            verbose_name_plural = _("Learning Goals")
            ordering            = ("course", "name")

         def __str__(self):
            return f"{self.name} ({self.get_level_display()})"

Always list ``UUIDMixin`` first in the inheritance chain, followed by other core mixins, and auth
mixins last. This order keeps Python's Method Resolution Order (MRO) predictable and ensures that
the ``save()`` and ``clean()`` overrides defined in each mixin chain correctly through
``super()``.

Note, how model fields are declared as class attributes using Django's ``models.<FieldType>`` classes.
Each field type maps to a Python value type and a database column type, e.g. ``models.CharField`` for
short text, ``models.TextField`` for longer text, ``models.BooleanField`` for true/false flags,
and ``models.ForeignKey`` for relations.

.. hint::

   In OpenBook, prefer explicit ``verbose_name`` values wrapped in ``_()`` for all user-facing
   fields, so labels in Admin forms and API-driven UIs stay consistent and translatable. Also
   use ``get_level_display()`` in ``__str__()`` whenever a field defines ``choices``. This returns
   the human-readable (and translated) label instead of the raw stored value.

.. seealso::

   Django model field reference:
   https://docs.djangoproject.com/en/stable/ref/models/fields/

   Common field options:
   https://docs.djangoproject.com/en/stable/ref/models/fields/#field-options

Add Meta Class and Utility Methods
..................................

Every model must define an inner ``Meta`` class with at least ``verbose_name`` and
``verbose_name_plural``. Both values must be wrapped in ``_()`` for translation. Add
``ordering`` to define a sensible default sort order, and declare ``indexes`` and
``constraints`` as the domain requires

Additionaly, provide a ``__str__()`` method so the model displays as a human-readable string
in the Admin and in log output. When ``NameDescriptionMixin`` is included it already supplies a
``__str__`` that returns ``self.name``, so override it only when the default output is not
descriptive enough. ``ActiveInactiveMixin`` provides a companion ``__str__`` that returns
``"(inactive)"`` when the object is inactive, which you can compose into a richer string
like shown below.

.. code-block:: python

   class LearningGoal(UUIDMixin, CreatedModifiedByMixin):
      # Field definitions ...

      class Meta:
         verbose_name        = _("Learning Goal")
         verbose_name_plural = _("Learning Goals")
         ordering            = ("course", "name")

         indexes = [
            models.Index(fields=("course", "name")),
         ]

      def __str__(self):
         return f"{self.name} {ActiveInactiveMixin.__str__(self)}".strip()

On top of that you may override additional methods to fine-tune model behaviour as well as
add domain-logic in additional free-style methods. But always consider that domain-logic
methods may modify a model instance's values but should not call ``save()`` to persist the
changes. Calling ``save()`` or any other method modifying the database should be handled at
the call-site.

Add Companion Models for Translations etc.
..........................................

Many OpenBook domain models need language-specific texts. In those cases, keep the main model
language-neutral and store translatable texts in a companion model in the same source file.
This keeps core business fields stable while allowing any number of translations per object.
Use this pattern for companion translation models:

1. Inherit from ``UUIDMixin`` and ``TranslatableMixin``.
2. Add a ``parent`` foreign key to the main model with ``related_name="translations"``.
3. Add only the fields that are truly language-dependent.
4. Inherit the companion model ``Meta`` class from ``TranslatableMixin.Meta``.

Example:

.. code-block:: python

   class LearningGoal(UUIDMixin, NameDescriptionMixin, CreatedModifiedByMixin):
      # Main, language-neutral fields here
      pass


   class LearningGoalText(UUIDMixin, TranslatableMixin):
      parent = models.ForeignKey(
         LearningGoal,
         on_delete    = models.CASCADE,
         related_name = "translations",
      )

      short_title = models.CharField(verbose_name=_("Short Title"), max_length=255)
      summary     = models.TextField(verbose_name=_("Summary"), blank=True, default="")

      class Meta(TranslatableMixin.Meta):
         verbose_name        = _("Learning Goal Text")
         verbose_name_plural = _("Learning Goal Texts")

Keep translation companion models close to their parent model in structure and naming so that
Admin, API serializers, and tests can follow the same conventions across apps.

Export From ``models/__init__.py``
..................................

After creating the model file, import all classes in ``models/__init__.py`` so Django's
app registry discovers it during startup and migration commands include it:

.. code-block:: python

   from .learning_goal import LearningGoal
   from .learning_goal import LearningGoalText

Available Core Model Mixins
...........................

The core app provides abstract mixin classes in ``openbook.core.models.mixins`` that capture
common model patterns. ``UUIDMixin`` must always appear first in the inheritance chain.
Beyond that, inherit only the mixins that match the model's actual requirements.

**UUID primary key** --- ``UUIDMixin`` replaces Django's default auto-increment integer primary
key with a UUID. Including this mixin first in the MRO is mandatory for all OpenBook models.
It prevents predictable IDs in API responses and URLs, and avoids accidental enumeration of
resources by external clients.

**Name and description** --- ``NameDescriptionMixin`` adds name, description, and text format
fields, where the description can be plain text, HTML, or Markdown. Provides a ``__str__`` that
returns ``self.name`` and a ``get_formatted_description()`` helper for rendering.

**Active/inactive flag** --- ``ActiveInactiveMixin`` adds an ``is_active`` boolean field. Its
``__str__`` returns the string "(inactive)" when the object is not active, which is useful for
composing a richer ``__str__`` on the main model.

**Validity time span** --- ``ValidityTimeSpanMixin`` adds start and end date fields with
built-in validation that the end date comes after the start date. Use this for content that is
only valid within a defined calendar window.

**Duration** --- ``DurationMixin`` adds a duration expressed in configurable units: minutes,
hours, days, weeks, months, or years. Use this for time-boxed activities such as assignments or
timed exercises.

**URL-friendly slug** --- ``UniqueSlugMixin`` and ``NonUniqueSlugMixin`` each add a ``slug``
field. Use the globally unique variant when the slug must never repeat across the whole table.
Use the context-scoped variant together with a ``UniqueConstraint`` in the model's ``Meta``
class when uniqueness only applies within a parent context, for example a slug that must be
unique per course but not globally.

**Translation companion marker** --- ``TranslatableMixin`` marks a companion model as a set of
translations for a parent model. Create a separate class holding the translatable text fields
and use the provided ``LanguageField()`` helper for the language reference. See the companion
translations pattern later in this section for a full example.

**File upload metadata** --- ``FileUploadMixin`` is for models that store uploaded files. It
automatically populates file name, file size, and MIME type fields when the model is saved.

Additional Auth Model Mixins
............................

In addition to the core mixins, the auth app adds mixins that connect models to the role-based
permission system. These live in ``openbook.auth.models.mixins``.

**Audit trail** --- ``CreatedModifiedByMixin`` records who created and last modified an object,
and when. The overridden ``save()`` reads the currently logged-in user from the request context
and populates these fields automatically. Add this mixin to most non-trivial models to support
auditing and accountability.

**Permission scope boundary** --- ``ScopedRolesMixin`` makes the model itself a top-level
permission scope. A scope owns an owner and carries relations for roles, role assignments,
enrollment methods, access requests, and public permissions. Use this only for container objects
such as courses — models that define a permission boundary for everything they contain.

**Scope membership** --- ``ScopeMixin`` is for models that belong to a scope rather than define
one. It adds generic foreign key fields pointing at the parent scope object. This is used
internally by models such as enrollment methods and access requests.

**Object-level permission check** --- ``RoleBasedObjectPermissionsMixin`` adds a
``has_obj_perm()`` method for checking object-level permissions on composite models, for example
course materials, where permission checks should be delegated to a parent scope. Override
``get_scope()`` to return the parent object.

.. note::

   In practice most feature models inherit ``UUIDMixin``, one or two content-describing core
   mixins, and ``CreatedModifiedByMixin``. Only top-level container objects that define a
   permission boundary, like courses, also need ``ScopedRolesMixin``.

Common Field Options
....................

In practice, most field declarations combine a type with options such as ``verbose_name``,
``default``, ``choices``, ``null``, ``blank``, ``db_index``, ``unique``, ``help_text``, and
``related_name`` (for relations). Use these options intentionally, because each one affects
validation, database constraints, query performance, or API behavior.

**Human-readable label** --- Always supply an explicit ``verbose_name`` wrapped in ``_()`` so
the label is translatable. It appears in Admin forms, error messages, and API schema
documentation. Without it Django generates a label from the attribute name, which can be
misleading (for example ``"course_id"`` instead of ``"Course"``).

**Database nullability vs. form emptiness** --- ``null`` controls whether the database column
may store NULL; ``blank`` controls whether Django forms and serializers accept an empty value.
For text fields, prefer ``null=False`` and ``blank=True`` when the value is optional, so you
store an empty string rather than mixing two representations of "no value" in the same column.
For non-text fields such as date and time fields, model optional values with both ``null=True``
and ``blank=True``.

**Uniqueness vs. query performance** --- Use ``unique=True`` only when duplicates must be
impossible by business rule, for example a globally unique external ID. That constraint already
creates a database index as a side effect. When duplicate values are allowed but lookups are
frequent — for example filtering by status or slug — use ``db_index=True`` instead.

**Safe initial values** --- Add a ``default`` only when there is one genuinely correct
initial value for the domain. Avoid hiding missing data with an arbitrary default.

**Fixed enumerations** --- Use ``choices`` for small, stable sets of values such as workflow
states, taxonomy levels, or category sets. Define the choices as an inner class on the model
so they travel with the model and are easy to reference from tests and serializers.

**Editorial guidance** --- Add ``help_text`` for any field where an editor might misunderstand
the expected meaning or format. The text appears as a hint beneath the widget in Admin forms.

**Reverse relation name** --- Always set an explicit ``related_name`` on foreign keys and
many-to-many fields. A clear name keeps reverse lookups readable and avoids clashes when the
same model is referenced from multiple places.

Example patterns:

.. code-block:: python

   class ExampleModel(UUIDMixin, CreatedModifiedByMixin):
      title = models.CharField(
         verbose_name = _("Title"),
         max_length   = 255,
         blank        = True,
         default      = "",
      )

      available_until = models.DateTimeField(
         verbose_name = _("Available Until"),
         null         = True,
         blank        = True,
      )

      external_id = models.CharField(
         verbose_name = _("External Id"),
         max_length   = 64,
         unique       = True,
      )

      status = models.CharField(
         verbose_name = _("Status"),
         max_length   = 32,
         db_index     = True,
         choices      = StatusChoices,
      )

      course = models.ForeignKey(
         "openbook_content.Course",
         verbose_name = _("Course"),
         on_delete    = models.CASCADE,
         related_name = "learning_goals",
      )

Checklist Before Moving On
..........................

Before you continue with Admin and API integration, verify that:

1. The model is placed in the correct file under ``models/`` (one concept plus companion models).
2. Required core/auth mixins are inherited, with ``UUIDMixin`` first.
3. User-facing labels (``verbose_name`` and choice labels) are wrapped in ``_()``.
4. Field options are intentional, especially ``null`` vs ``blank`` and ``unique`` vs ``db_index``.
5. ``Meta`` includes at least ``verbose_name`` and ``verbose_name_plural``, plus optional ordering/indexes.
6. ``__str__()`` returns a concise, human-readable identifier.
7. The model is imported in ``models/__init__.py``.


--------------------------
# Adding Models to the Admin
--------------------------

.. NOTE TO COPILOT:
.. make sure that the tutorial follows a logical progression from simple to more complete
.. because, getting this part right, including all the custom classes is central to the OpenBook architecture
.. Each model NEEDS a viewset, serzializers, filters
.. Start with simple example codes and expand from there with ever increasing examples

.. The mixins are central to the OpenBook architecture
.. Readers must know their relevance and how to use them for what to be able to write correct code.
.. Please read their source to understand the background, before drafting the documentation.
.. Also read src/openbook/auth/admin/enrollment_method.py to understand the patterns we are going to document.

- Building upon the previous tutorial, exposing models in the admin
- Every major model should be exposed in the admin
   - To allow administrators to analyze and fix data-related problems
   - To create test data until a full UI has been built
- Minimum steps:
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
# Exposing Models in the REST API
-------------------------------

.. NOTE TO COPILOT:
.. make sure that the tutorial follows a logical progression from simple to more complete
.. because, getting this part right, including all the custom classes is central to the OpenBook architecture
.. Each model NEEDS a viewset, serzializers, filters
.. Start with simple example codes and expand from there with ever increasing examples

.. The mixins are central to the OpenBook architecture
.. Readers must know their relevance and how to use them for what to be able to write correct code.
.. Please read their source to understand the background, before drafting the documentation.
.. Also read src/openbook/auth/viewsets/enrollment_method.py to understand the patterns we are going to document.

- Building upon the previous tutorials, making models available to clients and the SPA via the REST API
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


.. NOTE TO COPILOT: The mixin is important to use to ensure baseline test coverage.
.. Readers must know their relevance and how to use them for what to be able to write correct code.
.. Please read their source to understand the background, before drafting the documentation.
.. Also read src/openbook/auth/tests/test_enrollment_method.py to understand the patterns we are going to document.

- Expanding on the previous examples, test coverage is important to ensure quality and ensure future maintenance
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
