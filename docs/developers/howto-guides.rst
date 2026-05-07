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

   The verbose name is used in the admin and in other places in the UI. So it must be
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
   fields, so labels in admin forms and API-driven UIs stay consistent and translatable. Also
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
in the admin and in log output. When ``NameDescriptionMixin`` is included it already supplies a
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
admin, API serializers, and tests can follow the same conventions across apps.

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
the label is translatable. It appears in admin forms, error messages, and API schema
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
the expected meaning or format. The text appears as a hint beneath the widget in admin forms.

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

Before you continue with admin and API integration, verify that:

1. The model is placed in the correct file under ``models/`` (one concept plus companion models).
2. Required core/auth mixins are inherited, with ``UUIDMixin`` first.
3. User-facing labels (``verbose_name`` and choice labels) are wrapped in ``_()``.
4. Field options are intentional, especially ``null`` vs ``blank`` and ``unique`` vs ``db_index``.
5. ``Meta`` includes at least ``verbose_name`` and ``verbose_name_plural``, plus optional ordering/indexes.
6. ``__str__()`` returns a concise, human-readable identifier.
7. The model is imported in ``models/__init__.py``.


--------------------------
Adding Models to the admin
--------------------------

Django admin is the primary tool for administrators and developers to inspect live data, diagnose
problems, and create test content during development before a full UI exists. For this reason,
every model should have an admin integration. The work follows the same file-mirroring pattern
as models and viewsets: one source file per domain concept in the ``admin/`` directory, wired
together through ``__init__.py``.

Create the Admin File
.....................

To integrate a model into the Django admin create a new file in the ``admin/`` directory with
the same name as its source file in the ``model/`` directory. Within the new file define a
class that inherits from ``CustomModeladmin``, imported from ``openbook.admin``. This base class
combines three things, which is why, unlike in traditional Django projects, you never touch
Django's built-in ``Modeladmin`` class directly:

1. Django Unfold for the styled admin UI, and
2. DjangoQL for advanced search expressions in the change list,
3. Django Import/Export for CSV, YAML, and XLSX data exchange.

A minimal admin class needs only the ``model``, ``list_display``, ``ordering``, and
``search_fields`` properties to link it to the model class and name the fields used
in the overview list.  Again, using learning goals as an example, the file would be
named ``admin/learning_goal.py`` (like the model file) and have the following conent:

.. code-block:: python

   from openbook.admin         import CustomModeladmin
   from ..models.learning_goal import LearningGoal


   class LearningGoaladmin(CustomModeladmin):
       """admin view for learning goals."""
       model         = LearningGoal
       list_display  = ["name", "course", "level", "is_active"]
       ordering      = ["course", "name"]
       search_fields = ["name", "course__name"]

This is already functional: the change list shows the configured columns, results are sortable
and searchable, and the default form --- not declared in the class --- renders all editable fields.
Isn't Django great? 🙂

Register in ``__init__.py``
...........................

Once the class exists, register it in ``admin/__init__.py``:

.. code-block:: python

   from openbook.admin import admin_site
   from .learning_goal import LearningGoaladmin
   from ..             import models

   admin_site.register(models.LearningGoal, LearningGoaladmin)

The order of ``register()`` calls determines the order in which models appear in the admin
sidebar. So, register models in a logical order that makes sense to administrators.

Configuring the Change List
...........................

The following admin class attributes control the change list behaviour. Look at other admin
classes nearby to see how they are typically used and play aroudn with their values to achieve
best results.

.. important::

   We treat the admin as a first-class citizen, as if it was the primary user interface for
   all users. Because, for administrators it really *is* the primary user interface to
   work with the models.

**Visible columns** --- ``list_display`` sets which fields appear as columns. Keep it focused:
show the fields needed to identify and distinguish records at a glance.

**Clickable links** --- ``list_display_links`` specifies which columns act as links to the
edit page. Without it, only the first column is a link by default. To simplify navigation a
little, try to make all fields clickable.

**Related field prefetching** --- ``list_select_related`` names the Foreign Key fields
that Django should join in the same query as the list, avoiding one extra query per row.
This usually enhances the performance considerably.

