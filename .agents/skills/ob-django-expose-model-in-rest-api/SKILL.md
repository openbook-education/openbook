---
name: ob-django-expose-model-in-rest-api
description: >
  Use when exposing a Django model through the OpenBook REST API using
  Django REST Framework. Trigger phrases: create viewset, expose model,
  rest api, serializer, filterset, routes.py, DRF endpoint,
  flex fields, custom action, register router.
user-invocable: true
argument-hint: Description of the REST API to be exposed
---

# Expose Django Models in the REST API

Expose models through Django REST Framework using the OpenBook API conventions.

## Objectives

* For every exposed model, create:
    1. A `ViewSet`
    2. A `Serializer`
    3. A `FilterSet`
    4. A route registration in `routes.py`
* Keep serializers, filters, and viewsets together in the same file under `viewsets/`.

# File Layout

* Mirror the structure of `models/` and `admin/`. Example:
    * `models/learning_goal.py`
    * `admin/learning_goal.py`
    * `viewsets/learning_goal.py`
* Do NOT place API code in `__init__.py`.

# ViewSet Rules

## Base Structure

Always inherit in this exact order:

```python
class MyViewSet(ModelViewSetMixin, ModelViewSet):
```

* The mixin order is mandatory so object-level permission checks work during creation.
* For public list/retrieve endpoints, prepend: `AllowAnonymousListRetrieveViewSetMixin`

Example:

```python
class PublicCourseViewSet(
    AllowAnonymousListRetrieveViewSetMixin,
    ModelViewSetMixin,
    ModelViewSet,
):
```

## Required Decorators

TODO:
* Every ViewSet must use:

    ```python
    @extend_schema(...)
    @with_flex_fields_parameters()
    ```

* `extend_schema()` groups endpoints in OpenAPI output.
* `with_flex_fields_parameters()` documents `_fields`, `_omit`, and `_expand`.

## Required Attributes

Every ViewSet must define:

* `queryset`
* `serializer_class`
* `filterset_class`
* `search_fields`
* `ordering`

Example:

```python
queryset         = Course.objects.all()
serializer_class = CourseSerializer
filterset_class  = CourseFilter
ordering         = ["name"]
search_fields    = ["name", "description"]
```

## Queryset Rules

* Usually use: `<Model>.objects.all()`
  This defines the maximum accessible dataset before DRF permission filtering.
* Avoid custom filtering in `queryset` unless globally required.

## Ordering Rules

* Mirror the model `Meta.ordering` value.
* This keeps admin UI and REST API behavior consistent.

## Search Field Rules

* Use focused, user-meaningful fields only.
* Do not expose excessive search fields.
* Use Django relation traversal where appropriate.

Example:

```python
search_fields = [
    "name",
    "description",
    "course__name",
]
```

# Serializer Rules

## Base Class

* Always inherit: `FlexFieldsModelSerializer`
* For scoped role owner models: `ScopedRolesSerializerMixin`, `FlexFieldsModelSerializer` in exactly this order.

## Serializer Placement

* Define serializers in the same file as the ViewSet.
* Serializer classes must appear before the ViewSet definition.

## Required Meta Configuration

Always define:

```python
class Meta:
    model            = MyModel
    fields           = [...]
    read_only_fields = [...]
```

## Field Rules

### Explicit Fields Only

* Always declare `fields` explicitly.
* Never use: `"__all__"`
* Start with `"id"`.
* End with audit fields:
  * `"created_by"`,
  * `"created_at"`,
  * `"modified_by"`,
  * `"modified_at"`,

## Read-Only Fields

* At minimum include: `"id"`, `"created_at"`, `"modified_at"`,
* Add any server-managed fields.

## Expandable Fields

* Declare `expandable_fields` for all FK and M2M relations.
* Use dotted serializer paths as strings:

    ```python
    expandable_fields = {
        "course": "openbook.content.viewsets.course.CourseSerializer",
    }
    ```

* For M2M:

    ```python
    expandable_fields = {
        "permissions": (
            "openbook.auth.viewsets.permission.PermissionSerializer",
            {"many": True},
        ),
    }
    ```

* Never directly import serializers from other files.
* Always use dotted import path strings to avoid circular imports.

## Custom Serializer Fields

* Use custom serializer fields when raw FK IDs are not user-friendly.
* Common built-in fields: `UserField`, `RoleField`, `ScopeTypeField`
* Only add custom fields when they provide meaningful API usability improvements.

Example:

```python
created_by = UserField(read_only=True)
```

## ScopedRolesSerializerMixin Rules

For `ScopedRolesMixin` models:

* Use `ScopedRolesSerializerMixin`
* Spread its Meta field collections instead of duplicating them

