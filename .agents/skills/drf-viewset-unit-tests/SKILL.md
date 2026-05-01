---
name: drf-viewset-unit-tests
description: 'Generate Django REST Framework ViewSet unit tests with Django TestCase and APIClient.login. Use when creating or updating tests for list/search/sort/pagination, CRUD, authentication, permissions, and 403/404 behavior.'
argument-hint: 'ViewSet path/name plus app label and model permissions (for example: openbook.api.SiteViewSet)'
user-invocable: true
---

# DRF ViewSet Unit Tests

Create consistent, permission-aware unit tests for Django REST Framework ViewSets.

## When To Use

- Add tests for a new `...ViewSet`.
- Expand incomplete ViewSet tests.
- Standardize test style and response assertions.

## Required Inputs

- ViewSet class and module path.
- Router basename or resolved endpoints.
- Model permissions required per action (`view`, `add`, `change`, `delete`).
- Fields required for create and update payloads.
- Whether the serializer/model includes file fields.

If any input is missing, inspect the code before writing tests.

## Rules

- Inherit from `django.test.TestCase`.
- Name class `XYZ_ViewSet_Tests`.
- Add class docstring: `Tests for the <ViewSetName> REST API.`
- Keep method names short (`test_list_ok`, `test_create_forbidden`).
- Add short docstring per test method.
- Add `setUp` only when needed. No `setUp` docstring.
- Use `APIClient.login()`, never `force_authentication()`.
- For PATCH against models with file fields, pass `format="json"`.

## Endpoint Resolution

1. Determine list URL from router basename: `reverse('<basename>-list')`.
2. Determine detail URL: `reverse('<basename>-detail', args=[obj.pk])`.
3. If basename is unclear, derive it from router registration before writing tests.

## Test Matrix

Write tests for these cases.

1. List success with permission.
2. List denied without permission (`403`).
3. Search via `_search` returns filtered `results`.
4. Sort via `_sort` returns expected order.
5. Pagination via `_page` and `_page_size` returns paged envelope.
6. Create success with permission.
7. Create denied without permission (`403`).
8. Update success with permission.
9. Update denied without permission (`403`).
10. Partial update success with permission.
11. Partial update denied without permission (`403`).
12. Delete success with permission.
13. Delete denied without permission (`403`).
14. Non-existing detail object returns `404` (no object-existence leak).

## Assertions

- List response shape:
  `{'count': <int>, 'next': <url-or-null>, 'previous': <url-or-null>, 'results': <list>}`
- Use status assertions for each operation (`200`, `201`, `204`, `403`, `404`).
- Verify key state changes after create, update, partial update, delete.
- Verify no state change for forbidden operations.

## Minimal Output Template

Use this structure when generating tests.

```python
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class XYZ_ViewSet_Tests(TestCase):
    """Tests for the XYZViewSet REST API."""

    def setUp(self):
        self.client = APIClient()
        # create users, permissions, and fixtures

    def test_list_ok(self):
        """List should return paginated results for authorized user."""
        pass

    def test_create_forbidden(self):
        """Create should fail for user without add permission."""
        pass
```

## Quality Gate Before Returning

1. Every CRUD action has both allowed and forbidden coverage.
2. List tests include `_search`, `_sort`, `_page`, `_page_size`.
3. Missing objects are validated with `404`.
4. Login uses `APIClient.login()` only.
5. Method and docstring wording is concise.