**Default sort** --- ``ordering`` sets the default sort order for the change list. Mirror the
``ordering`` declared in the model's ``Meta`` class to keep behaviour consistent.

**Full-text search** --- ``search_fields`` drives the DjangoQL search bar. Use double
underscore notation to traverse relations: ``"course__name"`` searches the related course's
name.

**Filter sidebar** --- ``list_filter`` populates the right-hand filter panel. Use plain field
names for simple boolean or choice fields, and ``(field, RelatedOnlyFieldListFilter)`` tuples
for Foreign Key fields where you want to restrict the list to values that are actually in use.

**Read-only fields** --- ``readonly_fields`` marks fields that should be visible in the edit
form but cannot be changed by the admin user. Always include the audit trail field names here
so they are visible but protected from accidental edits.

Audit Trail Integration
.......................

When a model uses ``CreatedModifiedByMixin``, import the four helper constants from
``openbook.auth.admin.mixins.audit`` and spread them into the relevant admin class attributes:

.. code-block:: python

   from openbook.auth.admin.mixins.audit import created_modified_by_fields
   from openbook.auth.admin.mixins.audit import created_modified_by_fieldset
   from openbook.auth.admin.mixins.audit import created_modified_by_filter
   from openbook.auth.admin.mixins.audit import created_modified_by_related


   class LearningGoaladmin(CustomModeladmin):
       """admin view for learning goals."""
       model               = LearningGoal
       resource_classes    = [LearningGoalResource]
       list_display        = ["name", "course", "level", "is_active", *created_modified_by_fields]
       list_select_related = [*created_modified_by_related]
       list_filter         = ["level", "is_active", *created_modified_by_filter]
       readonly_fields     = [*created_modified_by_fields]
       ordering            = ["course", "name"]
       search_fields       = ["name", "course__name"]

The four constants expand as follows:

**Column names** --- ``created_modified_by_fields`` is a list of four field names:
``created_by``, ``created_at``, ``modified_by``, and ``modified_at``. Spread it into
``list_display`` to show audit columns in the change list, and into ``readonly_fields`` to
prevent manual edits.

**Prefetch hints** --- ``created_modified_by_related`` lists the two Foreign Key names for the
user relations. Spread it into ``list_select_related`` to avoid N+1 queries when the list renders.

**Filter sidebar** --- ``created_modified_by_filter`` is a list of filter entries (plain
strings and ``(field, FilterClass)`` tuples). Spread it into ``list_filter``.

**Fieldset** --- ``created_modified_by_fieldset`` is a ready-made fieldset tuple rendered as
a tab. Always append it as the last entry in ``fieldsets``.

Organising the Edit Form with Fieldsets
.......................................

By default Django admin renders all editable fields in a single unstyled block. Fieldsets
group fields into named sections and can optionally render as Django Unfold tabs, making
longer forms easier to navigate. To this end, define ``fieldsets`` for the edit/change view
and optionally -- when different -- ``add_fieldsets`` for the create view.

.. caution::

   When both ``fieldsets`` and ``add_fieldsets`` are present, the two must not be identical.
   The latter must omit auto-populated fields such as the audit trail, because those fields
   do not exist yet on first save and their presence causes a crash.

.. code-block:: python

   class LearningGoaladmin(CustomModeladmin):
       """admin view for learning goals."""
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

**Audit fieldset** --- Always end ``fieldsets`` with ``created_modified_by_fieldset`` when the
model uses ``CreatedModifiedByMixin``. Never include it in ``add_fieldsets``.

Inline Views
............

Related objects such as translation companion models can be embedded directly in the parent
model's change page using inline classes. This is more ergonomic than requiring administrators
to navigate to a separate list to manage translations. To do so, define a ``TabularInline``
(or ``StackedInline`` for more complex layouts) in the same admin file and reference it in the
parent admin class via ``inlines``:

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


   class LearningGoaladmin(CustomModeladmin):
       """admin view for learning goals."""
       # ...
       inlines = [_LearningGoalTextInline]

