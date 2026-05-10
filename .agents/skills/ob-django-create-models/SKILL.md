---
name: ob-django-create-models
description: >
  Use when creating, extending, or reviewing Django models in OpenBook.
  Trigger phrases: model, models/, ForeignKey, Meta, mixin, choices,
  translation model, TranslatableMixin, __str__, field options,
  related_name, UUIDMixin, migration, database schema.
user-invocable: true
argument-hint: Detailed description of the models to be created.
---

# OpenBook Django Model Conventions

Follow these rules whenever creating or modifying Django models.

## File and Structure Rules

* Create one Python file per main domain concept inside `models/`.
* Keep closely related helper models (for example translation companion models) in the same file as the parent model.
* Export every model class from `models/__init__.py`.
* Keep naming aligned across `models/`, `admin/`, `serializers/`, and `viewsets/`.

Example:

```python
from .learning_goal import LearningGoal
from .learning_goal import LearningGoalText
```

## Inheritance and Mixins

* Always inherit `UUIDMixin` first.
* Place other core mixins after `UUIDMixin`.
* Place auth mixins last.
* Preserve predictable MRO behavior and cooperative `super()` chaining.

Typical inheritance order:

```python
class ExampleModel(
    UUIDMixin,
    NameDescriptionMixin,
    ActiveInactiveMixin,
    CreatedModifiedByMixin,
):
```

* Only include mixins that match actual domain requirements.
* Most feature models use:
  * `UUIDMixin`
  * one or two content-related core mixins
  * `CreatedModifiedByMixin`
* Only top-level permission boundary objects use `ScopedRolesMixin`.

## Field Declaration Rules

* Use explicit `verbose_name=_("...")` on all user-facing fields.
- Always wrap labels and choice labels in `gettext_lazy` (`_`).
* Always define explicit `related_name` values on relations.
* Prefer intentional field options over framework defaults.

### Nullability

* For text fields:
  * prefer `blank=True` and `default=""`
  * avoid `null=True`
* For non-text optional fields:
  * use both `null=True` and `blank=True`

### Indexing and Constraints

* Use `unique=True` only for actual business uniqueness rules.
* Use `db_index=True` for frequent lookups without uniqueness.
* Add indexes and constraints explicitly in `Meta`.

### Choices

* Define stable enumerations using inner `TextChoices` classes.
* Use `get_FOO_display()` when rendering human-readable values.

Example:

```python
class StatusChoices(models.TextChoices):
    DRAFT = "draft", _("Draft")
    LIVE  = "live", _("Live")
```

## Meta Class Requirements

Every model must define a `Meta` class with at least:

```python
class Meta:
    verbose_name = _("Example")
    verbose_name_plural = _("Examples")
```

Additionally:

* Add sensible `ordering`.
* Add `indexes` and `constraints` where appropriate.
* Translation companion models inherit from `TranslatableMixin.Meta`.

Example:

```python
class Meta(TranslatableMixin.Meta):
    verbose_name = _("Example Text")
    verbose_name_plural = _("Example Texts")
```

## `__str__` Rules

* Always provide a concise human-readable representation.
* Do not override `NameDescriptionMixin.__str__()` unless needed.
* Compose `ActiveInactiveMixin.__str__()` into richer strings when useful.

Example:

```python
def __str__(self):
    return f"{self.name} {ActiveInactiveMixin.__str__(self)}".strip()
```

* Domain methods may modify instance state but should not call `save()`.
* Persistence belongs at the call site.

## Translation Companion Models

Use companion translation models for language-dependent content.

Rules:

1. Keep the parent model language-neutral.
2. Store translations in a separate companion model.
3. Inherit from `UUIDMixin` and `TranslatableMixin`.
4. Add: `parent = models.ForeignKey(..., related_name="translations")`
5. Store only translatable fields in the companion model.
6. Keep naming and structure aligned with the parent model.

Example:

```python
class LearningGoalText(UUIDMixin, TranslatableMixin):
    parent = models.ForeignKey(
        LearningGoal,
        on_delete    = models.CASCADE,
        related_name = "translations",
    )

    summary = models.TextField(
        verbose_name = _("Summary"),
        blank        = True,
        default      = "",
    )

    class Meta(TranslatableMixin.Meta):
        verbose_name        = _("Learning Goal Text")
        verbose_name_plural = _("Learning Goal Texts")
```

