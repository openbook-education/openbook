=============================
How To Implement New Features
=============================

This page collects various tutorials for often-needed development activities. The tutorials
build upon each other and together cover the full development cycle for adding a new feature:
from creating a Django app and defining the data model, through admin integration, all the way
to exposing the model via the REST API so the frontend can consume it. Following them in order
for each new feature ensures nothing is missed.

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
in line with best practices recommended by the Django developers. Technically speaking, both are Python
project directories with predefined submodules (either single Python files or directories with a
:file:`__init__.py` file --- from Python's or Django's point of view, there is no difference). Theoretically,
a Django project does not need to be split into smaller apps. But the split improves clarity, separation
of concerns and code reuse. Imagine the difference like this:

A Django project is the full server application, while a Django app is a focused domain module inside
that project. In OpenBook, apps are the unit for organizing data models, admin integration, REST API
endpoints, and migration history around one bounded topic. Therefore, the first step when implementing
a new feature is either to find the right app to extend or to create a new app from scratch. This tutorial
shows how to do the latter.

Create and Register a New App
.............................

Create the app with Django, then place it under :file:`src/openbook` with a short, domain-specific name.
After that, register it in :attr:`INSTALLED_APPS` in :file:`src/openbook/settings.py` so migrations, admin
discovery, and app startup hooks run automatically.

Imagine we wanted to create a new app for tracking learning progress. The typical process would be:

.. code-block:: bash

   cd src
   python manage.py startapp learning_goals openbook/progress