Our conventions are:

**No empty placeholder** --- Always set ``extra = 0`` to suppress the empty placeholder rows
that Django renders by default.

**Link to full admin page** -- If the inlined model has a proper admin page, set
``show_change_link = True`` so that administrators can open the inline record on its own page
for more detailed work.

**Render as tabs** --- Consider, setting ``tab = True`` to render the inline as a separate Django
Unfold tab, keeping the main form uncluttered.

**Prefix private classes** --- Prefix inline class names with an underscore to signal that they are
private implementation details of the file.

Import/Export Support
.....................

In OpenBook every admin class should support file-based data import/export so that administrators
can export data for review, import test data, or migrate entries between environments. This requires
are resource class that must be derived from ``ImportExportModelResource`` (in ``openbook.admin``)
and declare the field list in its inner ``Meta`` class. Wire it into the admin class via the
``resource_classes`` property like so:

.. code-block:: python

   from openbook.admin         import CustomModeladmin
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


   class LearningGoaladmin(CustomModeladmin):
       """admin view for learning goals."""
       model            = LearningGoal
       resource_classes = [LearningGoalResource]   # Resource class above
       list_display     = ["name", "course", "level", "is_active"]
       ordering         = ["course", "name"]
       search_fields    = ["name", "course__name"]

.. note::

   Mind the square brackets around the ressource class.

Always include ``"id"`` and ``"delete"`` as the first two fields. The ``delete`` column is a
convention from ``ImportExportModelResource`` that lets users mark rows for deletion (provided
thw file rows contain valid ids) by setting the value in the file to ``true``.

For foreign keys, boolean fields, or many-to-many fields that
cannot be represented as plain text, add a ``Field()`` declaration with an appropriate widget
class. The advanced patterns subsection covers this for scope-related fields.

.. seealso::

   Advanced Import/Export patterns:
   https://django-import-export.readthedocs.io/en/latest/advanced_usage.html

Advanced: Scope-specific Patterns
..................................

Models that use ``ScopeMixin`` (i.e. belong to a permission scope) or ``ScopedRolesMixin``
(i.e. define a permission scope) require additional mixins for the form and resource classes.
All of these live in ``openbook.auth.admin.mixins.scope``.

**Scope-member models** --- When a model references a scope via ``ScopeMixin``, inherit the
resource class from ``ScopeResourceMixin`` instead of ``ImportExportModelResource``. This
mixin handles import and export of the scope reference, resolving scope objects by slug during
import. For the form, inherit from ``ScopeFormMixin`` to replace the raw UUID widget with a
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


   class EnrollmentMethodadmin(CustomModeladmin):
       form             = EnrollmentMethodForm
       resource_classes = [EnrollmentMethodResource]
       # ...

**Scope-owner models** --- When a model defines a permission scope via ``ScopedRolesMixin``,
inherit the resource class from ``ScopedRolesResourceMixin`` to handle export of the owner and
public permissions fields. For the form, inherit from ``ScopedRolesFormMixin`` to restrict
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


   class Courseadmin(CustomModeladmin):
       form             = CourseForm
       resource_classes = [CourseResource]
       # ...

.. important::

   Note that ``ScopedRolesResourceMixin`` must come before ``ImportExportModelResource`` in the
   inheritance chain so that its field declarations take precedence.

**Scope-role fields** --- Models that combine a scope reference with a role field additionally
need ``ScopeRoleFieldFormMixin`` on the form class to restrict the role choices to roles
defined within the selected scope. The corresponding inline class should inherit
``ScopeRoleFieldInlineMixin`` to apply the same restriction inside inline forms.

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

When both ``ScopeFormMixin`` and ``ScopeRoleFieldFormMixin`` are needed, merge their ``Media``
declarations explicitly as shown above. The same form class is then wired into the admin class
via the ``form`` attribute.

The module also exports the helper constants ``scope_type_filter`` and
``permissions_fieldset``, which can be spread into ``list_filter`` and ``fieldsets``
respectively, in the same way as the audit trail helpers.

