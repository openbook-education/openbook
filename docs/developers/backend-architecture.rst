====================
Backend Architecture
====================

This page collects defining aspects of the OpenBook backend architecture. The intention is to help
developers understand the most important technology and implementation choices.

.. contents:: Page Content
   :local:


------------------
Technology Choices
------------------

The OpenBook Server is built with the following technology:

.. list-table::
   :width: 100%
   :widths: 1 2

   * - **Python**
     - Programming language
   * - **Poetry**
     - Package manager
   * - **Django Web Framework**
     - Core server framework
   * - **Django Allauth**
     - Authentication, user management, single sign-on
   * - **Django REST Framework**
     - REST API for the frontend and external clients
   * - **Django Channels**
     - WebSocket support
   * - **Celery**
     - Background tasks

The idea is to keep the technical requirements lean to enable easy deployment in custom environments.
Therefore, the choice of Django might be considered "conservative", but in fact it contains all
needed functionality, like HTTP request routing, server-side templates, and database access, in a
single, stable, and well-maintained dependency.


--------------------------
Architectural Cornerstones
--------------------------

REST API and Single Page App
............................

.. graphviz::
  :align: center
  :caption: Class relationships for the REST API

  digraph rest_api_layers {
    graph [bgcolor=transparent, rankdir=TB, nodesep=0.35, ranksep=0.6];
    node [shape=box, style="rounded,filled", fontname="Sans", fontsize=11, width=2.8, height=0.7, fixedsize=true];

    model      [label=<<B>Model</B><BR/>Stores domain data<BR/>and core rules>, fillcolor="#e3f2fd", color="#1e88e5"];
    serializer [label=<<B>Serializer</B><BR/>Validates payloads<BR/>and shapes JSON>, fillcolor="#fff3e0", color="#fb8c00"];
    filterset  [label=<<B>FilterSet</B><BR/>Defines query params<BR/>and queryset filters>, fillcolor="#e8f5e9", color="#43a047"];
    viewset    [label=<<B>ViewSet</B><BR/>Exposes list/detail actions<BR/>and binds the other classes>, fillcolor="#fce4ec", color="#d81b60"];

    model -> serializer   [color="#1e88e5"];
    model -> filterset    [color="#1e88e5"];
    model -> viewset      [color="#1e88e5"];
    serializer -> viewset [color="#fb8c00"];
    filterset -> viewset  [color="#43a047"];
  }

Django applications traditionally use server-side rendering for the UI. This is because, when
Django was invented, web applications in general used server-side rendering to dynamically
create HTML. JavaScript was only used for visual effects and small UX enhancements. Nowadays,
web apps often consist of a single page app running completely in-browser and a server backend
providing data persistency and domain logic. OpenBook falls into this category, too. Because it
allows us to provide a much more dynamic and interactive UI and the REST API feeding the UI can
also be consumed by other clients or even 3rd-party systems.

Understanding RESTful principles is easy. Writing a good REST API isn't. OpenBook uses Django
REST Framework and a few related libraries to provide a flexible and modern REST API that not
only serves data over HTTP. In particular:

**Flexible response structure** --- Simpler REST APIs use fixed request and response structures,
meaning that the full resource data is always exchanged between client and server. But:

- What if the client only needs a small subset of fields from a much larger resource?
- What if the client just wants to update a single field or two?
- What if the resource has a deep structure with relations to other resources?
- What if the client needs to query (also known as search or filter) the list of resources?

Clearly, one size doesn't fit all. For this reason, OpenBook allows the clients to narrow down
which fields to read or write and to decide which relations to expand and which relations to
reduce to a single foreign key ID. This is made possible through the :mod:`drf-flex-fields2`
library (our own maintained fork of the great :mod:`drf-flex-fields` by Robert Singer).
Additionally, Django Filters is included to allow clients not only to list resources but also to
filter the result
list with queries.

For each model, the following three classes must be written, to pull this off:

.. list-table::
   :header-rows: 1
   :width: 100%

   * - Class
     - Responsibility
   * - ViewSet
     - Definition and handling of RESTful HTTP endpoints
   * - FilterSet
     - Definition of query parameters and filtering the result list
   * - Serializer
     - JSON (de)serialization, flexible response shaping

