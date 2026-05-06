=============
# How To Guides
=============

This page collects various tutorials for often-needed development activities. The tutorials
build upon each other, as usually for each new feature all the below documented steps need
to be carried out.

.. contents:: Page Content
   :local:


-----------------
# Creating New Apps
-----------------

- Django Project vs. App (in resemblance to the same section from ``doc/HACKING.md``).
- Creating a new app with ``manage.py``
- OpenBook apps must live inside ``src/openbook``, using short names
- Adding to ``INSTALLED_APPS`` in ``settings.py``
- ``apps.py`` with a custom ``AppConfig`` class
- Typical layout of an OpenBook Django app (read ``src/openbook/content`` as a template)
   - ``routes.py`` instead of URLS
      - no server-side rendering / view templates
      - just models, admin, REST API, fixtures, migrations, unit tests
   - Other typical Django app elements when needed
- Example code for ``apps.py``


-------------------
# Creating New Models
-------------------

.. NOTE: The mixins are central to the OpenBook architecture
.. Readers must absolutely get them right

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
.. Readers must absolutely get them right

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
.. Readers must absolutely get them right

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
.. Readers must get this right, including how to correctly use the mixin (read its source to understand before you document)

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