.. code-block:: python

   from openbook.auth.admin.mixins.scope import permissions_fieldset
   from openbook.auth.admin.mixins.scope import scope_type_filter


   class Courseadmin(CustomModeladmin):
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
2. The admin class inherits from ``CustomModeladmin``.
3. A resource class is defined and listed in ``resource_classes``.
4. Audit trail constants are used when ``CreatedModifiedByMixin`` is in the model's MRO.
5. ``readonly_fields`` includes the audit trail field names.
6. Both ``fieldsets`` and ``add_fieldsets`` are defined, and ``add_fieldsets`` omits the audit fieldset.
7. Companion models (e.g. translations) are covered by an inline class.
8. The admin class is registered in ``admin/__init__.py`` in the correct position.

.. seealso::

   Django admin reference:
   https://docs.djangoproject.com/en/stable/ref/contrib/admin/

   Modeladmin list display options:
   https://docs.djangoproject.com/en/stable/ref/contrib/admin/#modeladmin-options

   Django admin actions:
   https://docs.djangoproject.com/en/stable/ref/contrib/admin/actions/

   Django Import/Export documentation:
   https://django-import-export.readthedocs.io/en/latest/


-------------------------------
Exposing Models in the REST API
-------------------------------

Building on the previous tutorials, this section explains how to expose a model through the REST API so
that the frontend SPA and external clients can consume it. Every model needs three things: a **viewset**
that handles HTTP requests, a **serializer** that translates between Python objects and JSON, and a
**filter class** that enables clients to query the list endpoint. All three live in a single file inside
``viewsets/``, mirroring the structure of ``models/`` and ``admin/``.

Create the ViewSet
..................

Create one file per domain concept inside ``viewsets/``, named after the corresponding model file.
Continuing the learning progress example, the file would be ``viewsets/learning_goal.py``.
Every viewset inherits ``ModelViewSetMixin`` first, followed by DRF's ``ModelViewSet``. The order
matters: ``ModelViewSetMixin`` must precede ``ModelViewSet`` so that its ``create()`` override takes
effect. The mixin fills and validates the model instance before saving, which allows Django's
object-level permission checks to run during creation --- when no database record exists yet.

A minimal viewset looks like this:

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
       serializer_class = LearningGoalSerializer   # defined below
       filterset_class  = LearningGoalFilter        # defined below
       ordering         = ["course", "name"]
       search_fields    = ["name", "description", "course__name"]

The two class decorators serve specific purposes. ``@extend_schema(extensions=...)`` registers the
viewset under a named group in the OpenAPI schema, which the API browser uses to organise endpoints by
application area. ``@with_flex_fields_parameters()`` adds the ``_fields``, ``_omit``, and ``_expand``
query parameter descriptions to the schema so clients know how to request only the fields they need.

For models whose list and detail endpoints should be publicly readable without authentication, add
``AllowAnonymousListRetrieveViewSetMixin`` before ``ModelViewSetMixin`` in the inheritance chain:

.. code-block:: python

   from openbook.drf.viewsets import AllowAnonymousListRetrieveViewSetMixin

   class LearningGoalViewSet(AllowAnonymousListRetrieveViewSetMixin, ModelViewSetMixin, ModelViewSet):
       ...

This mixin returns ``AllowAny`` permissions for the ``list`` and ``retrieve`` actions while delegating
all other permission checks to the viewset's default permission classes.

Register API Routes
...................

Unlike
``models/`` and ``admin/``, there is no ``__init__.py`` import step. Instead, import the viewset
directly in ``routes.py`` and register it with the DRF router there:

.. code-block:: python

   from .viewsets.learning_goal import LearningGoalViewSet


   def register_api_routes(router, prefix):
       router.register(f"{prefix}/learning_goals", LearningGoalViewSet, basename="learning_goal")

The ``basename`` argument is used by DRF to generate the URL names for reverse lookups, such as
``learning_goal-list`` and ``learning_goal-detail``. Use the model name in ``snake_case`` as the
convention throughout OpenBook.

Creat the Serializer
....................