**OpenAPI Schema** --- For a long time, REST web services were missing a universally accepted
machine-readable description like WSDL in the SOAP world. In recent times, OpenAPI --- formerly
known as Swagger --- has filled this gap. This allows us to generate type-safe client stubs,
validate requests and responses, and much more. Unlike in other projects, in OpenBook the OpenAPI
schema is generated from the Python source, which means it will always be up to date.

**User documentation** --- Another advantage of OpenAPI is that browsable API documentation
can be generated from it. To this end, OpenBook integrates ReDoc to provide human-readable
API documentation.

Enhanced Django Admin
.....................

.. graphviz::
  :align: center
  :caption: Class relationships for Admin integration

  digraph admin_layers {
    graph [bgcolor=transparent, rankdir=TB, nodesep=0.35, ranksep=0.6];
    node [shape=box, style="rounded,filled", fontname="Sans", fontsize=11, width=2.8, height=0.7, fixedsize=true];

    model    [label=<<B>Model</B><BR/>Persistent domain object>, fillcolor="#e3f2fd", color="#1e88e5"];
    resource [label=<<B>Resource</B><BR/>Maps rows for import<BR/>and export files>, fillcolor="#fff3e0", color="#fb8c00"];
    admin    [label=<<B>Admin</B><BR/>Defines list/change views,<BR/>inlines, tabs, and actions>, fillcolor="#e8f5e9", color="#43a047"];

    model -> admin    [color="#1e88e5"];
    model -> resource [color="#1e88e5"];
    resource -> admin [color="#fb8c00"];
  }

The Admin is a very useful and rather unique feature to Django. With just a few lines of code
any model can be integrated, supporting all CRUD (Create, Read, Update, Delete) operations.
In OpenBook the Django Admin is used for developers and administrators to customize the system,
inspect live data and create mock data even before the corresponding part in the frontend app
has been built. For this reason, even though the primary end users (lecturers and students)
never use the Admin, it is treated as a first-class citizen, providing an optimized user interface
for each model. In particular:

- Django Unfold is integrated to provide a modern user experience throughout.
- Related models are grouped in sub-categories below each technical app.
- Inline models and tab pages are used extensively to optimize data maintenance.
- DjangoQL is integrated to provide additional search capabilities beyond traditional filters.
- Django Import/Export is integrated to allow importing and exporting models from/to files.

Therefore, for each model, at least the following classes must be written:

.. list-table::
   :header-rows: 1
   :width: 100%

   * - Class
     - Responsibility
   * - Admin
     - Definition of the change and list views
   * - Resource
     - File-based import and export of model data

Role-Based Permissions
......................

Another difference to regular Django apps lies in the permission handling. By default, Django uses coarse
permissions that define what a user can do with a given type of data (model), e.g. "can view textbooks".
While perfectly sensible for applications like news pages or blog engines, this falls short in educational
contexts. Because in education it is not enough to say, that "teachers can edit course contents" or that
"teachers can assess tests". One must also say *which courses* they can edit or *which tests* for *which students*
they may assess.

Django provides object-level permission hooks for this, but ships no concrete implementation. Similar to most
Learning Management Systems, OpenBook implements a role-based permission system, where users have different roles
in different contexts. The prime example is being a teacher/lecturer on one course but only a student in another.

.. seealso::

   See the next section for a deep-dive on how the permission system is implemented.

Database Models
...............

