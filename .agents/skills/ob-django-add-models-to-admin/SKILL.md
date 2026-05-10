---
name: ob-django-add-models-to-admin
description: >
  Use when creating or updating Django Admin integrations for models in OpenBook.
  Trigger phrases: admin class, django admin, model admin, admin.py, fieldsets,
  inline admin, import/export, django unfold, djangoql, register admin,
  resource_classes, list_display, readonly_fields, admin sidebar.
user-invocable: true
argument-hint: Descriptions of the models to be added to the Admin
---

# OpenBook Django Admin Conventions

* Integrate every model into Django Admin as a first-class administrative UI.
* Follow the file-mirroring structure and OpenBook admin abstractions exactly.

## Required Structure

* Create one admin source file per model under `admin/`.
* Mirror the model file name from `models/`.
* Register the admin class in `admin/__init__.py`.
* Keep registration order logical for sidebar navigation.

Example:

* `models/learning_goal.py`
* `admin/learning_goal.py`

## Required Base Classes

Always inherit admin classes from:

```python
from openbook.admin import CustomModelAdmin
```

Never inherit directly from Django's `ModelAdmin`.

For import/export resources use:

```python
from openbook.admin import ImportExportModelResource
```

## Import Rules

Always import models from their defining file:

```python
from ..models.learning_goal import LearningGoal
```

Never import models from:

```python
from .. import models
```

except inside `admin/__init__.py` for registration.

Reason: reduce circular import risk.

## Minimal Admin Class

Every admin class should define at minimum:

- `model`
- `list_display`
- `ordering`
- `search_fields`

Example:

```python
class LearningGoalAdmin(CustomModelAdmin):
    """Admin view for learning goals."""

    model         = LearningGoal
    list_display  = ["name", "course", "level", "is_active"]
    ordering      = ["course", "name"]
    search_fields = ["name", "course__name"]
```

## Change List Conventions

### list_display

* Show identifying fields only.
* Keep overview compact and scannable.

### list_display_links

* Prefer making all columns clickable.

### list_select_related

* Add all relevant foreign keys.
* Prevent N+1 queries.

### ordering

* Mirror the model `Meta.ordering`.

### search_fields

* Use Django relation traversal:
  `"course__name"`

### list_filter

* Add useful boolean, choice, and FK filters.
* For FK filters prefer:

```python
(field, RelatedOnlyFieldListFilter)
```

when appropriate.

### readonly_fields

* Always include audit fields when present.

## Audit Trail Integration

If the model uses `CreatedModifiedByMixin`:

```python
from openbook.auth.admin.mixins.audit import created_modified_by_fields
from openbook.auth.admin.mixins.audit import created_modified_by_fieldset
from openbook.auth.admin.mixins.audit import created_modified_by_filter
from openbook.auth.admin.mixins.audit import created_modified_by_related
```

Apply them consistently:

```python
list_display        = [*created_modified_by_fields]
list_select_related = [*created_modified_by_related]
list_filter         = [*created_modified_by_filter]
readonly_fields     = [*created_modified_by_fields]
```

Always append:

```python
created_modified_by_fieldset
```

to `fieldsets`.

Never include it in `add_fieldsets`.

## Fieldset Conventions

Always define `fieldsets` for non-trivial models.

Define `add_fieldsets` whenever readonly or auto-generated fields exist.

Rules:

* Group related fields together.
* Use tuples for same-row layout:

```python
("course", "level")
```

* Use Django Unfold tabs for secondary sections:

```python
"classes": ["tab"]
```

* `add_fieldsets` must omit fields unavailable before first save.
* `fieldsets` and `add_fieldsets` must not be identical.

## Inline Conventions

Add inline classes for all related models to make relations explicit.

Place inline classes in the same admin file.

Prefix inline class names with `_`:

```python
class _LearningGoalTextInline(TabularInline):
```

Defaults:

```python
extra            = 0
show_change_link = True
tab              = True
```

Use:

* `TabularInline` for simple layouts
* `StackedInline` for complex layouts

## Import/Export Requirements

Every admin class must support import/export.

Create a resource class:

```python
class LearningGoalResource(ImportExportModelResource):
```

Wire it into the admin:

```python
resource_classes = [LearningGoalResource]
```

Always include:

```python
"id",
"delete"
```

as the first resource fields.

Remember:

```python
resource_classes = [MyResource]
```