Every serializer extends ``FlexFieldsModelSerializer`` from ``openbook.drf.flex_serializers``. This
class wraps ``rest_flex_fields2`` and adds two important behaviours: it calls ``model.full_clean()``
during validation so that all Django field validators, ``clean()`` overrides, and uniqueness constraints
are enforced on every API write; and it caches the validated model instance so that ``ModelViewSetMixin``
can run permission checks before calling ``save()``.

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

A few conventions apply to every serializer. Always start the field list with ``"id"`` and end with the
audit trail fields so the JSON output is predictable and consistent across all endpoints. Mark ``"id"``,
``"created_at"``, and ``"modified_at"`` as read-only at minimum, since these are populated automatically
by the database or by ``CreatedModifiedByMixin``.

The ``expandable_fields`` dictionary maps field names to serializer class paths. By default, foreign keys
are returned as UUIDs; the client opts in to receiving a full nested object by appending
``?_expand=course`` to the request. For many-to-many relations, use the tuple form with
``{"many": True}`` as the second element:

.. code-block:: python

   expandable_fields = {
       "permissions": ("openbook.auth.viewsets.permission.PermissionSerializer", {"many": True}),
   }

For foreign keys that should be represented as human-readable strings rather than UUIDs, define a custom
serializer field. The auth app ships several ready-made fields for common cases: ``UserField`` (returns
the username), ``RoleField`` (returns the role slug), and ``ScopeTypeField`` (returns the
fully-qualified model string such as ``"openbook_content.course"``). These fields replace the default
``PrimaryKeyRelatedField`` and handle both input and output.

For scope-owner models that implement ``ScopedRolesMixin``, inherit ``ScopedRolesSerializerMixin``
before ``FlexFieldsModelSerializer``. This mixin injects the ``owner``, ``public_permissions``,
``role_assignments``, ``enrollment_methods``, and ``access_requests`` fields along with their
expandable variants. Spread its ``Meta`` field lists to avoid duplication:

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

Creat the Filter Class
......................

Every viewset needs a filter class so clients can search and narrow the list endpoint with query
parameters. The filter class inherits one or more mixin classes followed by ``FilterSet`` as the very
last base class. This order is a hard requirement: ``FilterSet`` must appear last so that the mixin
``Meta`` classes are resolved correctly before ``FilterSet`` processes them.

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

The ``fields`` dictionary maps field names to tuples of supported lookup expressions. Use
``("exact",)`` for equality checks and ``("exact", "lte", "gte")`` for date or numeric fields that
benefit from range queries.

The auth app provides filter mixins to cover the cross-cutting concerns. Add only those that match the
model's mixin inheritance.

**Audit trail filters** --- ``CreatedModifiedByFilterMixin`` adds ``created_by`` and ``modified_by``
character filters resolved by username, plus date-range lookups for ``created_at`` and ``modified_at``.
Use it for any model that includes ``CreatedModifiedByMixin``.

**Scope-member filters** --- ``ScopeFilterMixin`` adds ``scope_type`` and ``scope_uuid`` filters for
models that implement ``ScopeMixin``. The ``scope_type`` parameter accepts either a numeric content-type
primary key or a fully-qualified model string such as ``"openbook_content.course"``.

**Scope-owner filters** --- ``ScopedRolesFilterMixin`` adds an ``owner`` filter resolved by username.
Use it for models that implement ``ScopedRolesMixin``.

**Permission filters** --- ``PermissionsFilterMixin`` and ``PermissionFilterMixin`` filter by Django
permission strings in the form ``"app_label.codename"``. The former targets M2M permission relations;
the latter targets a single FK permission field.

When a field cannot be mapped to a standard lookup expression, define a custom filter method. Pass it
as the ``method`` argument on the filter declaration and implement the method on the class:

.. code-block:: python

   from django_filters.filters import CharFilter


   class EnrollmentMethodFilter(ScopeFilterMixin, CreatedModifiedByFilterMixin, FilterSet):
       role = CharFilter(method="role_filter")

       class Meta:
           model  = EnrollmentMethod
           fields = {
               **ScopeFilterMixin.Meta.fields,
               "role":      (),
               "name":      ("exact",),
               "is_active": ("exact",),
               **CreatedModifiedByFilterMixin.Meta.fields,
           }

       def role_filter(self, queryset, name, value):
           return queryset.filter(role__slug=value)