Example:

```python
fields = [
    "id",
    "name",
    *ScopedRolesSerializerMixin.Meta.fields,
]
```

# FilterSet Rules

## Base Class Order

* `FilterSet` must always be the final base class.
* Mixin ordering matters.

Example:

```python
class CourseFilter(
    CreatedModifiedByFilterMixin,
    FilterSet,
):
```

## Placement

* Define the FilterSet in the same file as the serializer and `ViewSet`.
* Usually place it before the `ViewSet`.

## Meta.fields Rules

* Expose all practically useful filters.
* Use dictionary syntax:
* Use:
    * `("exact",)` for equality
    * `("exact", "gte", "lte")` for dates and numeric ranges

Example:

```python
fields = {
    "name": ("exact",),
    "created_at": ("exact", "gte", "lte"),
}
```

## Standard Filter Mixins

* Use the matching mixins when applicable:
* Mixins live in `src/openbook/core/admin/mixins` and `src/openbook/auth/admin/mixins`.

| Model Capability         | Filter Mixin                   |
| ------------------------ | ------------------------------ |
| `CreatedModifiedByMixin` | `CreatedModifiedByFilterMixin` |
| `ScopeMixin`             | `ScopeFilterMixin`             |
| `ScopedRolesMixin`       | `ScopedRolesFilterMixin`       |
| M2M permissions          | `PermissionsFilterMixin`       |
| FK permission field      | `PermissionFilterMixin`        |

## Custom Filters

* Use explicit filter fields plus `method=` for non-trivial lookups.
* Use custom methods when traversal or special logic is required.

Example:

```python
role = CharFilter(method="role_filter")

def role_filter(self, queryset, name, value):
    return queryset.filter(role__slug=value)
```

# Route Registration

* Register every ViewSet in `routes.py`.
* Use snake_case model names for `basename`.
* Do NOT register routes in `__init__.py`.

Example:

```python
router.register(
    f"{prefix}/learning_goals",
    LearningGoalViewSet,
    basename="learning_goal",
)
```

# Custom Action Rules

* Use `@action` only for behavior outside standard CRUD operations.
* Every custom action must include: `@extend_schema(...)`
* Document:
    * request serializer
    * response serializer
    * operation summary
    * operation id
* Use:
    * `detail=True` for object endpoints
    * `detail=False` for collection endpoints
* Override `permission_classes` only when necessary.

Example:

```python
@action(detail=True, methods=["put"])
```

# OpenAPI Rules

* Always provide:
    * `x-app-name`
    * `x-model-name`
    * meaningful class docstrings
    * schema annotations for custom actions
* API documentation quality is mandatory.

# Definition of Done

A REST API exposure is complete only when:

* `viewsets/<model>.py` exists
* Serializer, FilterSet, and ViewSet exist in the same file
* `ModelViewSetMixin` precedes `ModelViewSet`
* `@extend_schema` is present
* `@with_flex_fields_parameters()` is present
* `queryset`, `serializer_class`, `filterset_class`, `ordering`, and `search_fields` are defined
* Serializer extends `FlexFieldsModelSerializer`
* Serializer fields are explicitly declared
* `read_only_fields` includes audit fields
* `expandable_fields` covers all FK/M2M relations
* Filter mixins are included where applicable
* `FilterSet` is last in the inheritance chain
* ViewSet is registered in `routes.py`
* OpenAPI schema renders correctly
* No circular serializer imports exist

# Anti-Patterns

DO NOT:

* use `"__all__"` in serializer fields
* directly import serializers from other viewset files
* place `FilterSet` before mixins
* place `ModelViewSet` before `ModelViewSetMixin`
* omit `expandable_fields`
* expose meaningless FK UUIDs when a custom field improves usability
* register API routes outside `routes.py`
* create undocumented custom actions
* expose broad or irrelevant `search_fields`

# Reference Skeleton

```python
class MyModelSerializer(FlexFieldsModelSerializer):
    class Meta:
        model             = MyModel
        fields            = [...]
        read_only_fields  = [...]
        expandable_fields = {...}


class MyModelFilter(CreatedModifiedByFilterMixin, FilterSet):
    class Meta:
        model  = MyModel
        fields = {...}


@extend_schema(
    extensions={
        "x-app-name":   "...",
        "x-model-name": "...",
    }
)
@with_flex_fields_parameters()
class MyModelViewSet(ModelViewSetMixin, ModelViewSet):
    queryset         = MyModel.objects.all()
    serializer_class = MyModelSerializer
    filterset_class  = MyModelFilter
    ordering         = [...]
    search_fields    = [...]
```