Then add the app import path to :attr:`INSTALLED_APPS`:

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
   │   ├── __init__.py
   │   └── learning_goal.py
   ├── admin/
   │   ├── __init__.py
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

   Note the many files named :file:`learning_goal.py` or similar. As we will see in the subsequent
   tutorials, most feature apps revolve around database models that are exposed in the Django
   admin and the REST API. The three directories :file:`models/`, :file:`admin/`, and :file:`viewsets/` serve
   exactly this purpose. To simplify navigation, each file is concerned with exactly one model
   (from a user's perspective), and we mirror the file structure between most directories.

   .. graphviz::
      :align: center
      :caption: Mirrored source structure for the model and all layers above

      digraph app_layout {
         graph [bgcolor=transparent, rankdir=TB, nodesep=0.35, ranksep=0.6];
         node [shape=box, style="rounded,filled", fontname="Sans", fontsize=11, width=2.8, height=0.5, fixedsize=true];

         model  [label=<<B>models/learning_goal.py</B><BR/>Django model>, fillcolor="#e3f2fd", color="#1e88e5"];
         admin  [label=<<B>admin/learning_goal.py</B><BR/>Admin integration>, fillcolor="#e8f5e9", color="#43a047"];
         api    [label=<<B>viewsets/learning_goal.py</B><BR/>REST API integration>, fillcolor="#fff3e0", color="#fb8c00"];
         routes [label=<<B>routes.py</B><BR/>Registers API endpoints>, fillcolor="#fce4ec", color="#d81b60"];

         model -> admin [color="#43a047"];
         model -> api   [color="#fb8c00"];
         api -> routes  [color="#d81b60"];
      }

Define :file:`apps.py` With Explicit Metadata
.............................................

Next you need to expose an :class:`AppConfig` with a stable :attr:`name` and explicit :attr:`label`.
Though not strictly required, the label is important because OpenBook uses app labels
in places like fixture model names and generic scope references.

Create the file :file:`apps.py` inside the app directory with the following content:

.. code-block:: python

   from django.apps              import AppConfig
   from django.utils.translation import gettext_lazy as _


   class ProgressApp(AppConfig):
       name = "openbook.learning_progress"
       label = "openbook_learning_progress"
       verbose_name = _("Learning Progress")

.. note::

   Note the pattern for the class attribute values. The app name and label must follow
   conventions similar to Python module names: no spaces, start with a letter,
   ``snake_case`` capitalization, etc. The name is always ``openbook.<app_label>``, and
   the app label is ``openbook_`` followed by the package name.

   The verbose name is used in the admin and in other places in the UI. So it must be
   marked with :func:`_` as a translatable text.

Register API Routes in :file:`routes.py`
........................................

OpenBook app structure focuses on models, admin, and REST APIs. We do not define server-rendered
pages and thus typically do not have app-level :file:`urls.py` files. Instead, each app provides
API routes through :file:`routes.py`, and the project registers them from :file:`src/openbook/urls.py`.
To this end, each app must expose a :func:`register_api_routes` function in :file:`routes.py`
that registers the URL routes for the REST API endpoints.

Example:

.. code-block:: python

   from .viewsets.goal import GoalViewSet


   def register_api_routes(router, prefix):
       # Will be filled in later, when REST API viewsets are defined
       pass

Then wire the app-level route registration into :file:`src/openbook/urls.py` like so:

.. code-block:: python

   # Existing imports ...
   from .learing_progress.routes import register_api_routes as register_learning_progress_api_routes

   # Existing register_<app_label>_api_routes
   register_learning_progress_api_routes(api_router, "learning_progress")

.. note::

   Note again the pattern, where the app label is used for consistent naming.

Checklist Before Moving On
..........................

Before implementing models and APIs, verify that:

1. The app lives under ``src/openbook/<app_name>``.
2. The app is listed in :attr:`INSTALLED_APPS`.
3. :file:`apps.py` defines :attr:`name`, :attr:`label`, and :attr:`verbose_name`.
4. :file:`routes.py` exposes :func:`register_api_routes`.
5. :file:`src/openbook/urls.py` imports and calls your route registration function.


-------------------
Creating New Models
-------------------

Models are the heart of each Django app. They define the database schema, enforce data integrity,
and provide the Python interface for all persistent data. In OpenBook, every major domain concept
gets its own model file inside the app's :file:`models/` directory, mirroring the structure of the
:file:`admin/` and :file:`viewsets/` directories that build on top of it.

Create the Model
................

Create one Python file per domain concept inside :file:`models/`. Closely related helper models ---
such as a translation companion for internationalised text fields --- live in the same file.
Continuing the learning progress example, let's add :file:`models/learning_goal.py`.

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

Always list :class:`UUIDMixin` first in the inheritance chain, followed by other core mixins, and auth
mixins last. This order keeps Python's Method Resolution Order (MRO) predictable and ensures that
the :meth:`save` and :meth:`clean` overrides defined in each mixin chain correctly through
:func:`super`.

Note how model fields are declared as class attributes using Django's :class:`models.<FieldType>` classes.
Each field type maps to a Python value type and a database column type, e.g. :class:`models.CharField` for
short text, :class:`models.TextField` for longer text, :class:`models.BooleanField` for true/false flags,
and :class:`models.ForeignKey` for relations.

.. hint::

   In OpenBook, prefer explicit :attr:`verbose_name` values wrapped in :func:`_` for all user-facing
   fields, so labels in admin forms and API-driven UIs stay consistent and translatable. Also
   use :meth:`get_level_display` in :meth:`__str__` whenever a field defines :attr:`choices`. This returns
   the human-readable (and translated) label instead of the raw stored value.

.. seealso::

   Django model field reference:
   https://docs.djangoproject.com/en/stable/ref/models/fields/

   Common field options:
   https://docs.djangoproject.com/en/stable/ref/models/fields/#field-options

Add Meta Class and Utility Methods
..................................

Every model must define an inner :class:`Meta` class with at least :attr:`verbose_name` and
:attr:`verbose_name_plural`. Both values must be wrapped in :func:`_` for translation. Add
:attr:`ordering` to define a sensible default sort order, and declare :attr:`indexes` and
:attr:`constraints` as the domain requires.

Additionally, provide a :meth:`__str__` method so the model displays as a human-readable string
in the admin and in log output. When :class:`NameDescriptionMixin` is included it already supplies a
:meth:`__str__` that returns ``self.name``, so override it only when the default output is not
descriptive enough. :class:`ActiveInactiveMixin` provides a companion :meth:`__str__` that returns
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

On top of that, you may override additional methods to fine-tune model behaviour as well as
add domain logic in additional freestyle methods. But always consider that domain-logic
methods may modify a model instance's values but should not call :meth:`save` to persist the
changes. Calling :meth:`save` or any other method that modifies the database should be handled at
the call site.

Add Companion Models for Translations etc.
..........................................

Many OpenBook domain models need language-specific texts. In those cases, keep the main model
language-neutral and store translatable texts in a companion model in the same source file.
This keeps core business fields stable while allowing any number of translations per object.
Use this pattern for companion translation models:

1. Inherit from :class:`UUIDMixin` and :class:`TranslatableMixin`.
2. Add a :attr:`parent` foreign key to the main model with ``related_name="translations"``.
3. Add only the fields that are truly language-dependent.
4. Inherit the companion model :class:`Meta` class from :class:`TranslatableMixin.Meta`.

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
admin, API serializers, and tests can follow the same conventions across apps.

Export From :file:`models/__init__.py`
......................................

After creating the model file, import all classes in :file:`models/__init__.py` so Django's
app registry discovers it during startup and migration commands include it:

.. code-block:: python

   from .learning_goal import LearningGoal
   from .learning_goal import LearningGoalText

Available Core Model Mixins
...........................

The core app provides abstract mixin classes in :mod:`openbook.core.models.mixins` that capture
common model patterns. :class:`UUIDMixin` must always appear first in the inheritance chain.
Beyond that, inherit only the mixins that match the model's actual requirements.

**UUID primary key** --- :class:`UUIDMixin` replaces Django's default auto-increment integer primary
key with a UUID. Including this mixin first in the MRO is mandatory for all OpenBook models.
It prevents predictable IDs in API responses and URLs, and avoids accidental enumeration of
resources by external clients.

**Name and description** --- :class:`NameDescriptionMixin` adds name, description, and text format
fields, where the description can be plain text, HTML, or Markdown. Provides a :meth:`__str__` that
returns ``self.name`` and a :meth:`get_formatted_description` helper for rendering.

**Active/inactive flag** --- :class:`ActiveInactiveMixin` adds an :attr:`is_active` boolean field. Its
:meth:`__str__` returns the string "(inactive)" when the object is not active, which is useful for
composing a richer :meth:`__str__` on the main model.

**Validity time span** --- :class:`ValidityTimeSpanMixin` adds start and end date fields with
built-in validation that the end date comes after the start date. Use this for content that is
only valid within a defined calendar window.

**Duration** --- :class:`DurationMixin` adds a duration expressed in configurable units: minutes,
hours, days, weeks, months, or years. Use this for time-boxed activities such as assignments or
timed exercises.

**URL-friendly slug** --- :class:`UniqueSlugMixin` and :class:`NonUniqueSlugMixin` each add a :attr:`slug`
field. Use the globally unique variant when the slug must never repeat across the whole table.
Use the context-scoped variant together with a :class:`UniqueConstraint` in the model's :class:`Meta`
class when uniqueness only applies within a parent context, for example a slug that must be
unique per course but not globally.

**Translation companion marker** --- :class:`TranslatableMixin` marks a companion model as a set of
translations for a parent model. Create a separate class holding the translatable text fields
and use the provided :class:`LanguageField` helper for the language reference. See the companion
translations pattern later in this section for a full example.

**File upload metadata** --- :class:`FileUploadMixin` is for models that store uploaded files. It
automatically populates file name, file size, and MIME type fields when the model is saved.

Additional Auth Model Mixins
............................

In addition to the core mixins, the auth app adds mixins that connect models to the role-based
permission system. These live in :mod:`openbook.auth.models.mixins`.

**Audit trail** --- :class:`CreatedModifiedByMixin` records who created and last modified an object,
and when. The overridden :meth:`save` reads the currently logged-in user from the request context
and populates these fields automatically. Add this mixin to most non-trivial models to support
auditing and accountability.

**Permission scope boundary** --- :class:`ScopedRolesMixin` makes the model itself a top-level
permission scope. A scope owns an owner and carries relations for roles, role assignments,
enrollment methods, access requests, and public permissions. Use this only for container objects
such as courses --- models that define a permission boundary for everything they contain.

**Scope membership** --- :class:`ScopeMixin` is for models that belong to a scope rather than define
one. It adds generic foreign key fields pointing at the parent scope object. This is used
internally by models such as enrollment methods and access requests.

**Object-level permission check** --- :class:`RoleBasedObjectPermissionsMixin` adds a
:meth:`has_obj_perm` method for checking object-level permissions on composite models, for example
course materials, where permission checks should be delegated to a parent scope. Override
:meth:`get_scope` to return the parent object.

.. note::

   In practice most feature models inherit :class:`UUIDMixin`, one or two content-describing core
   mixins, and :class:`CreatedModifiedByMixin`. Only top-level container objects that define a
   permission boundary, like courses, also need :class:`ScopedRolesMixin`.

Common Field Options
....................

In practice, most field declarations combine a type with options such as :attr:`verbose_name`,
:attr:`default`, :attr:`choices`, :attr:`null`, :attr:`blank`, :attr:`db_index`, :attr:`unique`, :attr:`help_text`, and
:attr:`related_name` (for relations). Use these options intentionally, because each one affects
validation, database constraints, query performance, or API behavior.

**Human-readable label** --- Always supply an explicit :attr:`verbose_name` wrapped in :func:`_` so
the label is translatable. It appears in admin forms, error messages, and API schema
documentation. Without it Django generates a label from the attribute name, which can be
misleading (for example ``"course_id"`` instead of ``"Course"``).

**Database nullability vs. form emptiness** --- :attr:`null` controls whether the database column
may store NULL; :attr:`blank` controls whether Django forms and serializers accept an empty value.
For text fields, prefer ``null=False`` and ``blank=True`` when the value is optional, so you
store an empty string rather than mixing two representations of "no value" in the same column.
For non-text fields such as date and time fields, model optional values with both ``null=True``
and ``blank=True``.

**Uniqueness vs. query performance** --- Use ``unique=True`` only when duplicates must be
impossible by business rule, for example a globally unique external ID. That constraint already
creates a database index as a side effect. When duplicate values are allowed but lookups are
frequent --- for example filtering by status or slug --- use ``db_index=True`` instead.

**Safe initial values** --- Add a :attr:`default` only when there is one genuinely correct
initial value for the domain. Avoid hiding missing data with an arbitrary default.

**Fixed enumerations** --- Use :attr:`choices` for small, stable sets of values such as workflow
states, taxonomy levels, or category sets. Define the choices as an inner class on the model
so they travel with the model and are easy to reference from tests and serializers.

**Editorial guidance** --- Add :attr:`help_text` for any field where an editor might misunderstand
the expected meaning or format. The text appears as a hint beneath the widget in admin forms.

**Reverse relation name** --- Always set an explicit :attr:`related_name` on foreign keys and
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

Create Migrations
.................

After defining or changing models, create a migration file and apply it to the database.
In OpenBook, do this from the :file:`src/` directory so :file:`manage.py` can discover
the project settings and app registry correctly.

Run :mod:`makemigrations` for your app label first. Continuing the example from above,
that label is ``openbook_learning_progress``:

.. code-block:: bash

   cd src
   python manage.py makemigrations openbook_learning_progress

This creates a new migration file under :file:`migrations/` (for example
:file:`0002_add_learning_goal_level.py`) whenever Django detects schema changes.
When you update models later, run the same command again. Django then creates the next
numbered migration file that captures only the new changes.

Apply all unapplied migrations with :mod:`migrate`:

.. code-block:: bash

   python manage.py migrate

To verify migration state for one app, use:

.. code-block:: bash

   python manage.py showmigrations openbook_learning_progress

The output marks applied migrations with ``[X]`` and pending ones with ``[ ]``.

.. important::

   Do not edit or rewrite existing migration history after it has been shared with
   other developers. Instead, create a new migration that moves the schema from the
   current state to the next state.

.. hint::

   Before committing, run :mod:`makemigrations` once more to ensure no model changes
   are left without a migration file.

Checklist Before Moving On
..........................

Before you continue with admin and API integration, verify that:

1. The model is placed in the correct file under :file:`models/` (one concept plus companion models).
2. Required core/auth mixins are inherited, with :class:`UUIDMixin` first.
3. User-facing labels (:attr:`verbose_name` and choice labels) are wrapped in :func:`_`.
4. Field options are intentional, especially :attr:`null` vs :attr:`blank` and :attr:`unique` vs :attr:`db_index`.
5. :class:`Meta` includes at least :attr:`verbose_name` and :attr:`verbose_name_plural`, plus optional ordering/indexes.
6. :meth:`__str__` returns a concise, human-readable identifier.
7. The model is imported in :file:`models/__init__.py`.
8. Migrations have been created and tested.


--------------------------
Adding Models to the Admin
--------------------------

Django Admin is the primary tool for administrators and developers to inspect live data, diagnose
problems, and create test content during development before a full UI exists. For this reason,
every model should have an admin integration. The work follows the same file-mirroring pattern
as models and viewsets: one source file per domain concept in the :file:`admin/` directory, wired
together through :file:`__init__.py`.

Create the Admin File
.....................

To integrate a model into the Django Admin, create a new file in the :file:`admin/` directory with
the same name as its source file in the :file:`models/` directory. Within the new file, define a
class that inherits from :class:`CustomModelAdmin`, imported from :mod:`openbook.admin`. This base class
combines three things, which is why, unlike in traditional Django projects, you never touch
Django's built-in :class:`ModelAdmin` class directly:

1. Django Unfold for the styled admin UI, and
2. DjangoQL for advanced search expressions in the change list,
3. Django Import/Export for CSV, YAML, and XLSX data exchange.

A minimal admin class needs only the :attr:`model`, :attr:`list_display`, :attr:`ordering`, and
:attr:`search_fields` properties to link it to the model class and name the fields used
in the overview list. Again, using learning goals as an example, the file would be
named :file:`admin/learning_goal.py` (like the model file) and have the following content:

.. code-block:: python

   from openbook.admin         import CustomModelAdmin
   from ..models.learning_goal import LearningGoal


   class LearningGoalAdmin(CustomModelAdmin):
       """Admin view for learning goals."""
       model         = LearningGoal
       list_display  = ["name", "course", "level", "is_active"]
       ordering      = ["course", "name"]
       search_fields = ["name", "course__name"]

This is already functional: the change list shows the configured columns, results are sortable
and searchable, and the default form --- not declared in the class --- renders all editable fields.
Isn't Django great? 🙂

.. important::

   Always import models from the file in which they are defined, e.g. ``..models.learning_goal``.
   Never import them from ``..models`` to reduce the risk of circular imports.

Register in :file:`__init__.py`
...............................

Once the class exists, register it in :file:`admin/__init__.py`:

.. code-block:: python

   from openbook.admin import admin_site
   from .learning_goal import LearningGoalAdmin
   from ..             import models

   admin_site.register(models.LearningGoal, LearningGoalAdmin)

The order of :meth:`register()` calls determines the order in which models appear in the admin
sidebar. So, register models in a logical order that makes sense to administrators.

Configuring the Change List
...........................

The following admin class attributes control the change list behaviour. Look at other admin
classes nearby to see how they are typically used and play around with their values to achieve
best results.

.. important::

   We treat the admin as a first-class citizen, as if it was the primary user interface for
   all users. Because, for administrators it really *is* the primary user interface to
   work with the models.

**Visible columns** --- :attr:`list_display` sets which fields appear as columns. Keep it focused:
show the fields needed to identify and distinguish records at a glance.

**Clickable links** --- :attr:`list_display_links` specifies which columns act as links to the
edit page. Without it, only the first column is a link by default. To simplify navigation a
little, try to make all fields clickable.

**Related field prefetching** --- :attr:`list_select_related` names the Foreign Key fields
that Django should join in the same query as the list, avoiding one extra query per row.
This usually enhances performance considerably.

**Default sort** --- :attr:`ordering` sets the default sort order for the change list. Mirror the
:attr:`ordering` declared in the model's :class:`Meta` class to keep behaviour consistent.

**Full-text search** --- :attr:`search_fields` drives the DjangoQL search bar. Use double
underscore notation to traverse relations: ``"course__name"`` searches the related course's
name.

**Filter sidebar** --- :attr:`list_filter` populates the right-hand filter panel. Use plain field
names for simple boolean or choice fields, and ``(field, RelatedOnlyFieldListFilter)`` tuples
for Foreign Key fields where you want to restrict the list to values that are actually in use.

**Read-only fields** --- :attr:`readonly_fields` marks fields that should be visible in the edit
form but cannot be changed by the admin user. Always include the audit trail field names here
so they are visible but protected from accidental edits.

Audit Trail Integration
.......................

When a model uses :class:`CreatedModifiedByMixin`, import the four helper constants from
:mod:`openbook.auth.admin.mixins.audit` and spread them into the relevant admin class attributes:

.. code-block:: python

   from openbook.auth.admin.mixins.audit import created_modified_by_fields
   from openbook.auth.admin.mixins.audit import created_modified_by_fieldset
   from openbook.auth.admin.mixins.audit import created_modified_by_filter
   from openbook.auth.admin.mixins.audit import created_modified_by_related


   class LearningGoalAdmin(CustomModelAdmin):
       """Admin view for learning goals."""
       model               = LearningGoal
       resource_classes    = [LearningGoalResource]
       list_display        = ["name", "course", "level", "is_active", *created_modified_by_fields]
       list_select_related = [*created_modified_by_related]
       list_filter         = ["level", "is_active", *created_modified_by_filter]
       readonly_fields     = [*created_modified_by_fields]
       ordering            = ["course", "name"]
       search_fields       = ["name", "course__name"]

The four constants expand as follows:

**Column names** --- :attr:`created_modified_by_fields` is a list of four field names:
``created_by``, ``created_at``, ``modified_by``, and ``modified_at``. Spread it into
:attr:`list_display` to show audit columns in the change list, and into :attr:`readonly_fields` to
prevent manual edits.

**Prefetch hints** --- :attr:`created_modified_by_related` lists the two Foreign Key names for the
user relations. Spread it into :attr:`list_select_related` to avoid N+1 queries when the list renders.

**Filter sidebar** --- :attr:`created_modified_by_filter` is a list of filter entries (plain
strings and ``(field, FilterClass)`` tuples). Spread it into :attr:`list_filter`.

**Fieldset** --- :attr:`created_modified_by_fieldset` is a ready-made fieldset tuple rendered as
a tab. Always append it as the last entry in :attr:`fieldsets`.

Organising the Edit Form with Fieldsets
.......................................

By default Django Admin renders all editable fields in a single unstyled block. Fieldsets
group fields into named sections and can optionally render as Django Unfold tabs, making
longer forms easier to navigate. To this end, define :attr:`fieldsets` for the edit/change view
and optionally -- when different -- :attr:`add_fieldsets` for the create view.

.. caution::

   When both :attr:`fieldsets` and :attr:`add_fieldsets` are present, the two must not be identical.
   The latter must omit auto-populated fields such as the audit trail, because those fields
   do not exist yet on first save and their presence causes a crash.

.. code-block:: python

   class LearningGoalAdmin(CustomModelAdmin):
       """Admin view for learning goals."""
       # ... list attributes from above ...

       fieldsets = [
           (None, {
               "fields": [
                   ("course", "level"),
                   ("name", "is_active"),
               ],
           }),
           (_("Description"), {
               "classes": ["tab"],
               "fields": ["description", "text_format"],
           }),
           created_modified_by_fieldset,
       ]

       # The same as fieldsets but without created_modified_by_fieldset.
       # Can be omitted for models with no readonly fields
       add_fieldsets = [
           (None, {
               "fields": [
                   ("course", "level"),
                   ("name", "is_active"),
               ],
           }),
           (_("Description"), {
               "classes": ["tab"],
               "fields": ["description", "text_format"],
           }),
       ]

A few conventions to follow:

**Field grouping** --- Pass a tuple inside the ``"fields"`` list to place multiple fields side
by side on the same row: ``("course", "level")`` renders both on one line.

**Tabs** --- Add ``"classes": ["tab"]`` to a fieldset to render it as a Django Unfold tab. Use
tabs for secondary or less frequently edited groups such as description text, validity
settings, or audit information.

**Audit fieldset** --- Always end :attr:`fieldsets` with :attr:`created_modified_by_fieldset` when the
model uses :class:`CreatedModifiedByMixin`. Never include it in :attr:`add_fieldsets`.

Inline Views
............

Related objects such as translation companion models can be embedded directly in the parent
model's change page using inline classes. This is more ergonomic than requiring administrators
to navigate to a separate list to manage translations. To do so, define a :class:`TabularInline`
(or :class:`StackedInline` for more complex layouts) in the same admin file and reference it in the
parent admin class via :attr:`inlines`:

.. code-block:: python

   from unfold.admin           import TabularInline
   from ..models.learning_goal import LearningGoalText


   class _LearningGoalTextInline(TabularInline):
       """Inline for translated texts of a learning goal."""
       model               = LearningGoalText
       fields              = ["language", "short_title", "summary"]
       ordering            = ["language"]
       extra               = 0
       show_change_link    = True
       tab                 = True
       verbose_name        = _("Translation")
       verbose_name_plural = _("Translations")


   class LearningGoalAdmin(CustomModelAdmin):
       """Admin view for learning goals."""
       # ...
       inlines = [_LearningGoalTextInline]

Our conventions are:

**No empty placeholder** --- Always set :attr:`extra` to ``0`` to suppress the empty placeholder rows
that Django renders by default.

**Link to full admin page** -- If the inlined model has a proper admin page, set
:attr:`show_change_link` to ``True`` so that administrators can open the inline record on its own page
for more detailed work.

**Render as tabs** --- Consider setting :attr:`tab` to ``True`` to render the inline as a separate Django
Unfold tab, keeping the main form uncluttered.

**Prefix private classes** --- Prefix inline class names with an underscore to signal that they are
private implementation details of the file.

Import/Export Support
.....................

In OpenBook, every admin class should support file-based data import/export so that administrators
can export data for review, import test data, or migrate entries between environments. This requires
a resource class that must be derived from :class:`ImportExportModelResource` (in :mod:`openbook.admin`)
and declare the field list in its inner :class:`Meta` class. Wire it into the admin class via the
:attr:`resource_classes` property like so:

.. code-block:: python

   from openbook.admin         import CustomModelAdmin
   from openbook.admin         import ImportExportModelResource
   from ..models.learning_goal import LearningGoal


   class LearningGoalResource(ImportExportModelResource):
       """Import/export resource for learning goals."""
       class Meta:
           model  = LearningGoal
           fields = [
               "id", "delete",
               "course", "name", "level", "is_active",
               "description", "text_format",
           ]


   class LearningGoalAdmin(CustomModelAdmin):
       """Admin view for learning goals."""
       model            = LearningGoal
       resource_classes = [LearningGoalResource]   # Resource class above
       list_display     = ["name", "course", "level", "is_active"]
       ordering         = ["course", "name"]
       search_fields    = ["name", "course__name"]

.. note::

   Mind the square brackets around the resource class.

Always include ``"id"`` and ``"delete"`` as the first two fields. The ``delete`` column is a
convention from :class:`ImportExportModelResource` that lets users mark rows for deletion (provided
the file rows contain valid IDs) by setting the value in the file to ``true``.

For foreign keys, boolean fields, or many-to-many fields that
cannot be represented as plain text, add a :class:`Field` declaration with an appropriate widget
class. The advanced patterns subsection covers this for scope-related fields.

.. seealso::

   Advanced Import/Export patterns:
   https://django-import-export.readthedocs.io/en/latest/advanced_usage.html

Advanced: Scope-specific Patterns
..................................

Models that use :class:`ScopeMixin` (i.e. belong to a permission scope) or :class:`ScopedRolesMixin`
(i.e. define a permission scope) require additional mixins for the form and resource classes.
All of these live in :mod:`openbook.auth.admin.mixins.scope`.

**Scope-member models** --- When a model references a scope via :class:`ScopeMixin`, inherit the
resource class from :class:`ScopeResourceMixin` instead of :class:`ImportExportModelResource`. This
mixin handles import and export of the scope reference, resolving scope objects by slug during
import. For the form, inherit from :class:`ScopeFormMixin` to replace the raw UUID widget with a
dynamically loaded select box that shows scope objects by name and restricts scope type choices
to valid options.

.. code-block:: python

   from openbook.auth.admin.mixins.scope import ScopeFormMixin
   from openbook.auth.admin.mixins.scope import ScopeResourceMixin


   class EnrollmentMethodResource(ScopeResourceMixin):
       class Meta:
           model  = EnrollmentMethod
           fields = [
               "id", "delete",
               *ScopeResourceMixin.Meta.fields,
               "name", "role", "is_active",
           ]


   class EnrollmentMethodForm(ScopeFormMixin):
       class Meta:
           model  = EnrollmentMethod
           fields = "__all__"


   class EnrollmentMethodAdmin(CustomModelAdmin):
       form             = EnrollmentMethodForm
       resource_classes = [EnrollmentMethodResource]
       # ...

**Scope-owner models** --- When a model defines a permission scope via :class:`ScopedRolesMixin`,
inherit the resource class from :class:`ScopedRolesResourceMixin` to handle export of the owner and
public permissions fields. For the form, inherit from :class:`ScopedRolesFormMixin` to restrict
visible permissions to those allowed for the scope type.

.. code-block:: python

   from openbook.admin                   import ImportExportModelResource
   from openbook.auth.admin.mixins.scope import ScopedRolesFormMixin
   from openbook.auth.admin.mixins.scope import ScopedRolesResourceMixin


   class CourseResource(ScopedRolesResourceMixin, ImportExportModelResource):
       class Meta:
           model  = Course
           fields = [
               "id", "delete",
               "slug", "name",
               *ScopedRolesResourceMixin.Meta.fields,
           ]


   class CourseForm(ScopedRolesFormMixin):
       class Meta:
           model  = Course
           fields = "__all__"


   class CourseAdmin(CustomModelAdmin):
       form             = CourseForm
       resource_classes = [CourseResource]
       # ...

.. important::

   Note that :class:`ScopedRolesResourceMixin` must come before :class:`ImportExportModelResource` in the
   inheritance chain so that its field declarations take precedence.

**Scope-role fields** --- Models that combine a scope reference with a role field additionally
need :class:`ScopeRoleFieldFormMixin` on the form class to restrict the role choices to roles
defined within the selected scope. The corresponding inline class should inherit
:class:`ScopeRoleFieldInlineMixin` to apply the same restriction inside inline forms.

.. code-block:: python

   from django.contrib.contenttypes.admin import GenericTabularInline
   from unfold.admin                       import TabularInline

   from openbook.auth.admin.mixins.scope   import ScopeFormMixin
   from openbook.auth.admin.mixins.scope   import ScopeRoleFieldFormMixin
   from openbook.auth.admin.mixins.scope   import ScopeRoleFieldInlineMixin


   class EnrollmentMethodForm(ScopeFormMixin, ScopeRoleFieldFormMixin):
       class Meta:
           model  = EnrollmentMethod
           fields = "__all__"

       class Media:
           css = {"all": [*ScopeFormMixin.Media.css["all"], *ScopeRoleFieldFormMixin.Media.css["all"]]}
           js  = [*ScopeFormMixin.Media.js, *ScopeRoleFieldFormMixin.Media.js]


   class EnrollmentMethodInline(ScopeRoleFieldInlineMixin, GenericTabularInline, TabularInline):
       model       = EnrollmentMethod
       ct_field    = "scope_type"
       ct_fk_field = "scope_uuid"
       fields      = ["name", "role", "is_active"]
       extra       = 0

When both :class:`ScopeFormMixin` and :class:`ScopeRoleFieldFormMixin` are needed, merge their :class:`Media`
declarations explicitly as shown above. The same form class is then wired into the admin class
via the :attr:`form` attribute.

The module also exports the helper constants :attr:`scope_type_filter` and
:attr:`permissions_fieldset`, which can be spread into :attr:`list_filter` and :attr:`fieldsets`
respectively, in the same way as the audit trail helpers.

.. code-block:: python

   from openbook.auth.admin.mixins.scope import permissions_fieldset
   from openbook.auth.admin.mixins.scope import scope_type_filter


   class CourseAdmin(CustomModelAdmin):
       list_filter = [
           scope_type_filter,
           # ...
       ]

       fieldsets = [
           # ...
           permissions_fieldset,
           created_modified_by_fieldset,
       ]

Checklist Before Moving On
..........................

Before continuing to REST API integration, verify that:

1. The admin file is placed under ``admin/``, mirroring the model file path.
2. The admin class inherits from :class:`CustomModelAdmin`.
3. A resource class is defined and listed in :attr:`resource_classes`.
4. Audit trail constants are used when :class:`CreatedModifiedByMixin` is in the model's MRO.
5. :attr:`readonly_fields` includes the audit trail field names.
6. Both :attr:`fieldsets` and :attr:`add_fieldsets` are defined, and :attr:`add_fieldsets` omits the audit fieldset.
7. Companion models (e.g. translations) are covered by an inline class.
8. The admin class is registered in :file:`admin/__init__.py` in the correct position.

.. seealso::

   Django Admin reference:
   https://docs.djangoproject.com/en/stable/ref/contrib/admin/

   ModelAdmin list display options:
   https://docs.djangoproject.com/en/stable/ref/contrib/admin/#modeladmin-options

   Django Admin actions:
   https://docs.djangoproject.com/en/stable/ref/contrib/admin/actions/

   Django Import/Export documentation:
   https://django-import-export.readthedocs.io/en/latest/


-------------------------------
Exposing Models in the REST API
-------------------------------

OpenBook uses Django REST Framework to build a REST API that the frontend and external clients can consume.
To pull this off, every model needs three things:

1. a **ViewSet** that handles HTTP requests,
2. a **Serializer** that translates between Python objects and JSON, and
3. a **FilterSet** class that enables clients to query the list endpoint.

Building on the previous tutorials, this section explains how to work with Django REST Framework and some
OpenBook utilities to expose a model through the REST API.

Create the ViewSet
..................

In this tutorial we are using the learning goals model from the tutorials above and expose it
via the REST API. To do so, create a file called :file:`viewsets/learning_goal.py`, again following
the convention to mirror the file structure of the ``models/`` and ``admin/`` directories, and
put the following minimal ViewSet inside:

.. code-block:: python

   from drf_spectacular.utils   import extend_schema
   from rest_framework.viewsets import ModelViewSet

   from openbook.drf.viewsets   import ModelViewSetMixin
   from openbook.drf.viewsets   import with_flex_fields_parameters
   from ..models.learning_goal  import LearningGoal


   @extend_schema(
       extensions={
           "x-app-name":   "Learning Progress",
           "x-model-name": "Learning Goals",
       }
   )
   @with_flex_fields_parameters()
   class LearningGoalViewSet(ModelViewSetMixin, ModelViewSet):
       __doc__ = "Learning goals for a course"

       queryset         = LearningGoal.objects.all()
       serializer_class = LearningGoalSerializer   # not yet defined
       filterset_class  = LearningGoalFilter       # not yet defined
       ordering         = ["course", "name"]
       search_fields    = ["name", "description", "course__name"]

.. note::

   We will cover the :class:`LearningGoalSerializer` and :class:`LearningGoalFilter` classes soon.
   They must be defined at the beginning of the same file for the example to work.

From top to bottom, this code snippet does the following:

**OpenAPI schema extension** --- The class decorator :func:`@extend_schema` adds a new section to
the OpenAPI web service documentation. This keeps all related endpoints concerning a given model
nicely together in the API browser. Similarly, the :attr:`__doc__` attribute defines the long description
shown in the documentation.

**Flex fields parameters** --- The class decorator :func:`@with_flex_fields_parameters` adds the
``_fields``, ``_omit``, and ``_expand`` query parameters to the OpenAPI schema so clients know
how to request only the fields they need. The implementation is handled by the filterset class.

**Mixin and base class** --- The ViewSet class must inherit from :class:`ModelViewSetMixin` and
:class:`ModelViewSet` in exactly this order. The order is important so that the mixin can fill and
validate the model instance before saving, which in turn allows Django's object-level permission
checks to run during creation --- when no database record exists yet.

**Queryset** --- :attr:`queryset` defines the base database query for all actions. Almost always
you want to set it to ``<Model>.objects.all()``. This defines the maximum data that someone
with all permissions can retrieve. Django REST Framework automatically adds further filters
for permissions and more.

**Serializer and FilterSet classes** --- :attr:`serializer_class` points to the serializer that converts
model instances to JSON and validates incoming data. :attr:`filterset_class` points to the filter class
that parses the URL query parameters and narrows the queryset accordingly. Both are defined in the
same file and covered in detail in the sections below.

**Ordering** --- :attr:`ordering` sets the default sort order for list responses. Mirror the
:attr:`ordering` declared in the model's :class:`Meta` class so that the API and the admin behave
consistently. Clients can override the sort order at request time using the ``ordering`` query
parameter.

**Search fields** --- :attr:`search_fields` drives the full-text search available via the ``search``
query parameter. Use double-underscore notation to traverse relations, e.g. ``"course__name"``
to search the name of the related course. Keep this list focused on the fields that are meaningful
for users to search by.

.. hint::

   In OpenBook, models by default are not accessible without authentication and proper permissions.
   This makes sense most of the time, but doesn't work for the landing page and other public areas.

   If your model must be accessible without login, add :class:`AllowAnonymousListRetrieveViewSetMixin`
   before :class:`ModelViewSetMixin` in the inheritance chain.
   This mixin returns :class:`AllowAny` permissions for the ``list`` and ``retrieve`` actions while delegating
   all other permission checks to the ViewSet's default permission classes.

Create the Serializer
.....................

A ViewSet class handles HTTP requests and maps them to RESTful endpoints. But it doesn't know how
to represent a model's data in a data format like JSON or how to convert raw JSON data back into
a model instance. These tasks are delegated to Serializer classes.

In OpenBook Serializer classes are tightly coupled to the ViewSets. For this reason we keep both
in the same file, defining the Serializer first (because in Python a class cannot be used before
it is defined). As a second peculiarity, OpenBook integrates the :mod:`drf-flex-fields2` library to
allow clients to request only those fields they need. A basic implementation looks like this:

.. code-block:: python

   from openbook.drf.flex_serializers  import FlexFieldsModelSerializer
   from openbook.auth.serializers.user import UserField
   from ..models.learning_goal         import LearningGoal


   class LearningGoalSerializer(FlexFieldsModelSerializer):
       __doc__ = "Learning Goal"

       created_by  = UserField(read_only=True)
       modified_by = UserField(read_only=True)

       class Meta:
           model = LearningGoal

           fields = [
               "id", "course",
               "name", "description", "text_format",
               "level", "is_active",
               "created_by", "created_at", "modified_by", "modified_at",
           ]

           read_only_fields = ["id", "created_at", "modified_at"]

           expandable_fields = {
               "course":      "openbook.content.viewsets.course.CourseSerializer",
               "created_by":  "openbook.auth.viewsets.user.UserSerializer",
               "modified_by": "openbook.auth.viewsets.user.UserSerializer",
           }

As a bare minimum, serializer classes must contain an inner :class:`Meta` class with the :attr:`model` property.
Everything else is, in theory, optional. Still, we follow the following conventions:

**Explicit field list** --- Always declare :attr:`fields` explicitly to prevent accidentally exposing
sensitive model data. Never use ``"__all__"``. Start the list with ``"id"`` and end with the audit
trail fields so the JSON output is predictable and consistent across all endpoints.

**Explicit read-only fields** --- Declare :attr:`read_only_fields` for every field that must not be
writable via the API. At a minimum this includes ``"id"``, ``"created_at"``, and ``"modified_at"``,
since they are populated automatically by the database or by :class:`CreatedModifiedByMixin`.

**Expandable fields** --- By default, foreign keys are returned with their raw database values.
However, OpenBook allows the client to append something like ``?_expand=course`` to the request
URL to expand them into full nested objects. This is enabled by :attr:`expandable_fields` which
references the dotted import path string of the respective Serializers. For many-to-many relations,
use the tuple form with ``{"many": True}`` as the second element:

.. code-block:: python

   expandable_fields = {
       "permissions": ("openbook.auth.viewsets.permission.PermissionSerializer", {"many": True}),
   }

.. important::

   Always reference serializers from other files with dotted import path strings, as shown above.
   Never directly import the serializers to avoid circular imports, which are not allowed in Python.

**Custom serializer fields** --- For Foreign Key fields where a raw ID is not meaningful to API
consumers, add custom field classes as shown above with :attr:`created_by` and :attr:`modified_by`.
The auth app ships several ready-made fields for the most common cases:

- :class:`UserField` returns the username,
- :class:`RoleField` returns the role slug, and
- :class:`ScopeTypeField` returns the fully-qualified model string such as ``"openbook_content.course"``.

The same pattern -- a custom field class that overrides :meth:`to_internal_value` and :meth:`to_representation` --
can be applied to any foreign key that needs a human-readable representation. But only spend
the time when it has clear advantages, not just because UUIDs don't look pretty.

.. hint::

   For scope-owner models that implement :class:`ScopedRolesMixin`, inherit :class:`ScopedRolesSerializerMixin`
   before :class:`FlexFieldsModelSerializer`. This mixin injects the :attr:`owner`, :attr:`public_permissions`,
   :attr:`role_assignments`, :attr:`enrollment_methods`, and :attr:`access_requests` fields along with their
   expandable variants. Spread its :class:`Meta` field lists to avoid duplication:

   .. code-block:: python

      from openbook.auth.serializers.mixins.scope import ScopedRolesSerializerMixin


      class CourseSerializer(ScopedRolesSerializerMixin, FlexFieldsModelSerializer):
         created_by  = UserField(read_only=True)
         modified_by = UserField(read_only=True)

         class Meta:
            model = Course

            fields = [
                  "id", "slug", "name", "description", "text_format",
                  *ScopedRolesSerializerMixin.Meta.fields,
                  "created_by", "created_at", "modified_by", "modified_at",
            ]

            read_only_fields = [
                  "id",
                  *ScopedRolesSerializerMixin.Meta.read_only_fields,
                  "created_at", "modified_at",
            ]

            expandable_fields = {
                  **ScopedRolesSerializerMixin.Meta.expandable_fields,
                  "created_by":  "openbook.auth.viewsets.user.UserSerializer",
                  "modified_by": "openbook.auth.viewsets.user.UserSerializer",
            }

Create the Filter Class
.......................

In OpenBook every ViewSet class references a FilterSet class defined in the same file so clients can
not only request a list of model entries but search and narrow the list with query parameters. For this
the FilterSet class inherits one or more optional mixin classes followed by :class:`FilterSet` as the very
last base class. Again, the ordering is important.

.. code-block:: python

   from django_filters.filterset           import FilterSet
   from openbook.auth.filters.mixins.audit import CreatedModifiedByFilterMixin
   from ..models.learning_goal             import LearningGoal


   class LearningGoalFilter(CreatedModifiedByFilterMixin, FilterSet):
       class Meta:
           model  = LearningGoal
           fields = {
               "course":    ("exact",),
               "level":     ("exact",),
               "is_active": ("exact",),
               **CreatedModifiedByFilterMixin.Meta.fields,
           }

The :attr:`fields` dictionary maps field names to tuples of supported lookup expressions. Use
``("exact",)`` for equality checks and ``("exact", "lte", "gte")`` for date or numeric fields that
benefit from range queries. Try to cover as many fields as makes sense for clients to filter against.

As always, for cross-cutting concerns, the auth app provides mixins. These are roughly identical
to the mixins used in the model definitions:

**Audit trail filters** --- :class:`CreatedModifiedByFilterMixin` adds :attr:`created_by` and :attr:`modified_by`
character filters resolved by username, plus date-range lookups for :attr:`created_at` and :attr:`modified_at`.
Use it for any model that includes :class:`CreatedModifiedByMixin`.

**Scope-member filters** --- :class:`ScopeFilterMixin` adds :attr:`scope_type` and :attr:`scope_uuid` filters for
models that implement :class:`ScopeMixin`. The ``scope_type`` parameter accepts either a numeric content-type
primary key or a fully-qualified model string such as ``"openbook_content.course"``.

**Scope-owner filters** --- :class:`ScopedRolesFilterMixin` adds an :attr:`owner` filter resolved by username.
Use it for models that implement :class:`ScopedRolesMixin`.

**Permission filters** --- :class:`PermissionsFilterMixin` and :class:`PermissionFilterMixin` filter by Django
permission strings in the form ``"app_label.codename"``. The former targets M2M permission relations;
the latter targets a single FK permission field.

In some very special cases, a field cannot be mapped to a standard lookup expression. You then need
to define a new property for the field and pass it a filter method like so:

.. code-block:: python

   from django_filters.filters import CharFilter


   class EnrollmentMethodFilter(ScopeFilterMixin, CreatedModifiedByFilterMixin, FilterSet):
       # Explicit filter field
       role = CharFilter(method="role_filter")

       class Meta:
           model  = EnrollmentMethod
           fields = {
               # The field is included, but the match types are deliberately empty
               "role": (),
               ...
           }

       # Custom filter logic for the field
       def role_filter(self, queryset, name, value):
           return queryset.filter(role__slug=value)

The method receives the queryset and the filter value and returns a filtered queryset. Use this pattern
for any filter that must traverse a relation or apply logic that standard lookups cannot express.

Register API Routes
...................

As a final step, edit :file:`routes.py` to register the new ViewSet with the Django REST Framework router:

.. code-block:: python

   from .viewsets.learning_goal import LearningGoalViewSet


   def register_api_routes(router, prefix):
       router.register(f"{prefix}/learning_goals", LearningGoalViewSet, basename="learning_goal")

The :attr:`basename` argument is used to generate the URL names for reverse lookups, such as ``learning_goal-list``
and ``learning_goal-detail``. Use the model name in ``snake_case`` as the convention throughout OpenBook.

Advanced: Custom Actions
........................

Use custom actions when you need endpoints beyond the standard CRUD methods provided by
:class:`ModelViewSet`. Define them with :func:`@action` from :mod:`rest_framework.decorators`.

The :attr:`detail` flag controls whether the endpoint targets one object (``True``) or the full
collection (``False``). :attr:`methods` defines the allowed HTTP verbs, :attr:`url_path` defines the
URL suffix, and :attr:`permission_classes` can override permissions for that action only.

Annotate every custom action with :func:`@extend_schema` so the OpenAPI output documents the
request and response format correctly.

.. code-block:: python

   from drf_spectacular.utils      import extend_schema
   from drf_spectacular.utils      import inline_serializer
   from rest_framework.decorators  import action
   from rest_framework.permissions import AllowAny
   from rest_framework.response    import Response
   from rest_framework.serializers import CharField


   class EnrollmentMethodViewSet(ModelViewSetMixin, ModelViewSet):
       ...

       @extend_schema(
           operation_id = "auth_enrollment_method_enroll",
           summary      = "Enroll User",
           responses    = RoleAssignmentSerializer,
           request      = inline_serializer(
               name   = "EnrollActionRequestSerializer",
               fields = {"passphrase": CharField(required=False)},
           ),
       )
       @action(detail=True, methods=["put"], url_path="enroll", permission_classes=[AllowAny])
       def enroll(self, request, pk=None):
           """Self-enrollment of the current user via this enrollment method."""
           enrollment_method = self.get_object()
           role_assignment   = enrollment_method.enroll(
               user             = request.user,
               passphrase       = request.data.get("passphrase", None),
               check_permission = True,
           )
           return Response(RoleAssignmentSerializer(role_assignment).data)

Checklist Before Moving On
..........................

Before continuing to fixtures and tests, verify that:

1. The ViewSet file is in ``viewsets/``, named after the model file.
2. The ViewSet inherits :class:`ModelViewSetMixin` before :class:`ModelViewSet`.
3. The :func:`@extend_schema` and :func:`@with_flex_fields_parameters` decorators are present.
4. All required attributes are set: :attr:`queryset`, :attr:`serializer_class`, :attr:`filterset_class`, :attr:`search_fields`.
5. The serializer extends :class:`FlexFieldsModelSerializer`.
6. The serializer includes ``"id"`` and audit fields in ``read_only_fields``.
7. ``expandable_fields`` is declared for all FK and M2M relations.
8. The filter class has :class:`FilterSet` last in its MRO and includes all applicable filter mixins.
9. The ViewSet is registered in :file:`routes.py` (not :file:`__init__.py`).

.. seealso::

   Django REST Framework ViewSet reference:
   https://www.django-rest-framework.org/api-guide/viewsets/

   DRF Flex Fields 2 documentation:
   https://drf-flex-fields2.readthedocs.org

   DRF Spectacular documentation:
   https://drf-spectacular.readthedocs.io/en/latest/

   Django Filters documentation:
   https://django-filter.readthedocs.io/en/stable/

-----------------
Creating Fixtures
-----------------

Fixtures provide a reproducible baseline of data for local development and first-time deployments.
Use YAML fixtures to keep the data readable, reviewable, and easy to maintain in version control.

.. rst-class:: spaced-list

1. Create and prepare the data first in Django Admin or the application UI until it reflects the state you
   want to ship as a fixture.

2. Then export only the data you need into a dedicated file under ``fixtures/<app>/`` using the following
   command --- including natural keys, to avoid unstable references with some of the external models:

   .. code-block:: bash

      python manage.py dumpdata --format yaml --natural-foreign --natural-primary openbook_learning_progress

2. After export, treat the fixture as source code. Reorder entries logically, remove unnecessary ``null``
   values, and add comments where relationships are not obvious.

3. When the fixture is stable, integrate it into the initial data loading workflow so other developers
   can bootstrap a complete project state with one command. The related management command lives in
   :file:`src/openbook/core/management/commands/load_initial_data.py`.

.. important::

   Keep the file extension as ``.yaml``, because Django does not discover other extensions as fixtures.

.. note::

   Natural keys are useful for export stability, but we do not use them as model-wide primary references.
   Adding natural keys across all models considerably increases model and manager complexity and often
   requires new uniqueness constraints that do not fit the domain model.

   But generic relations remain the decisive limitation. Even with natural keys, ``object_id`` values in
   generic relations still point to concrete object identifiers. In practice, this means UUIDs remain part
   of the fixture data, and quite heavyweight custom serializers would be required to remove them consistently.

   UUIDs keep this trade-off manageable. Unlike auto-increment IDs, UUIDs are stable enough for fixture
   exchange across environments and significantly reduce import collisions.


------------------
Writing Unit Tests
------------------

Test coverage is the quality gate for everything built in the previous tutorials. A well-tested feature
can be refactored, extended, and maintained with confidence. The guiding principle is to test observable
contracts and behaviour, not internal implementation details. Test what a class *promises* --- the errors
it raises, the objects it returns, the database state it produces --- and leave the question of *how*
it delivers that promise to the implementation.

Tests are usually organized around models where every test module follows the same three-class pattern.
For a learning goal model, the file would be :file:`tests/learning_goal.py`, and the class names would be
:class:`LearningGoal_Test_Mixin`, :class:`LearningGoal_Model_Tests`, and :class:`LearningGoal_ViewSet_Tests`.

.. rst-class:: spaced-list

1. **<Model>_Test_Mixin** holds the shared :meth:`setUp` logic: creating users, parent objects, and
   the fixture records required by both test classes below it. It contains no ``test_*`` methods and
   serves purely as a reusable setup provider.

2. **<Model>_Model_Tests** tests low-level model behaviour: validation errors raised by
   :meth:`clean`, the return values and side-effects of domain methods, and any permission checks
   enforced directly on the model.

3. **<Model>_ViewSet_Tests** tests the HTTP contract of the REST API: status codes, search,
   sorting, pagination, field expansion, and the full CRUD lifecycle.

Write the Test Mixin
....................

Every test class needs a consistent, well-known database state before it can make meaningful
assertions. Without a shared baseline, each test class would have to recreate the same users,
parent objects, and fixture records independently, leading to duplication and drift. The test
mixin solves this by centralising that setup in a single :meth:`setUp` method that both
``<Model>_Model_Tests`` and ``<Model>_ViewSet_Tests`` inherit.

.. code-block:: python

   from openbook.auth.middleware.current_user import reset_current_user
   from openbook.auth.models.user             import User
   from ..models.learning_goal                import LearningGoal


   class LearningGoal_Test_Mixin:
       def setUp(self):
           super().setUp()
           reset_current_user()

           # Setup mock data and save it to instance attributes
           self.user = User.objects.create_user(
               username = "student",
               email    = "student@test.com",
               password = "password",
           )

           self.goal_active = LearningGoal.objects.create(
               name      = "Understand mixins",
               is_active = True,
           )

           self.goal_inactive = LearningGoal.objects.create(
               name      = "Master serializers",
               is_active = False,
           )

.. important::
   Always call :meth:`super().setUp()` first, then :func:`reset_current_user` to clear the request-scoped
   current-user context so that audit-trail fields set in one test do not bleed into another.

   Also, keep the mixin free of ``test_*`` methods. Any test logic placed here would run twice ---
   once for each subclass --- and may produce unexpected interactions between the model tests and the
   ViewSet tests.

Write Model Tests
.................

The model test class validates the low-level domain logic that lives directly on the model. This
is where you confirm that the model enforces its own rules: that :meth:`clean` rejects invalid data,
that domain methods return the right objects, that side-effects on related records occur as
promised, and that the correct exceptions are raised when preconditions are violated. These tests
run entirely in Python without HTTP --- they are fast, focused, and independent of the REST layer.

Inherit from the mixin first and :class:`TestCase` last, so that Python's method resolution order (MRO)
calls the mixin's :meth:`setUp` before Django's test infrastructure:

.. code-block:: python

   from django.core.exceptions import ValidationError
   from django.test            import TestCase


   class LearningGoal_Model_Tests(LearningGoal_Test_Mixin, TestCase):
       """
      Tests for the :class:`LearningGoal` model.
       """

       def test_inactive_goal_raises_on_enroll(self):
           """
           Enrolling against an inactive goal raises :class:`ValidationError`.
           """
           with self.assertRaises(ValidationError):
               self.goal_inactive.enroll(user=self.user)

       def test_complete_returns_assignment(self):
           """
           :meth:`complete` returns the created completion record.
           """
           result = self.goal_active.complete(user=self.user)
           self.assertIsNotNone(result)
           self.assertEqual(result.goal, self.goal_active)

Except for the self-written mixin class, this is a straightforward Django unit test class.
Good candidates for tests are:

- :meth:`clean` validation rules,
- domain method return types and return values,
- database side-effects (rows created or deleted),
- exceptions raised under invalid conditions.

Give each test method a docstring that reads as a one-sentence specification that becomes the
failure message when the test breaks.

.. hint::

   Prefer one focused assertion per test method. A test that checks five things at once gives you
   a pass/fail result but no useful signal about *which* contract was broken.

Write ViewSet Tests
...................

The ViewSet test class verifies the full HTTP contract that clients depend on. Where model tests
check Python-level behaviour, ViewSet tests confirm that the right status codes are returned, that
authentication and authorisation are enforced, that list responses support search, sorting, and
pagination, and that create, update, and delete operations produce the expected database state.
Writing these tests by hand for every endpoint would be tedious and error-prone; OpenBook's
:class:`ModelViewSetTestMixin` generates the repetitive baseline tests automatically so developers
can focus on the edge cases specific to each model.

:class:`LearningGoal_ViewSet_Tests` tests the REST API layer. The bulk of the work is handled
automatically by OpenBook's :class:`ModelViewSetTestMixin`, imported from :mod:`openbook.test`.
For every configured operation it produces three test methods at class-creation time:

.. rst-class:: spaced-list

- An unauthenticated request that must return 401 or 403.
- An authenticated but unauthorised request that must return 403 or 404 for single objects
  or an empty list for the ``list`` action.
- An authorised request that must return the expected status code and produce the expected
  database state.

For the ``list`` action it additionally generates tests for search, sorting, and pagination. For
``retrieve`` it generates an expand-fields test and a 404 test for an unknown primary key. For
``update`` and ``partial_update`` it verifies that every field named in ``"updates"`` carries the
expected value after the call. For ``destroy`` it checks that the object no longer exists.

All of this runs without a single manual test method. Providing the class attributes below is
enough to activate the entire baseline suite:

.. code-block:: python

   from django.test        import TestCase
   from openbook.test      import ModelViewSetTestMixin
   from ..models.goal      import LearningGoal


   class LearningGoal_ViewSet_Tests(ModelViewSetTestMixin, LearningGoal_Test_Mixin, TestCase):
       """
      Tests for the :class:`LearningGoalViewSet` REST API.
       """
       base_name         = "learning_goal"
       model             = LearningGoal
       count             = 2
       search_string     = "mixins"
       search_count      = 1
       sort_field        = "name"
       expandable_fields = ["created_by", "modified_by"]

From top to bottom this defines:

**Router base name** --- :attr:`base_name` is used to reverse URL names such as
``learning_goal-list`` and ``learning_goal-detail``. It must match the ``basename`` argument
passed to the router in :file:`routes.py`.

**Model class** --- :attr:`model` lets the mixin derive permission strings automatically, for
example ``openbook_learning_progress.view_learninggoal``.

**Expected list count** --- :attr:`count` is the number of results the ``list`` endpoint must return
when the test user has full permissions. Set it to the number of objects :meth:`setUp` creates that
are visible to the requesting user. Use a negative value to skip the count assertion.

**Search configuration** --- :attr:`search_string` and :attr:`search_count` configure the search test.
The mixin calls the ``list`` endpoint with ``?_search=<search_string>`` and asserts that exactly
``search_count`` results are returned.

**Sort and pagination field** --- :attr:`sort_field` names the field used for sort and pagination
tests. The mixin calls the ``list`` endpoint with ``?_sort=<sort_field>`` and verifies the
results are in order, then runs a pagination test with ``?_page_size=1&_page=1``.

**Expandable relation names** --- :attr:`expandable_fields` lists the relation names to test with
``?_expand=``. Append ``[]`` to a name for many-relations so the mixin expects a list of objects
rather than a single object.

Disable Unsupported Operations
..............................

Set ``"supported": False`` for an operation to assert that the endpoint returns 405 (Method Not
Allowed). This is useful when a ViewSet intentionally omits ``destroy`` or another standard
action:

.. code-block:: python

   class LearningGoal_ViewSet_Tests(ModelViewSetTestMixin, LearningGoal_Test_Mixin, TestCase):
       ...
       operations = {
           "destroy": {
               "supported": False,
           },
       }

Override Permission Checks
..........................

When a model is visible without authentication because a scope grants public permissions, set
``"model_permission": ()`` to skip the permission check for that operation in the ViewSet tests:

.. code-block:: python

   class LearningGoal_ViewSet_Tests(ModelViewSetTestMixin, LearningGoal_Test_Mixin, TestCase):
       ...
       operations = {
           "list": {
               "model_permission": (),
           },
       }

Provide Request Data and Verify Updates
.......................................

Operations that write data need request bodies and post-save assertions. Declare these in the
:attr:`operations` dictionary by overriding only the keys that differ from the defaults:

.. code-block:: python

   class LearningGoal_ViewSet_Tests(ModelViewSetTestMixin, LearningGoal_Test_Mixin, TestCase):
       ...
       def setUp(self):
           super().setUp()
           self.url_list   = reverse("learning_goal-list")
           self.url_detail = reverse("learning_goal-detail", args=[str(self.goal_active.pk)])

       def pk_found(self):
           return self.goal_active.id

       def get_create_request_data(self):
           return {
               "name":      "New Learning Goal",
               "is_active": True,
           }

       def get_update_request_data(self):
           return {
               "name":      "Updated Goal",
               "is_active": False,
           }

       operations = {
           "create": {
               "request_data": get_create_request_data,
           },
           "update": {
               "request_data": get_update_request_data,
               "updates": {
                   "name":      "Updated Goal",
                   "is_active": False,
               },
           },
           "partial_update": {
               "request_data": {"is_active": False},
               "updates":      {"is_active": False},
           },
       }

:meth:`pk_found` can be a method returning ``self.goal_active.id`` rather than a hard-coded string,
so it is evaluated lazily after :meth:`setUp` has run. :attr:`request_data` likewise accepts a method
so the request body can reference objects created in :meth:`setUp`.

The ``"updates"`` dictionary declares the assertions the mixin runs after a write operation
completes. Only the fields listed here are checked. Any field omitted is not asserted at all.
Each entry maps a field name to the value that field has in the database after the API call
returns. Nested dicts traverse relations: ``{"role": {"slug": "student"}}`` follows the ``role``
foreign key and asserts its ``slug`` field. For cases where this dict-based approach is
too limited, provide a callable under ``"assertions"`` instead.

Custom Actions and Additional Tests
...................................

For anything beyond standard CRUD web service actions, the ViewSet test class can contain ordinary
``test_*`` methods. Use them for custom ``@action`` endpoints, edge cases, and business rules
expressed over HTTP. Use the helper methods inherited from :class:`ModelViewSetTestMixin` to manage
authentication:

.. code-block:: python

   class LearningGoal_ViewSet_Tests(ModelViewSetTestMixin, LearningGoal_Test_Mixin, TestCase):
       ...
       def test_enroll_no_passphrase(self):
           """
           Self-enrollment without a passphrase returns 200 and creates a role assignment.
           """
           self.login(username="student", password="password")
           ...

       def test_enroll_unauthenticated(self):
           """
           Unauthenticated enrollment is rejected.
           """
           self.logout()

           response = self.client.put(self.url_enroll)
           self.assertIn(response.status_code, [401, 403])

Inside your test methods you can use the following helpers:

- ``self.login(username, password)`` to authenticate as a specific existing user
- ``self.create_user_and_login(perm_strings)`` to create a temporary user
- :meth:`self.logout()` to return to the unauthenticated state

Register in :file:`__init__.py`
...............................

Register the module in :file:`tests/__init__.py` so Django's test runner discovers it.
Otherwise the tests won't run when ``manage.py test`` is executed.

.. code-block:: python

   from .learning_goal import *

Checklist Before Moving On
..........................

Before committing the new feature, verify that:

1. The test file is placed under ``tests/``, named after the model file.
2. :file:`tests/__init__.py` imports the module so the test runner discovers it.
3. The test mixin calls :meth:`super().setUp()` and :func:`reset_current_user`.
4. The test mixin class contains no ``test_*`` methods.
5. ``<Model>_Model_Tests`` covers :meth:`clean` validation and all domain methods.
6. ``<Model>_ViewSet_Tests`` inherits :class:`ModelViewSetTestMixin`, the test mixin and then :class:`TestCase`.
7. All required class attributes for :class:`ModelViewSetTestMixin` are declared.
8. The :attr:`operations` dict contains only the overrides that differ from the defaults.
9. :meth:`get_create_request_data` is defined when create is supported.
10. Likewise, :meth:`get_update_request_data` is defined when update is supported.
11. Custom ``@action`` endpoints have at least one manual test method each.

.. seealso::

   Django testing documentation:
   https://docs.djangoproject.com/en/stable/topics/testing/

   Django REST Framework testing guide:
   https://www.django-rest-framework.org/api-guide/testing/


-----------------------------
Adding New Websocket Channels
-----------------------------

.. important::

   This tutorial is still in flux. It will be updated as we figure the details
   with regard to the OpenBook architecture out.

   As it stands now, we will likely integrate `chanx <https://chanx.readthedocs.io/>`_
   to simplify all this and add automated AsyncAPI generation and schema validation
   similar to how we do in the REST API. See
   `issue 69 <https://github.com/openbook-education/openbook/issues/69>`_
   on GitHub.

.. TODO: Migrate to chnx to reduce effort and get automatic AsyncAPI documentation and
.. server-side message validation. → Also add client-side stub generation from AsyncAPI.

WebSocket channels add a bidirectional, long-lived connection between browser and server.
Unlike regular HTTP requests, the server can push updates at any time after the connection
is accepted. This pattern is useful for live progress updates, collaborative editing signals,
notifications, or any UI state that should change without polling. In Django projects, this
is commonly implemented with Django Channels. Channels extends the ASGI stack and introduces
consumers, channel layers, and routing for WebSocket endpoints. The tutorial below describes
the recommended implementation flow for OpenBook, independent of the final concrete app integration.

Understand the Building Blocks
..............................

Before implementing a new channel, align on the responsibilities of each component.
:class:`AsyncJsonWebsocketConsumer` (or :class:`AsyncWebsocketConsumer`) handles one
WebSocket connection. Routing maps URL paths to consumer classes. The channel layer handles
fan-out and cross-process message delivery using named groups. The browser client subscribes
to a URL and reacts to JSON messages.

Compared to REST endpoints, there is no request/response lifecycle per update. Instead, a
connection is established once, then messages flow both ways until the socket closes.
Authentication and authorization still apply, but they are checked at connect-time and,
for sensitive operations, again per message.

Define the Event Contract First
...............................

Start by designing the message schema before writing code. A stable message contract keeps
backend consumers and Svelte clients aligned.

Use JSON envelopes with explicit type names and a small shared metadata shape.
For example:

.. code-block:: json

   {
      "type": "learning_goal.updated",
      "version": 1,
      "payload": {
         "id": "8b7f2a2b-8b7f-4bce-a620-1f1c8666f522",
         "name": "Understand mixins",
         "is_active": true
      }
   }

Keep event names domain-specific (for example ``learning_goal.updated``) and introduce a
``version`` field from day one. This avoids breaking clients when payloads evolve.

.. note::

   For now, simply document the contract via examples (like the one above) in the source
   code. Use docstrings or comments to collect the samples. Later we will define a process
   to properly document the event contracts in the manual.

Add Backend Routing and a Consumer
..................................

Create a dedicated module for WebSocket consumers in the owning app, for example
:file:`src/openbook/learning_progress/consumers/learning_goal.py`. Then create a routing
module that maps URL paths to these consumers. A minimal example looks like this:

.. code-block:: python

   import json

   from channels.generic.websocket import AsyncJsonWebsocketConsumer


   class LearningGoalConsumer(AsyncJsonWebsocketConsumer):
      """Websocket handler for real-time monitoring of learning goals."""

      async def connect(self):
         """Accept a new client connection and join it to the group."""
         self.course_id = self.scope["url_route"]["kwargs"]["course_id"]
         self.group_name = f"course_{self.course_id}_learning_goals"

         await self.channel_layer.group_add(self.group_name, self.channel_name)
         await self.accept()

      async def disconnect(self, close_code):
         """Remove this client from the group when it disconnects."""
         await self.channel_layer.group_discard(self.group_name, self.channel_name)

      async def receive_json(self, content, **kwargs):
         """Handle incoming messages from this connected client."""
         # Keep incoming handling strict and explicit.
         if content.get("type") == "ping":
            await self.send_json({"type": "pong", "version": 1, "payload": {}})

      async def learning_goal_updated(self, event):
         """Forward a learning_goal_updated group message to this client's connection."""
         await self.send_json(event["message"])

.. note::

   Each client connection receives its own consumer instance. In development, all
   instances run in a single process. In production with multiple worker processes,
   connections may be distributed across different processes, each with its own instances.
   The channel layer (via ``CHANNEL_LAYERS`` in settings, typically Redis) coordinates
   group messaging across all processes and instances. This is why ``group_add()`` and
   ``group_send()`` work reliably for broadcasting: the channel layer ensures that messages
   sent to a group reach all subscribed clients, regardless of which process handles their
   connection.

Matching routing example:

.. code-block:: python

   from django.urls import re_path

   from .consumers.learning_goal import LearningGoalConsumer


   websocket_urlpatterns = [
      re_path(
         r"^ws/learning-progress/courses/(?P<course_id>[0-9a-f-]+)/goals/$",
         LearningGoalConsumer.as_asgi(),
      ),
   ]

At project level, include app-specific patterns in the ASGI WebSocket router so Django Channels
can dispatch incoming connections to the correct consumer.

Group Communication Between Clients
...................................

In the consumer code above, we used two important operations: ``group_add()`` and ``group_discard()``.
These are the foundation for broadcasting messages to multiple clients at once.

**What are groups?** --- A group is a named channel that multiple consumers can subscribe to.
When a message is sent to a group, all subscribed consumers receive it. Groups exist within
the channel layer (your Redis instance or in-memory broker) and allow communication across
different ASGI worker processes. Without groups, you can only send messages directly to one
consumer's channel; with groups, you broadcast to many.

.. note::

   Use groups when you need to broadcast the same event to multiple connected clients simultaneously.
   For example, when a learning goal is updated, all clients viewing that course should receive the
   notification. However, if you only need to exchange data between one client and the server
   (e.g., file uploads, form submissions, or personalized progress updates), groups are unnecessary.
   In those cases, simply send messages directly to the client via :meth:`send_json` without involving
   the channel layer. Groups would only add latency and complexity that serve no purpose for simple
   one-to-one communication.

**Joining and leaving groups** --- In the consumer's :meth:`connect` method, we add the current
connection to a group:

.. code-block:: python

   await self.channel_layer.group_add(self.group_name, self.channel_name)

The first argument is the group name (a string like ``"course_123_learning_goals"``), and the
second is the channel name of *this specific connection* (provided by Django Channels). When
the client disconnects, we remove them:

.. code-block:: python

   await self.channel_layer.group_discard(self.group_name, self.channel_name)

**Sending to groups** --- Outside the consumer (for example in a view or signal handler), send
a message to all members of a group using :meth:`group_send`. The message is a dictionary with
at minimum a ``type`` key:

.. code-block:: python

   await channel_layer.group_send(
       "course_123_learning_goals",
       {
           "type": "goal_updated",        # Maps to learning_goal_updated() method
           "goal_id": "abc123",           # Additional data for the handler
           "name": "New Goal Name",
       }
   )

**Type-to-method mapping** --- The ``type`` field in the message dictionary is special. Django
Channels converts dots to underscores and calls the matching consumer method. So a message with
``"type": "goal_updated"`` invokes the :meth:`goal_updated` method. A message with ``"type": "learning.goal.updated"``
invokes :meth:`learning_goal_updated`. This allows one consumer to handle multiple message
types by defining multiple handler methods.

**Complete example with multiple message types** --- Here is an extended consumer that handles
two different event types:

.. code-block:: python

   import json
   from channels.generic.websocket import AsyncJsonWebsocketConsumer


   class LearningGoalConsumer(AsyncJsonWebsocketConsumer):
       """Websocket handler for real-time monitoring of learning goals."""

       async def connect(self):
           """Accept a new client connection and join it to the group."""
           self.course_id = self.scope["url_route"]["kwargs"]["course_id"]
           self.group_name = f"course_{self.course_id}_learning_goals"

           await self.channel_layer.group_add(self.group_name, self.channel_name)
           await self.accept()

       async def disconnect(self, close_code):
           """Remove this client from the group when it disconnects."""
           await self.channel_layer.group_discard(self.group_name, self.channel_name)

       async def receive_json(self, content, **kwargs):
           """Handle incoming messages from this connected client."""
           if content.get("type") == "ping":
               await self.send_json({
                   "type": "pong",
                   "version": 1,
                   "payload": {}
               })

       async def goal_created(self, event):
           """Handle goal_created messages from the group."""
           await self.send_json({
               "type": "learning_goal.created",
               "version": 1,
               "payload": event["payload"],
           })

       async def goal_updated(self, event):
           """Handle goal_updated messages from the group."""
           await self.send_json({
               "type": "learning_goal.updated",
               "version": 1,
               "payload": event["payload"],
           })

And from a view or signal handler, publish to the group:

.. code-block:: python

   from asgiref.sync import async_to_sync
   from channels.layers import get_channel_layer


   def create_learning_goal(request):
       # Create the goal in the database...
       goal = LearningGoal.objects.create(name="New Goal")

       # Notify all clients in the group
       channel_layer = get_channel_layer()
       async_to_sync(channel_layer.group_send)(
           f"course_{goal.course_id}_learning_goals",
           {
               "type": "goal_created",
               "payload": {
                   "id": str(goal.id),
                   "name": goal.name,
               },
           }
       )

       return JsonResponse({"status": "created"})

Each connected client in the group receives the message, and their consumer's :meth:`goal_created`
method is invoked, which then sends the formatted message to that client's WebSocket connection.

**Key points** --- Groups bridge synchronous and asynchronous code through the channel layer.
When you call :meth:`group_send` from a synchronous view, the channel layer queues the message
and delivers it asynchronously to all group members. Each member's consumer instance receives
the message independently, ensuring that broadcasting works correctly even with multiple
worker processes. The type-to-method mapping keeps message handling organized and extensible
as you add new event types over time.

Publish Events From Domain Logic
................................

Publishing should happen where state changes are authoritative, usually in service methods,
signals, or custom action handlers. The publisher sends a typed message to the group; the
consumer then forwards it to connected clients.

Example publisher call:

.. code-block:: python

   from asgiref.sync import async_to_sync


   async_to_sync(channel_layer.group_send)(
      f"course_{course_id}_learning_goals", {
         "type": "learning_goal_updated",
         "message": {
            "type": "learning_goal.updated",
            "version": 1,
            "payload": {
               "id": str(goal.id),
               "name": goal.name,
               "is_active": goal.is_active,
            },
         },
      },
   )

The ``type`` passed to :meth:`group_send` maps to a consumer method name where dots are
translated to underscores. For that reason, ``learning_goal_updated`` is handled by
:meth:`learning_goal_updated` in the consumer.

Consume Events in Svelte 5
..........................

In Svelte, create one small client module that owns connection setup, reconnect behavior,
and event dispatching to stores or callbacks. Keep this logic centralized to avoid duplicate
socket handling in multiple components.

Start with a socket module that handles connection, disconnection, and error recovery:

.. code-block:: javascript

   // src/lib/learningGoalsSocket.js
   /**
    * WebSocket connection manager for learning goals real-time updates.
    * Handles connection lifecycle, reconnection logic, and message validation.
    */

   import { writable } from "svelte/store";

   let socket = null;
   let reconnectAttempts = 0;
   const MAX_RECONNECT_ATTEMPTS = 5;
   const RECONNECT_DELAY = 2000;

   /** Reactive store indicating whether the WebSocket is currently connected. */
   export const isConnected = writable(false);

   /** Reactive store holding the last connection error message, or null if none. */
   export const connectionError = writable(null);

   /**
    * Constructs the WebSocket URL for the given course ID.
    * Uses secure (wss) or insecure (ws) protocol based on the current page protocol.
    * @param {string} courseId - The course identifier.
    * @returns {string} The WebSocket URL.
    */
   function buildSocketUrl(courseId) {
      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      return `${protocol}://${window.location.host}/ws/learning-progress/courses/${courseId}/goals/`;
   }

   /**
    * Validates and processes an incoming WebSocket message.
    * Messages must have a type and version field; others are logged as warnings.
    * @param {Object} message - The parsed JSON message from the server.
    * @param {string} message.type - The event type (e.g., "learning_goal.updated").
    * @param {number} message.version - The message contract version.
    * @param {Function} onEvent - Callback to dispatch valid messages.
    */
   function handleMessage(message, onEvent) {
      // Validate message shape before processing
      if (!message.type || !message.version) {
         console.warn("Invalid message format:", message);
         return;
      }

      // Dispatch to handler or application logic
      onEvent(message);
   }

   /**
    * Attempts to reconnect to the WebSocket after a delay.
    * Gives up after MAX_RECONNECT_ATTEMPTS and sets an error message.
    * @param {string} courseId - The course identifier.
    * @param {Function} onEvent - The event handler callback.
    */
   function attemptReconnect(courseId, onEvent) {
      if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
         connectionError.set("Failed to reconnect after multiple attempts");
         return;
      }

      reconnectAttempts += 1;
      setTimeout(() => {
         connect(courseId, onEvent);
      }, RECONNECT_DELAY);
   }

   /**
    * Establishes a WebSocket connection to the learning goals channel for the given course.
    * Sets up event listeners for open, message, error, and close events.
    * @param {string} courseId - The course identifier.
    * @param {Function} onEvent - Callback invoked with each valid incoming message.
    */
   export function connect(courseId, onEvent) {
      const url = buildSocketUrl(courseId);

      socket = new WebSocket(url);

      socket.addEventListener("open", () => {
         isConnected.set(true);
         connectionError.set(null);
         reconnectAttempts = 0;
      });

      socket.addEventListener("message", (event) => {
         try {
            const message = JSON.parse(event.data);
            handleMessage(message, onEvent);
         } catch (error) {
            console.error("Failed to parse WebSocket message:", error);
         }
      });

      socket.addEventListener("error", (error) => {
         console.error("WebSocket error:", error);
         connectionError.set("Connection error");
      });

      socket.addEventListener("close", () => {
         isConnected.set(false);
         attemptReconnect(courseId, onEvent);
      });
   }

   /**
    * Closes the WebSocket connection and resets the internal state.
    * Updates isConnected store to false.
    */
   export function disconnect() {
      if (socket) {
         socket.close();
         socket = null;
      }
      isConnected.set(false);
   }

   /**
    * Sends a message to the server via the WebSocket.
    * Does nothing if the socket is not connected; logs a warning.
    * @param {Object} message - The message object to send (will be JSON-stringified).
    * @param {string} message.type - The event type (e.g., "ping").
    * @param {number} message.version - The message contract version.
    */
   export function sendMessage(message) {
      if (socket && socket.readyState === WebSocket.OPEN) {
         socket.send(JSON.stringify(message));
      } else {
         console.warn("Socket not connected, message not sent:", message);
      }
   }