The method receives the queryset and the filter value and returns a filtered queryset. Use this pattern
for any filter that must traverse a relation or apply logic that standard lookups cannot express.

Advanced: OpenAPI Extensions and Custom Actions
...............................................

Most viewsets need nothing beyond what the preceding tutorials cover. The patterns below apply when
default behaviour is not sufficient.

**Overriding operation details** --- ``@extend_schema`` can also be applied to individual action
methods to set the ``operation_id``, a human-readable ``summary``, a typed ``request`` body, and the
expected ``responses``. Use ``inline_serializer`` for simple one-off request payloads that do not
warrant a dedicated serializer class:

.. code-block:: python

   from drf_spectacular.utils      import extend_schema
   from drf_spectacular.utils      import inline_serializer
   from rest_framework.serializers import CharField


   @extend_schema(
       operation_id = "learning_progress_learning_goal_submit",
       summary      = "Submit Learning Goal",
       request      = inline_serializer(
           name   = "SubmitGoalRequestSerializer",
           fields = {"evidence": CharField(required=False)},
       ),
       responses = LearningGoalSerializer,
   )
   @action(detail=True, methods=["put"], url_path="submit")
   def submit(self, request, pk=None):
       ...

**Custom actions** --- Use ``@action`` from ``rest_framework.decorators`` to add endpoints beyond the
standard CRUD set. The ``detail`` flag controls whether the action operates on a single object
(``True``, appended to the object's URL) or on the collection (``False``, appended to the list URL).
The ``url_path`` value becomes the URL segment, and ``permission_classes`` overrides the viewset's
default permissions for that action only:

.. code-block:: python

   from rest_framework.decorators  import action
   from rest_framework.permissions import AllowAny
   from rest_framework.response    import Response


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

Always annotate custom actions with ``@extend_schema`` so the generated API documentation includes the
correct request and response shapes.

**Scope-specific patterns** --- Models using ``ScopedRolesMixin`` or ``ScopeMixin`` need additional
wiring in both the serializer and the filter class, as shown in the examples throughout this section.
For complete reference implementations, read ``src/openbook/content/viewsets/course.py``
(scope-owner pattern) and ``src/openbook/auth/viewsets/enrollment_method.py`` (scope-member pattern)
side by side.

.. seealso::

   Django REST Framework ViewSet reference:
   https://www.django-rest-framework.org/api-guide/viewsets/

   DRF Flex Fields documentation:
   https://rsinger86.github.io/drf-flex-fields/

   DRF Spectacular documentation:
   https://drf-spectacular.readthedocs.io/en/latest/

   Django Filters documentation:
   https://django-filter.readthedocs.io/en/stable/

Checklist Before Moving On
..........................

Before continuing to fixtures and tests, verify that:

1. The viewset file is in ``viewsets/``, named after the model file.
2. The viewset inherits ``ModelViewSetMixin`` before ``ModelViewSet``.
3. The ``@extend_schema(extensions=...)`` and ``@with_flex_fields_parameters()`` decorators are present.
4. All required attributes are set: ``queryset``, ``serializer_class``, ``filterset_class``,
   ``search_fields``.
5. The serializer extends ``FlexFieldsModelSerializer`` with ``"id"`` and audit fields in
   ``read_only_fields``.
6. ``expandable_fields`` is declared for all FK and M2M relations.
7. The filter class has ``FilterSet`` last in its MRO and includes all applicable filter mixins.
8. The viewset is registered in ``routes.py`` (not ``__init__.py``).

-----------------
Creating Fixtures
-----------------

Fixtures provide a reproducible baseline of data for local development and first-time deployments.
Use YAML fixtures to keep the data readable, reviewable, and easy to maintain in version control.

.. rst-class:: spaced-list

1. Create and prepare the data first in Django admin or the application UI until it reflects the state you
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
