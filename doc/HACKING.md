Developer Notes for OpenBook
============================

This document serves as a cheat sheet for developers to get started quickly. There are no
fancy things -- if you already know Python, Poetry, Django, NPM, ... But finding the right
information might not be easy when working with so much different technology. This document
tries to summarize the most important things.

1. [Technology Choices](#technology-choices)
1. [Django Project vs. App](#django-project-vs-app)
1. [Permission Handling](#permission-handling)
1. [Creating Fixtures](#creating-fixtures)



Technology Choices
------------------

The OpenBook Server is built with the following technology:

* Python
* Poetry - Package Management
* Django Web Framework - Core Server Framework
* Django REST Framework - API Endpoints for the frontend and external clients
* Django Channels - Websocket Support

The idea is to keep the technical requirements lean to enable easy deployment in custom environments.
Therefore the choice of Django might be considered "conservative", but in fact it contains all the needed
functionality like HTTP request routing, server-side templates, database access, ... in a single, stable
and well maintained dependency.

The frontend is a single page app, composed of a core library and several add-on libraries, that
can also run stand-alone without server backend. In part this is due to the development history
of the project starting as a pure static SPA in 2017. But it has the nice advantage to still allow
static deployments of course materials on any web server or learning management system. Therefore,
for the frontend we use the following additional things:

 * esbuild - Bundler
 * npm - Package manager
 * TypeScript - Type annotations for JavaScript

Django Project vs. App
----------------------

Each Django web application consists of a _Django project_, representing the web application
itself, and usually multiple _Django apps_, representing single functional units. Both are
Python modules with certain required source files. Though the whole source code could easily
live inside the project module, the Django developers recommend splitting the project into
multiple apps to foster separation of concerns and code re-use.

When you have a project like `openbook` the Django Admin command created a top-level
directory of that name, containing a sub-directory of the same name. But to avoid having
three nested directories of the same name, that directory was renamed to `src`, inside
which the `openbook` Django project lives, inside which several apps live. Technically
the apps could also live a siblings to the project, but allows us to use the sibling
directories for other things.


```text
.                                 Root directory with this file
└── src                           Main source directory
    ├── manage.py                 Django CLI
    └── openbook                  Django project
        ├── settings.py           Django configuration
        ├── app_1                 Django Application
        │   └── ...
        ├── app_2                 Django Application
        │   └── ...
        └── ...                   Django Application
```

Permission Handling
-------------------

This section described the permission handling in Django and how it is used in the application.
It explains the implementation strategy to make regular model-based permissions (e.g. "Can create
textbook") co-exist with object-level permissions (e.g. "Can change THIS textbook").

### Default Permissions for Each Model

When the app `django.contrib.auth` is installed, Django automatically creates four permission objects
the database for each model:

 * `{app_label}.add_{model}`: Add new objects
 * `{app_label}.view_{model}`: Search and display objects
 * `{app_label}.change_{model}`: Modify existing objects
 * `{app_label}.delete_{model}`: Delete existing objects

`{app_label}` is the owning app's label (as defined in the `App` class) and `{model}` the name of the
model in lower-case (no other transformation done).

### How Permissions are Checked (on Model Level)

**Django Admin:**
By default the model permissions are checked in the Django Admin (in the `ModelAdmin` class, methods
`has_..._permission(self, request)`) to check, if a user is allowed to perform the corresponding action.

**Own Code:**
No permissions check is done when directly accessing the database with the Django ORM. Permission checks
must be performed in the higher-levels (views) of which the Django Admin happens to be one. The easiest way
to check a permission is to call `has_perm()` on the user object, e.g. `user.has_perm("myapp.view_model").
This in turn iterates over the installed authentication backends and calls `has_perm(user_obj, perm)`
until one backend grants the permission.

**Django REST Framework:**
Django REST Framework doesn't do permission checks, unless specifically asked in the `ViewSet`s. Permission checks
are encapsulated in `permission_classes` that may implement arbitrary logic. These classes inherit from a
`BasePermission` that defines the method `has_permission(self, request, view)`. Most implementations don't
use the `django.contrib.auth` permissions but rather implement simpler checks like `IsAuthenticated` or `AllowAny`.
`DjangoModelPermissions` applies similar permission checks as Django Admin's `ModelAdmin`, though they are
not sharing any code.

When a `ViewSet` contains multiple permission classes as a list, the permission is only granted if all of them
return `True`:

```python
class MyModelViewSet(ModelViewSet):
    queryset           = MyModel.objects.all()
    serializer_class   = MyModelSerializer
    permission_classes = [IsAuthenticated, IsStaff, IsOwner]
```

However, permissions can also be combined using logic operators, e.g.:

```python
class MyModelViewSet(ModelViewSet):
    #...
    permission_classes = IsAuthenticated & (IsStaff | IsOwner)
```

#### How Object-Level Permissions are Checked

Object-level permissions always require a custom authentication backend, as Django only includes the API.
The API is a compatible extension to the regular API:

* `User.has_perm(self, perm, obj=None)` (Django User)
* `has_perm(user_obj, perm, obj=None)` (Authentication Backend)
* `ModelAdmin.has_..._permission(self, request, obj=None)` (Django Admin)
* `BasePermission.has_object_permission(self, request, view, obj)` (Django REST Framework)

However, there are some oddities:

* Neither Django, Django Admin nor Django REST Framework apply object permissions to query sets.
  This means, users can always query objects and read all data even when they lack "view" permissions.

* Django's default `ModelBackend` always returns `False` when object-level permissions are checked,
  even when the user has the permission.

* `ModelAdmin` ignores the `obj` parameter and always checks for model permissions.

* Django REST Framework checks object-level permissions only in class `DjangoObjectPermissions`, but despite
  the documentation it seems the the add permission is not checked (because the new object is not yet existing).

* Django REST Framework checks object permissions on the `get_object()` method. It may be necessary to
  manually call the inherited method, when it is replaced with a custom implementation or the generic
  REST views are not used. Limitations of object permissions in Django REST Framework
  ([Source](https://www.django-rest-framework.org/api-guide/permissions/)):

  * For performance reasons the generic views will not automatically apply object level permissions
    to each instance in a queryset when returning a list of objects.

  * Often when you're using object level permissions you'll also want to filter the queryset appropriately,
    to ensure that users only have visibility onto instances that they are permitted to view.

  * Because the `get_object()` method is not called, object level permissions from the `has_object_permission()`
    method are not applied when creating objects. In order to restrict object creation you need to implement
    the permission check either in your `Serializer` class or override the `perform_create()` method of your
    `ViewSet` class.

#### How our Custom Authentication Backend is Implemented

**Adding Roles to Models:**
Our permission system is built around the premise that some models support object-permissions and
others don't. Models supporting object-permissions implement the `ScopedRolesMixin` to become a
scope for user roles and related objects:

 * Roles: Exist within the scope and collect Django `Permission`s.
 * Allowed Permissions: Define which permissions can be added to the roles of a scope
 * Role Assignments: Assign roles to users within the scope
 * Access Requests: Can be created by users to request a role within a scope
 * Enrollment Methods: Allow users to self-enroll to get a role within a scope
 * Public Permissions: Are permissions for non-enrolled and anonymous users within a scope

Typical scopes are courses and textbooks. They often contain related objects (e.g. course materials
or textbook pages) that also support object-permissions but share the scope of their parent object.
This allows to express permissions like "In this course (scope object) teachers (role) can create
materials (related object)". For this the related objects must inherit `RoleBasedObjectPermissionsMixin`
and override the `get_scope()` method. In both cases (scope objects and related objects) the method
`has_perm()` can be overridden to implement additional custom-checks.

**Authentication Backend:**
We provide a custom authentication backend in class `openbook.core.RoleBasedObjectPermissionsBackend`
as it appears simpler than reusing third-party libraries. Especially libraries like Django Guardian
which requires to explicitly persist and keep in sync who can do what for which single object.

`RoleBasedObjectPermissionsBackend` inherits from the stock `ModelBackend` and changes its behavior
as follows- For normal permission checks without an object it behaves exactly the same. Object permissions
are checked in the following order, stopping at the first match:

1. The user is a superuser
1. The user and the object are the same
1. The user is the object's `owner` (optional).
1. The object's `has_obj_perm()` method (via mixins, optional).
    1. Public permissions of the scope
    1. Roles assigned to the user
1. Regular non-object permissions

Superusers can do anything. Users can change their own data. The owner is always authorized. Otherwise role-based
permissions are checked. If this is not supported by the object or fails, it falls back to regular user permissions.
Thus, the `ModelBackend` doesn't need to be included in the Django settings, as its function is already covered.

The Django Admin first checks "view" than "change" permissions when a single object should be displayed.
This logic has been moved to our `RoleBasedObjectPermissionsBackend` to unify the behavior in all parts
of the application.

#### How we Iron out the Inconsistencies

**Querying and Filtering:**
No deliberate attempt is done on the technical level to restrict query results to objects where the user
has view permissions. Applying several database joins this would in theory be possible, but it seems not
worth the effort or performance loss. Instead, we should be cautious to return as little fields as possible
when models are searched and queried, always assuming that the returned values could be visible to anyone.

**Django Admin:**
Use `openbook.core.admin.utils.model.ModelAdmin` instead of the stock `ModelAdmin` to make sure that
object-level permissions are checked for displaying, changing and deleting single objects. Unlike the
stock class, this version applies a hack to check object-permissions also for new objects ("add").

**Django REST Framework:**
We set our own `AllowNone` default permission in `settings.py` to enforce a deliberate decision for
each view set and prevent unprotected REST endpoints by accident.

The module `openbook.core.drf` contains specialized `ModelSerializer` and `ModelViewSet` classes that
use `DjangoObjectPermissionsOnly` by default, run a `full_clean()` on the object before it is saved
(to run validations implemented in the model layer) and checks object-permissions also when new objects
are created (POST).

These two classes also employ a hack to check object-permissions also for new objects ("add").

`DjangoObjectPermissionsOnly` is a specialized version of the stock `DjangoObjectPermissions` that
respects the logic in our authentication backend (model-permission is not required but overrides
object-permission, view permission is checked, too).

Creating Fixtures
-----------------

Fixtures are a good way to provide initial data for developers and end-users to get started with
the OpenBook server. Here are a few hints on what to consider:

* **Hand-edited YAML Format:** Use `python manage.py dumpdata --format yaml myapp` to create a data
  dump on the console. Copy the relevant parts into a new `fixtures/myapp/xyz.yaml` file. Note that
  the file extension must be exactly `.yaml` for Django to recognize the fixture. Clean up the file,
  bring all entries in logical order, remove unneeded `null` properties and add comments.

* **Natural Keys:** When using the `dumpdata` command make sure to enable natural keys. Thus the
  full command becomes: `python manage.py dumpdata --format yaml --natural-foreign --natural-primary myapp`.
  This avoids a problem with generic relations: Each model with a generic relation must have a foreign
  key on the `ContentType` model that contains a list of all known models. This uses an auto-incremented
  ID that is not stable. Without natural keys the fixtures would contain the raw ID of the content type,
  that would most-likely not reference the model we want during import of the fixture.

* **Load Initial Data:** Once your new fixture is working, consider adding it to the `load_initial_data`
  management command. The source code is in the `openbook/core/management` directory. This allows other
  developers and users to import a complete set of initial data with only one command.

**Natural keys, part II:** Why are we not using natural keys for our models? After writing the lines
above the initial plan was to add natural keys to all own models, so that the fixtures would be free
from UUIDs and generally much easier to read. But the attached trade-offs quickly outgrew the benefit:

* Adding natural keys to each model increases the size considerably: `natural_key()` method, custom
  manager, unique constraint for each model. But that alone would have been okay, as we didn't want
  to introduce a dependency to [Django Natural Keys](https://pypi.org/project/natural-keys/) to keep
  the dependencies minimal.

* Many models have a name, that would be a perfect fit for the natural key. But it might be problematic
  to make them unique.

* Generic relations are still problematic due to the `object_id` property. That was the real killer.
  Why all the effort, if each generic relation still references the UUID of the related object?
  For this to work the UUID of the related object must be enforced during import, neglecting the reason
  to add natural keys in the first place.

  There is a work-around using [custom serializers and deserializers](https://stackoverflow.com/a/70700302).
  But that is quite a lot of code that needs deep understanding of Django's inner workings. 🤯
  Clearly something to avoid, if at all possible.

Thankfully, using UUIDs the problem is not as large as if we were using the traditional auto-incremented
IDs. With auto-incremented IDs natural keys are needed to ensure stable keys. Otherwise entries will
not be imported if the ID is already used by another entry and imported foreign keys will reference
the wrong object. UUIDs are supposed to be globally unique by default, avoiding most of the problems
in the first place.