Now create a store for managing learning goals:

.. code-block:: javascript

   // src/lib/learningGoalsStore.js
   /**
    * Svelte store for managing the list of learning goals.
    * Provides reactive operations: add, update, delete, and set goals.
    */

   import { writable } from "svelte/store";

   /**
    * Creates a custom Svelte store for learning goals.
    * @returns {Object} Store with subscribe, addGoal, updateGoal, deleteGoal, and setGoals methods.
    */
   function createLearningGoalsStore() {
      const { subscribe, set, update } = writable([]);

      return {
         subscribe,

         /**
          * Adds a new goal to the list.
          * @param {Object} goal - The goal object to add.
          */
         addGoal: (goal) => update((goals) => [...goals, goal]),

         /**
          * Updates an existing goal by ID with new property values.
          * @param {string} goalId - The goal's unique identifier.
          * @param {Object} updates - Partial object with properties to merge.
          */
         updateGoal: (goalId, updates) => update((goals) =>
            goals.map((g) => (g.id === goalId ? { ...g, ...updates } : g))
         ),

         /**
          * Removes a goal from the list by ID.
          * @param {string} goalId - The goal's unique identifier.
          */
         deleteGoal: (goalId) => update((goals) =>
            goals.filter((g) => g.id !== goalId)
         ),

         /**
          * Replaces the entire goals list with a new array.
          * @param {Array} goals - The new goals array.
          */
         setGoals: (goals) => set(goals),
      };
   }

   /** Exported store instance for use in components. */
   export const learningGoals = createLearningGoalsStore();