.. graphviz::
   :align: center
   :caption: Mixin inheritance for models

   digraph model_mixins {
      graph [bgcolor=transparent, rankdir=TB, nodesep=0.35, ranksep=0.6];
      node [shape=box, style="rounded,filled", fontname="Sans", fontsize=11, width=2.8, height=0.7, fixedsize=true];
      edge [arrowsize=1.1, arrowtail=empty, arrowhead=none];

      uuid1   [label=<<B>UUIDMixin</B><BR/>UUID primary key>, fillcolor="#e3f2fd", color="#1e88e5"];
      audit1  [label=<<B>CreatedModifiedByMixin</B><BR/>Creation and change audit trail>, fillcolor="#e3f2fd", color="#1e88e5"];
      others1 [label=<<B>...Mixin</B><BR/>Additional mixins>, fillcolor="#e3f2fd", color="#1e88e5"];
      model   [label=<<B>Concrete Model</B><BR/>Business fields and relations>, fillcolor="#f5f5f5", color="#616161"];

      uuid2   [label=<<B>UUIDMixin</B><BR/>UUID primary key>, fillcolor="#e3f2fd", color="#1e88e5"];
      i18n2   [label=<<B>TranslatableMixin</B><BR/>Language-specific text handling>, fillcolor="#e3f2fd", color="#1e88e5"];
      text    [label=<<B>Text Model</B><BR/>Translated labels, titles,<BR/>and descriptions>, fillcolor="#f5f5f5", color="#616161"];

      { rank=same; uuid1; audit1; others1; }
      { rank=same; uuid2; i18n2; }

      uuid1 -> model   [dir=back];
      audit1 -> model  [dir=back];
      others1 -> model [dir=back];

      model -> uuid2   [style=invis, weight=10];
      model -> i18n2   [style=invis, weight=10];

      uuid2 -> text    [dir=back];
      i18n2 -> text    [dir=back];

      model -> text    [label="parent / translations", arrowhead=normal];
   }

Most business models inherit a small set of abstract mixins instead of redefining technical
fields in each app. :class:`UUIDMixin` replaces numeric IDs with UUIDs, :class:`CreatedModifiedByMixin`
adds an audit trail, and further mixins such as :class:`ActiveInactiveMixin` or the scope-related
mixins add recurring behavior only where needed.

Translatable content is modeled separately. A main model keeps the stable business identity and
relations, while a companion ``*Text`` model in the same file inherits :class:`TranslatableMixin` and
stores the language-specific labels, titles, and descriptions for that parent object.

.. hint::

   In OpenBook all self-defined models use :class:`UUIDMixin` to replace the sequential ID
   key field with stable UUIDs. This helps to avoid number clashes in migrations.

Source Code Structure
.....................

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

Typically, Django Apps define all models in a single source file called :file:`models.py`, the
Admin views in a file called :file:`admin.py`, the REST endpoints in a file called :file:`viewsets.py`
and so on. In OpenBook these are directories with one source file per domain concept, e.g:

.. code-block:: text

   src/openbook/learning_progress/
   ├── __init__.py
   ├── models/
   │   ├── __init__.py
   │   └── badge.py
   │   └── learning_goal.py
   ├── admin/
   │   ├── __init__.py
   │   ├── badge.py
   │   └── learning_goal.py
   └── viewsets/
       ├── __init__.py
       ├── badge.py
       └── learning_goal.py

To make these directories behave like single source files, they contain a :file:`__init__.py` file,
that re-exports all public contents of the other files. Additionally, as can be seen, each directory
contains the same set of files. This is because each model must be integrated with the Django Admin
as well as be exposed through the REST API.

To simplify these tasks a little and enforce uniform behavior, the OpenBook core and auth apps
contain several mixins for recurring concepts. These serve as conceptual building blocks throughout
the system that reduce variation and help developers understand new features by analogy with
existing ones.


-----------------------------
Permission Handling in Detail
-----------------------------

This section describes permission handling in Django and how it is used in the application. It
explains the implementation strategy to make regular model-based permissions (for example,
"Can create textbook") coexist with object-level permissions (for example,
"Can change THIS textbook").

Default Permissions for Each Model
..................................

When the app :mod:`django.contrib.auth` is installed, Django automatically creates four permission objects
in the database for each model:

.. list-table::
   :header-rows: 1
   :width: 100%
   :widths: 1 2

   * - Permission
     - Meaning
   * - ``{app_label}.add_{model}``
     - Add new objects
   * - ``{app_label}.view_{model}``
     - Search and display objects
   * - ``{app_label}.change_{model}``
     - Modify existing objects
   * - ``{app_label}.delete_{model}``
     - Delete existing objects

``{app_label}`` is the owning app's label (as defined in the ``App`` class), and ``{model}`` is the name
of the model in lowercase (no other transformation done).

How Permissions Are Checked on Model Level
..........................................

**Django Admin** -- By default, model permissions are checked in the Django Admin (in the
:class:`ModelAdmin` class, methods :meth:`has_..._permission(self, request)`) to check whether a user is allowed
to perform the corresponding action.