must use square brackets.

## Scope-Aware Models

### ScopeMixin models

Use:

* `ScopeFormMixin`
* `ScopeResourceMixin`

### ScopedRolesMixin models

Use:

* `ScopedRolesFormMixin`
* `ScopedRolesResourceMixin`

Inheritance order matters:

```python
class CourseResource(
    ScopedRolesResourceMixin,
    ImportExportModelResource,
):
```

Mixin must come first.

### Scope-role fields

When both scope and role restrictions exist:

* add `ScopeRoleFieldFormMixin`
* add `ScopeRoleFieldInlineMixin` for inlines
* explicitly merge `Media` declarations

## Admin Registration

Register in `admin/__init__.py`:

```python
from openbook.admin import admin_site
from .learning_goal import LearningGoalAdmin
from .. import models

admin_site.register(models.LearningGoal, LearningGoalAdmin)
```

Sidebar order follows registration order.

## Definition of Done

Before finishing, verify:

* Admin file mirrors model file path.
* Admin class inherits `CustomModelAdmin`.
* Resource class exists.
* `resource_classes` is configured.
* Audit helpers are applied when required.
* Audit fields are readonly.
* `fieldsets` and `add_fieldsets` are correct.
* Inlines exist for companion models.
* `extra = 0` on all inlines.
* Admin class is registered in `admin/__init__.py`.
* `list_select_related` prevents obvious N+1 queries.
* Search and filters are useful for administrators.
* Import/export fields include `"id"` and `"delete"` first.

## Anti-Patterns

DO NOT:

* Direct `ModelAdmin` usage
* Monolithic `admin.py`
* Importing models from `..models`
* Missing resource classes
* Missing audit integration
* Identical `fieldsets` and `add_fieldsets`
* Inline placeholder rows (`extra != 0`)
* Missing `list_select_related`
* Dumping every field into `list_display`
* Unstructured edit forms without fieldsets

## Reference Skeleton

```python
from django.utils.translation import gettext_lazy as _
from unfold.admin import TabularInline

from openbook.admin import CustomModelAdmin
from openbook.admin import ImportExportModelResource

from openbook.auth.admin.mixins.audit import created_modified_by_fields
from openbook.auth.admin.mixins.audit import created_modified_by_fieldset
from openbook.auth.admin.mixins.audit import created_modified_by_filter
from openbook.auth.admin.mixins.audit import created_modified_by_related

from ..models.example_model import ExampleModel
from ..models.example_model import ExampleModelText


class ExampleModelResource(ImportExportModelResource):
    """Import/export resource for example models."""

    class Meta:
        model = ExampleModel
        fields = [
            "id",
            "delete",
            "name",
            "is_active",
        ]


class _ExampleModelTextInline(TabularInline):
    """Inline for translated texts."""

    model               = ExampleModelText
    fields              = ["language", "title"]
    ordering            = ["language"]
    extra               = 0
    show_change_link    = True
    tab                 = True
    verbose_name        = _("Translation")
    verbose_name_plural = _("Translations")


class ExampleModelAdmin(CustomModelAdmin):
    """Admin view for example models."""

    model               = ExampleModel
    resource_classes    = [ExampleModelResource]

    list_display = [
        "name",
        "is_active",
        *created_modified_by_fields,
    ]

    list_display_links = [
        "name",
        "is_active",
    ]

    list_select_related = [
        *created_modified_by_related,
    ]

    list_filter = [
        "is_active",
        *created_modified_by_filter,
    ]

    readonly_fields = [
        *created_modified_by_fields,
    ]

    ordering = [
        "name",
    ]

    search_fields = [
        "name",
    ]

    fieldsets = [
        (None, {
            "fields": [
                ("name", "is_active"),
            ],
        }),
        (_("Description"), {
            "classes": ["tab"],
            "fields": [
                "description",
            ],
        }),
        created_modified_by_fieldset,
    ]

    add_fieldsets = [
        (None, {
            "fields": [
                ("name", "is_active"),
            ],
        }),
        (_("Description"), {
            "classes": ["tab"],
            "fields": [
                "description",
            ],
        }),
    ]

    inlines = [
        _ExampleModelTextInline,
    ]
```

```python
from openbook.admin import admin_site

from .. import models
from .example_model import ExampleModelAdmin


admin_site.register(models.ExampleModel, ExampleModelAdmin)
```
