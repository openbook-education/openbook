---
name: ob-django-model-unit-tests
description: 'Generate Django model unit tests with django.test.TestCase. Use when creating or updating tests for model behavior, validation, defaults, constraints, and model methods (excluding __str__).'
argument-hint: 'Model path/name plus app label (for example: openbook.models.Site)'
user-invocable: true
---

# Django Model Unit Tests

Create concise, behavior-focused unit tests for a Django model.

## When To Use

- Add tests for a new model.
- Expand incomplete model tests.
- Standardize model test naming and docstring style.

## Required Inputs

- Model class name and module path.
- Required fields and valid minimal fixture data.
- Model defaults, choices, constraints, and custom methods.
- Validation or save-side effects (for example: `clean()`, signals, overridden `save()`).

If any input is missing, inspect the model and related code before writing tests.

## Rules

- Inherit from `django.test.TestCase`.
- Name class `XYZ_Model_Tests`.
- Add class docstring: `Tests for the <ModelName> model.`
- Keep method names short (`test_default_status`, `test_slug_generated`).
- Add short docstring per test method.
- Add `setUp` only when needed. No `setUp` docstring.
- Do not add a test for `__str__` unless explicitly requested.

## Test Matrix

Write tests for applicable behavior in this order.

1. Model can be created with valid minimal data.
2. Required field validation fails when data is missing.
3. Default values are assigned as expected.
4. Choice fields reject invalid values (if constrained).
5. Field constraints are enforced (`unique`, `unique_together`, `UniqueConstraint`).
6. Custom model methods return expected results.
7. `clean()` and `full_clean()` behavior is correct (if implemented).
8. Save-side effects are applied (slug generation, normalization, timestamps, signals).

Skip cases that do not apply to the target model.

## Assertions

- Use `assertEqual`, `assertTrue`, `assertFalse`, `assertIsNotNone` for state checks.
- Use `assertRaises(ValidationError)` for model validation failures.
- Use `assertRaises(IntegrityError)` for DB-level constraint failures when appropriate.
- Verify persisted database state after save operations.

## Minimal Output Template

Use this structure when generating tests.

```python
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase


class XYZ_Model_Tests(TestCase):
    """Tests for the XYZ model."""

    def setUp(self):
        # create shared fixtures if needed
        pass

    def test_create_ok(self):
        """Model should be created with valid minimal data."""
        pass

    def test_required_field_validation(self):
        """Missing required field should raise validation error."""
        pass
```

## Quality Gate Before Returning

1. Class name follows `XYZ_Model_Tests`.
2. Method names and docstrings are concise.
3. No `__str__` test is included.
4. Assertions verify real model behavior, not only status flags.
5. Non-applicable matrix items are explicitly skipped, not ignored silently.