**Own Code** -- No permissions check is done when directly accessing the database with the Django ORM.
Permission checks must be performed in the higher levels (views), of which the Django Admin happens
to be one. The easiest way to check a permission is to call :meth:`has_perm()` on the user object, for
example :meth:`user.has_perm("myapp.view_model")`. This, in turn, iterates over the installed
authentication backends and calls :meth:`has_perm(user_obj, perm)` until one backend grants the
permission.

**Django REST Framework** -- Django REST Framework does not do permission checks unless specifically
asked in the :class:`ViewSet`. Permission checks are encapsulated in :attr:`permission_classes` that may
implement arbitrary logic. These classes inherit from a :class:`BasePermission` that defines the method
:meth:`has_permission(self, request, view)`. Most implementations do not use the :mod:`django.contrib.auth`
permissions but rather implement simpler checks like :class:`IsAuthenticated` or :class:`AllowAny`.
:class:`DjangoModelPermissions` applies permission checks similar to Django Admin's :class:`ModelAdmin`, though
they do not share any code.

When a :class:`ViewSet` contains multiple permission classes as a list, permission is only granted if all
of them return ``True``:

.. code-block:: python

   class MyModelViewSet(ModelViewSet):
      queryset = MyModel.objects.all()
      serializer_class = MyModelSerializer
      permission_classes = [IsAuthenticated, IsStaff, IsOwner]

However, permissions can also be combined using logic operators, for example:

.. code-block:: python

   class MyModelViewSet(ModelViewSet):
      # ...
      permission_classes = IsAuthenticated & (IsStaff | IsOwner)

How Object-Level Permissions Are Checked
........................................

Object-level permissions always require a custom authentication backend, as Django only includes the
API. The API is a compatible extension to the regular API:

.. list-table::
   :header-rows: 1
   :width: 100%

   * - Extension Point
     - API
   * - Django User
     - :meth:`User.has_perm(self, perm, obj=None)`
   * - Authentication Backend
     - :meth:`has_perm(user_obj, perm, obj=None)`
   * - Django Admin
     - :meth:`ModelAdmin.has_..._permission(self, request, obj=None)`
   * - Django REST Framework
     - :meth:`BasePermission.has_object_permission(self, request, view, obj)`

There are still framework-level limitations to keep in mind.

**Queryset Visibility** --- Neither Django, Django Admin, nor Django REST Framework apply object
permissions to querysets. This means users can always query objects and read all data even when
they lack "view" permissions.

**Default ModelBackend Behavior** --- Django's default :class:`ModelBackend` always returns ``False`` when
object-level permissions are checked, even when the user has the global permission.

**ModelAdmin Object Parameter** --- :class:`ModelAdmin` ignores the ``obj`` parameter and always checks
model permissions.

**Create Permission Gap in DRF** --- Django REST Framework checks object-level permissions only in
class :class:`DjangoObjectPermissions`, but despite the documentation, it seems the add permission is not
checked (because the new object does not yet exist).

**Limitations Around get_object()** --- Django REST Framework checks object permissions in the
:meth:`get_object()` method. It may be necessary to manually call the inherited method when it is
replaced with a custom implementation or when the generic REST views are not used. Limitations of
object permissions in Django REST Framework
(`Source <https://www.django-rest-framework.org/api-guide/permissions/>`_):

.. rst-class:: spaced-list

* For performance reasons, the generic views will not automatically apply object-level permissions
  to each instance in a queryset when returning a list of objects.

* Often, when using object-level permissions, you will also want to filter the queryset
  appropriately to ensure that users only have visibility onto instances that they are permitted to
  view.

* Because the :meth:`get_object()` method is not called, object-level permissions from the
  :meth:`has_object_permission()` method are not applied when creating objects. In order to restrict
  object creation, you need to implement the permission check either in the :class:`Serializer` class or
  override ``perform_create()`` in the ``ViewSet`` class.

How Our Custom Authentication Backend Is Implemented
....................................................

**Adding Roles to Models** -- Our permission system is built around the premise that some models
support object permissions and others do not. Models supporting object permissions implement the
``ScopedRolesMixin`` to become a scope for user roles and related objects:

.. list-table::
   :header-rows: 1
   :width: 100%

   * - Concept
     - Meaning
   * - Roles
     - Exist within the scope and collect Django ``Permission`` entries.
   * - Allowed Permissions
     - Define which permissions can be added to the roles of a scope.
   * - Role Assignments
     - Assign roles to users within the scope.
   * - Access Requests
     - Can be created by users to request a role within a scope.
   * - Enrollment Methods
     - Allow users to self-enroll to get a role within a scope.
   * - Public Permissions
     - Are permissions for non-enrolled and anonymous users within a scope.

Typical scopes are courses and textbooks. They often contain related objects (for example, course
materials or textbook pages) that also support object permissions but share the scope of their parent
object. This allows permissions like "In this course (scope object), teachers (role) can create
materials (related object)" to be expressed. For this, the related objects must inherit
:class:`RoleBasedObjectPermissionsMixin` and override the :meth:`get_scope()` method. In both cases (scope
objects and related objects), the method :meth:`has_obj_perm()` can be overridden to implement additional
custom checks.

**Authentication Backend** -- We provide a custom authentication backend in class
:class:`openbook.auth.backends.RoleBasedObjectPermissionsBackend` that extends the stock Django
:class:`ModelBackend`. This is simpler than reusing third-party libraries like Django Guardian,
which requires explicitly persisting and keeping in sync who can do what for every single object.

:class:`RoleBasedObjectPermissionsBackend` changes permission resolution as follows:

1. The user is a superuser.
2. A matching global entry exists in :class:`AnonymousPermission`.
3. The user and the object are the same.
4. The user is the object's ``owner`` (optional).
5. The object's :meth:`has_obj_perm()` method (via mixins, optional).

   1. Public permissions of the scope.
   2. Roles assigned to the user.

6. Regular non-object permissions from user and group assignments.
7. If ``view`` fails, retry as ``change`` (including object-aware checks).

This keeps object-level behavior consistent while preserving Django's model-level permission model.
Because this backend inherits from :class:`ModelBackend`, the default backend does not need to be added
separately in settings.

Unlike Django's :class:`ModelBackend`, the Django Admin first checks "view" then "change" permissions when
an object should be displayed. This logic is mirrored in our :class:`RoleBasedObjectPermissionsBackend` to
unify the behavior in all parts of the application.

How We Iron Out the Inconsistencies
...................................

**Querying and Filtering** -- For REST APIs, querysets are filtered with
:class:`openbook.drf.filters.DjangoObjectPermissionsFilter`. This filter evaluates
:meth:`request.user.has_perm("{app_label}.view_{model}", obj)` for each object and returns only visible
records. This closes DRF's default queryset visibility gap for list endpoints.

**Django Admin** -- The active admin base class is :class:`openbook.admin.CustomModelAdmin`. Admin model
classes inherit from this shared base, while permission decisions still flow through

**Django Admin** -- The code contains :class:`openbook.core.admin.utils.model.ModelAdmin` as a replacement
for the stock :class:`ModelAdmin` to make sure that object-level permissions are checked. But we currently
do not use it. If we want to use it in the future, the inheritance chain of
:class:`openbook.admin.CustomModelAdmin` must be adapted.

**Django REST Framework** -- In :file:`settings.py`, the default permissions are
:class:`IsAuthenticated` and :class:`DjangoObjectPermissionsOnly`. In practice, this means all endpoints are
protected by default unless a view explicitly overrides :attr:`permission_classes` (for example with
:class:`AllowAny`).

The module :mod:`openbook.drf` adds focused building blocks around DRF:

.. rst-class:: spaced-list

* :class:`openbook.drf.permissions.DjangoObjectPermissionsOnly` customizes DRF object-permission behavior,
  includes ``view`` in the permission map, and keeps model checks compatible with the backend logic.

* :class:`openbook.drf.flex_serializers.FlexFieldsModelSerializer` calls :meth:`full_clean()` before saving to
  reuse model-level validation.

* :class:`openbook.drf.viewsets.ModelViewSetMixin` performs object permission checks during ``POST`` by
  constructing a pre-filled instance before :meth:`perform_create()`.

:class:`DjangoObjectPermissionsOnly` is a specialized version of :class:`DjangoObjectPermissions` that includes
``view`` checks and delegates the final model-versus-object fallback behavior to our authentication
backend.