Finally, use the socket and store together in a component:

.. code-block:: html

   <!-- src/frontend/app/src/components/pages/learning-goals/LearningGoalsPage.svelte -->

   <script>
      import { onMount, onDestroy } from "svelte";
      import { learningGoals } from "../../stores/learningGoalsStore.js";
      import { connect, disconnect, isConnected, connectionError, sendMessage } from "../../sockets/learningGoalsSocket.js";

      /** @type {string | number} */
      export let courseId;

      /**
       * Handles incoming WebSocket messages and updates the store accordingly.
       * Dispatches messages by type: created, updated, or deleted events.
       * Unknown message types are logged as warnings.
       * @param {Object} message - The incoming WebSocket message.
       * @param {string} message.type - The event type (e.g., "learning_goal.created").
       * @param {Object} message.payload - The event payload containing goal data.
       */
      function handleSocketEvent(message) {
         switch (message.type) {
            case "learning_goal.created":
               learningGoals.addGoal(message.payload);
               break;

            case "learning_goal.updated":
               learningGoals.updateGoal(message.payload.id, message.payload);
               break;

            case "learning_goal.deleted":
               learningGoals.deleteGoal(message.payload.id);
               break;

            default:
               console.warn("Unknown message type:", message.type);
         }
      }

      /**
       * Lifecycle hook: runs when the component mounts.
       * Fetches initial goals from the REST API and establishes the WebSocket connection.
       */
      onMount(async () => {
         // Fetch initial goals from REST API
         const response = await fetch(`/api/learning_progress/learning_goals/?course=${courseId}`);
         const data = await response.json();
         learningGoals.setGoals(data.results);

         // Connect WebSocket for real-time updates
         connect(courseId, handleSocketEvent);
      });

      /**
       * Lifecycle hook: runs when the component is destroyed.
       * Closes the WebSocket connection to release resources.
       */
      onDestroy(() => {
         disconnect();
      });

      /**
       * Sends a ping message to the server to test the connection.
       * Useful for debugging or keeping the connection alive.
       */
      function sendPing() {
         sendMessage({ type: "ping", version: 1, payload: {} });
      }
   </script>

   <div class="goals-container">
      <h2>Learning Goals</h2>

      {#if $connectionError}
         <div class="error">
            WebSocket connection failed: {$connectionError}
         </div>
      {/if}

      <div class="status">
         Status: {$isConnected ? "Connected" : "Disconnected"}
         <button on:click={sendPing} disabled={!$isConnected}>
            Test Connection
         </button>
      </div>

      <ul class="goals-list">
         {#each $learningGoals as goal (goal.id)}
            <li class="goal-item" class:inactive={!goal.is_active}>
               <strong>{goal.name}</strong>
               <p>{goal.description}</p>
               <span class="level">{goal.level}</span>
            </li>
         {/each}
      </ul>
   </div>

   <style>
      .goals-container {
         padding: 1rem;
      }

      .error {
         background: #fee;
         border: 1px solid #f44;
         padding: 0.5rem;
         border-radius: 4px;
         color: #c00;
         margin-bottom: 1rem;
      }

      .status {
         margin-bottom: 1rem;
         padding: 0.5rem;
         background: #eee;
         border-radius: 4px;
      }

      .goals-list {
         list-style: none;
         padding: 0;
      }

      .goal-item {
         padding: 1rem;
         margin-bottom: 0.5rem;
         border: 1px solid #ddd;
         border-radius: 4px;
         background: white;
      }

      .goal-item.inactive {
         opacity: 0.6;
      }

      .level {
         display: inline-block;
         background: #0066cc;
         color: white;
         padding: 0.25rem 0.5rem;
         border-radius: 3px;
         font-size: 0.85rem;
         margin-top: 0.5rem;
      }
   </style>

This end-to-end example shows:

1. **Socket module** with reconnection logic, error handling, and message validation
2. **Store** for reactive state management of goals
3. **Component** that initializes the connection, handles incoming events, and renders the UI
4. **Error handling** throughout: invalid message formats, connection failures, and recovery

The WebSocket events update the Svelte store reactively, which automatically updates the UI
whenever a goal is created, updated, or deleted by any client in the group.

.. important::

   Validate access on connect before joining any group. Do not trust ``course_id`` from the URL
   without permission checks against the authenticated user. Also validate incoming message
   types and payload shape before processing to avoid unsafe side effects. In the socket module
   above, we validate ``message.type`` and ``message.version`` before dispatching; in the
   component, the switch statement safely ignores unknown message types.

Checklist Before Moving On
..........................

Before opening a pull request, verify that:

1. The event schema is documented and versioned.
2. URL routing and consumer registration are wired in the ASGI application.
3. The consumer joins and leaves groups correctly in :meth:`connect` and :meth:`disconnect`.
4. Publish points are close to authoritative state changes.
5. Sensitive channels perform explicit permission checks.
6. The Svelte client handles reconnects and unknown message types gracefully.
7. Manual testing covers connect, receive, push update, and disconnect paths.

.. seealso::

   Django Channels documentation:
   https://channels.readthedocs.io/en/stable/

   ASGI specification:
   https://asgi.readthedocs.io/en/latest/

   Svelte documentation:
   https://svelte.dev/docs


---------------------------
Adding New Background Tasks
---------------------------

.. important::

   This tutorial is still in flux. It will be updated as we refine the details
   around the final OpenBook architecture. See
   `issue 70 <https://github.com/openbook-education/openbook/issues/70>`_
   on GitHub.

.. TODO: Add end-to-end example that also shows how to monitor task progress in the UI.

Background tasks move slow, expensive, or failure-prone work out of the HTTP request/response
path. Instead of blocking a user request while a long operation runs, the server enqueues a task,
returns quickly, and processes the work asynchronously in a worker process. In Django projects,
this is typically implemented with a task queue such as Celery. The patterns below describe a
recommended implementation flow for OpenBook. Because this area is still evolving, consider the
guidance here a stable starting point, not yet a final project-wide contract.

Understand the Building Blocks
..............................

Before implementing anything, align on four terms:

.. rst-class:: spaced-list

- **Task** --- A Python function that can run outside the request lifecycle, often retried on
  transient errors.

- **Broker** --- The queue transport (for example Redis or RabbitMQ) that receives enqueued tasks
  from Django and delivers them to workers.

- **Worker** --- A background process that consumes queued tasks and executes task functions.

- **Result backend** --- Optional persistence for task state and results so clients can query
  ``PENDING``, ``STARTED``, ``SUCCESS``, or ``FAILURE``.

Compared to synchronous view logic, task execution has different guarantees. A task may run later,
be retried, run more than once, or fail after partial progress. For that reason, task code should
be idempotent where possible and explicit about retry behavior.

Decide Whether Work Belongs in a Task
.....................................

Use a background task when at least one of the following applies:

1. The operation is slow enough to hurt API response time.
2. The operation depends on external services that may be temporarily unavailable.
3. The operation can be retried safely without user interaction.
4. The operation is triggered by an event and does not need an immediate response body.

Examples of good candidates include exporting a large dataset, synchronizing with an external
service, sending bulk notifications, or generating a report after a long-running import.
Keep operations synchronous when the result is immediately required to render the next UI state,
or when consistency rules demand one atomic database transaction across all steps.

Define the Task Contract First
..............................

Before writing the task function, define a small contract for input, output, and state reporting.
This keeps API endpoints, workers, and frontend polling/websocket handlers aligned.

At minimum, decide:

1. Which identifier(s) the task receives (for example one model UUID).
2. Which states are visible to clients (for example ``queued``, ``running``, ``done``, ``failed``).
3. Which progress payload is exposed (for example percentage and current step label).
4. Which errors are retried versus surfaced as terminal failures.

Prefer passing primitive identifiers into the task instead of full serialized objects. The task can
then load fresh database state at execution time and avoid stale payload assumptions.

.. note::

   Document the contract as docstrings in the code.

Implement the Task Function
...........................

Place task functions in a dedicated module inside the owning app, for example
:file:`src/openbook/learning_progress/tasks/goal_sync.py`. Keep each task focused on one workflow,
and keep reusable domain logic in ordinary service functions that can be tested independently of
Celery.

Minimal task example:

.. code-block:: python

   from celery import shared_task


   @shared_task(
       bind=True,
       autoretry_for=(ConnectionError, TimeoutError),
       retry_backoff=True,
       retry_jitter=True,
       max_retries=5,
   )
   def sync_learning_goal(self, goal_id):
      """Synchronize one learning goal with an external system in the background.

      Contract:
         Input:
            - ``goal_id`` (str): UUID of the learning goal.

         Progress states reported via ``update_state``:
            - ``PROGRESS`` with ``{"step": "loading", "percent": 10}``
            - ``PROGRESS`` with ``{"step": "synchronizing", "percent": 70}``
            - ``PROGRESS`` with ``{"step": "finalizing", "percent": 95}``

         Terminal outcomes:
            - ``SUCCESS`` returns a dict with ``goal_id``, ``status``, and
              ``external_reference``.
            - transient ``ConnectionError`` and ``TimeoutError`` are retried
              automatically (up to ``max_retries=5``).
      """
      self.update_state(
         state="PROGRESS",
         meta={"step": "loading", "percent": 10},
      )

      # Load model state lazily from the database.
      goal = LearningGoal.objects.get(pk=goal_id)

      self.update_state(
         state="PROGRESS",
         meta={"step": "synchronizing", "percent": 70},
      )

      result = synchronize_goal_with_external_system(goal)

      self.update_state(
         state="PROGRESS",
         meta={"step": "finalizing", "percent": 95},
      )

      return {
         "goal_id": str(goal.id),
         "status": "done",
         "external_reference": result.reference,
      }

The :func:`shared_task` decorator makes the function discoverable by workers.
``bind=True`` gives access to the task instance as ``self``, which is required for
:meth:`update_state` and retry control.

.. important::

   Keep task functions idempotent whenever possible. If a task retries or is delivered twice,
   running it again should not corrupt data or duplicate side effects.

Trigger Tasks From REST API Actions
...................................

A common pattern is to enqueue the task in a custom :class:`ViewSet`` action and return a tracking payload
immediately. This keeps request latency low while still giving the client enough data to monitor
progress.

Example custom action:

.. code-block:: python

   from drf_spectacular.utils      import extend_schema
   from rest_framework.decorators  import action
   from rest_framework.response    import Response


   class LearningGoalViewSet(ModelViewSetMixin, ModelViewSet):
      """REST endpoints for creating, reading, and synchronizing learning goals."""
      # Existing configuration ...

      @extend_schema(summary="Start Learning Goal Synchronization")
      @action(detail=True, methods=["post"], url_path="sync")
      def sync(self, request, pk=None):
         """Enqueue synchronization and return the HTTP task contract.

         Contract:
            - Returns ``202 Accepted`` when the task is queued.
            - Response payload includes:
              ``task_id`` (str), ``state`` ("queued"), and ``goal_id`` (str).
            - Clients use ``task_id`` to poll or subscribe for progress updates.
         """
         goal = self.get_object()
         async_result = sync_learning_goal.delay(str(goal.id))

         return Response(
            {
               "task_id": async_result.id,
               "state": "queued",
               "goal_id": str(goal.id),
            },
            status=202,
         )

Returning HTTP 202 indicates that the request was accepted for asynchronous processing and has not
completed yet. Include at least ``task_id`` and a stable object reference so the frontend can bind
UI state to the right task.

Expose Task Status to Clients
.............................

Clients need one read endpoint for task status. A minimal shape can include state, progress, and
error information. Keep the response contract stable and explicit.

Example status payload:

.. code-block:: json

   {
      "task_id": "77a8c1c7-faf8-454f-bab6-bf7f6c95c2f8",
      "state": "PROGRESS",
      "progress": {
         "step": "synchronizing",
         "percent": 70
      },
      "result": null,
      "error": null
   }

When the task succeeds, ``result`` contains the returned payload. On terminal failure, keep
``state`` and ``error`` explicit so the frontend can show actionable feedback.

Push Progress Updates to the UI
...............................

Polling works as a baseline, but WebSocket push gives better responsiveness for long-running jobs.
The event flow is similar to the WebSocket tutorial above:

1. Task execution updates state (for example via :meth:`update_state`).
2. A publisher emits typed progress events to a channel layer group.
3. The WebSocket consumer forwards events to connected clients.
4. Svelte components update local stores based on event ``type`` and ``task_id``.

Use a typed envelope and version field from day one:

.. code-block:: json

   {
      "type": "task.progress.updated",
      "version": 1,
      "payload": {
         "task_id": "77a8c1c7-faf8-454f-bab6-bf7f6c95c2f8",
         "state": "PROGRESS",
         "percent": 70,
         "step": "synchronizing"
      }
   }

Keep WebSocket subscriptions scoped. Clients should only receive events for tasks they are
authorized to observe.

Handle Reliability and Operations
.................................

Background processing is an operational concern, not only an implementation detail. Define explicit
settings for retries, time limits, and visibility into failures.

At minimum, configure and document:

1. Retry policy per task type.
2. Hard and soft execution time limits.
3. Dead-letter or failure handling strategy.
4. Worker concurrency and queue routing.
5. Metrics and logs for task success rate and latency.

During development, inspect worker logs and task state transitions for every new task before
opening a pull request.

Checklist Before Moving On
..........................

Before opening a pull request, verify that:

1. The task contract (input, output, state) is documented.
2. The task function is idempotent or has explicit duplicate protection.
3. Retry rules cover transient failures only.
4. A REST endpoint starts the task and returns HTTP 202 with ``task_id``.
5. A status endpoint exposes stable state, progress, and error fields.
6. UI updates work via polling or WebSocket events.
7. Permission checks prevent cross-user visibility of task progress.
8. Failure paths are tested and visible in logs.

.. seealso::

   Celery documentation:
   https://docs.celeryq.dev/en/stable/

   Django REST Framework actions:
   https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing

   Django Channels documentation:
   https://channels.readthedocs.io/en/stable/