## Common OpenBook Mixins

Use these intentionally:

* `UUIDMixin`: UUID primary key; mandatory first mixin
* `NameDescriptionMixin`: name, description, formatting helpers
* `ActiveInactiveMixin`: `is_active`,  inactive marker in `__str__`
* `ValidityTimeSpanMixin`: start/end validation
* `DurationMixin`: configurable durations
* `UniqueSlugMixin`: globally unique slug
* `NonUniqueSlugMixin`: context-scoped slug uniqueness
* `TranslatableMixin`: translation companion support
* `FileUploadMixin`: uploaded file metadata
* `CreatedModifiedByMixin`: audit trail; automatic request-user integration
* `ScopedRolesMixin`: permission boundary object
* `ScopeMixin`: membership in permission scope
* `RoleBasedObjectPermissionsMixin`: delegated object-level permission checks

Always prefer pre-existing mixins over custom fields.
Model Mixins live in `src/openbook/core/models/mixins` and `src/openbook/auth/models/mixins`.

## Definition of Done

Before considering model work complete, verify:

* Model file is correctly placed under `models/`.
* All model classes are exported in `models/__init__.py`.
* `UUIDMixin` is first in inheritance order.
* Mixins match actual domain behavior.
* All user-facing labels are translated with `_()`.
* Field options are intentional.
* Relations define explicit `related_name`.
* `Meta` includes: `verbose_name`, `verbose_name_plural`, appropriate ordering/indexes/constraints
* `__str__` is concise and useful.
* Translation models follow OpenBook conventions.
* No domain method performs implicit persistence.
* Resulting models are migration-safe and internally consistent.

## Anti-Patterns

DO NOT:

* Multiple unrelated domain concepts in one model file.
* `UUIDMixin` not being first.
* Missing `related_name`.
* Implicit framework-generated labels.
* `null=True` on optional text fields.
* Arbitrary default values hiding missing data.
* Business logic calling `save()` internally.
* Translation fields mixed into the parent model.
* Global uniqueness where scoped uniqueness is intended.
* Overusing mixins without domain justification.

## Reference Skeleton

```python
from django.db                import models
from django.utils.translation import gettext_lazy as _

from openbook.core.models.mixins.uuid   import UUIDMixin
from openbook.auth.models.mixins.audit  import CreatedModifiedByMixin


class ExampleModel(UUIDMixin, CreatedModifiedByMixin):
    """Short domain-focused description."""

    class StatusChoices(models.TextChoices):
        DRAFT = "draft", _("Draft")
        LIVE  = "live", _("Live")

    parent = models.ForeignKey(
        "app.ParentModel",
        verbose_name = _("Parent"),
        on_delete    = models.CASCADE,
        related_name = "example_models",
    )

    title = models.CharField(
        verbose_name = _("Title"),
        max_length   = 255,
        blank        = True,
        default      = "",
    )

    status = models.CharField(
        verbose_name = _("Status"),
        max_length   = 32,
        choices      = StatusChoices,
        default      = StatusChoices.DRAFT,
        db_index     = True,
    )

    published_at = models.DateTimeField(
        verbose_name = _("Published At"),
        null         = True,
        blank        = True,
    )

    class Meta:
        verbose_name        = _("Example Model")
        verbose_name_plural = _("Example Models")
        ordering            = ("title",)

        indexes = [
            models.Index(fields=("status", "title")),
        ]

    def __str__(self):
        return self.title
```

### Companion Translation Model

```python
class ExampleModelText(UUIDMixin, TranslatableMixin):
    parent = models.ForeignKey(
        ExampleModel,
        on_delete    = models.CASCADE,
        related_name = "translations",
    )

    summary = models.TextField(
        verbose_name = _("Summary"),
        blank        = True,
        default      = "",
    )

    class Meta(TranslatableMixin.Meta):
        verbose_name        = _("Example Model Text")
        verbose_name_plural = _("Example Model Texts")
```

### `models/__init__.py`

```python
from .example_model import ExampleModel
from .example_model import ExampleModelText
```
