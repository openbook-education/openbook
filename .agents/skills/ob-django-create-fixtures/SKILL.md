---
name: ob-django-create-fixtures
description: >
  Use when creating, exporting, cleaning, or integrating Django fixtures in
  OpenBook. Trigger phrases: fixture, dumpdata, initial data, bootstrap data,
  seed data, YAML fixture, load_initial_data, natural keys.
user-invocable: true
argument-hint: Description of the fixtures to be created
---

# Django Fixture Creation

Create and maintain Django fixtures as stable, reviewable source code for development bootstrap and initial deployments.

## Workflow

1. Prepare the desired data first using Django Admin or the application UI.
   Only export data that should intentionally become part of the reproducible
   baseline project state.

2. Export fixtures into `fixtures/<app>/` using YAML format and natural keys.

   Preferred command pattern:

   ```bash
   python manage.py dumpdata \
       --format yaml \
       --natural-foreign \
       --natural-primary \
       <app_or_model>
   ```

3. Keep the file extension as `.yaml`. Django fixture discovery depends on this extension.

4. After export, treat fixtures as maintained source code:
   * Reorder entries logically.
   * Group related objects together.
   * Remove unnecessary `null` values.
   * Remove irrelevant fields when safe.
   * Add comments where relationships are non-obvious.
   * Keep formatting readable and diff-friendly.

5. Avoid exporting unrelated or excessive data.
   Fixtures should remain focused, understandable, and reviewable.

6. When fixtures are intended for project bootstrap, integrate them into the initial loading workflow handled by:

   ```text
   src/openbook/core/management/commands/load_initial_data.py
   ```

## Conventions

* Prefer YAML fixtures over JSON for readability and maintainability.
* Always use `--natural-foreign` and `--natural-primary` during export.
* Do not introduce global natural-key strategies across all models unless explicitly required by the domain model.
* Remember that generic relations still contain concrete `object_id` values.
* UUID-based references are acceptable and expected in fixtures.

## Agent Expectations

When generating or modifying fixtures, the agent must:

* Preserve deterministic ordering where possible.
* Keep fixture diffs minimal and readable.
* Avoid unstable references and environment-specific values.
* Preserve UUIDs unless regeneration is explicitly required.
* Avoid embedding transient development data.
* Ensure referenced objects exist within the fixture set or bootstrap workflow.

## Reference Skeleton

```text
fixtures/
└── learning_progress/
    ├── initial_data.yaml
    └── demo_courses.yaml
```

Example export command:

```bash
python manage.py dumpdata \
    --format yaml \
    --natural-foreign \
    --natural-primary \
    learning_progress.Course \
    learning_progress.Lesson \
    > fixtures/learning_progress/initial_data.yaml
```
