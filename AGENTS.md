# AI Coding Agents

Mantra for all AI coding agents:
    - Keep answers short and on the point, when talking to the user.
    - Avoid fillers.
    - Never silently assume. When in doubt: ask

This repository defines custom agents in `.agents/agents/`.
Choose exactly one primary agent for a task:

## Interactive Guides

These agents guide you through multi-step workflows with a design-first philosophy, asking clarifying questions before implementation:

- `ob-django-backend-feature-guide`
    - Use when implementing a new backend feature in OpenBook across one or more Django apps. Guides through architecture, model design, admin integration, REST API exposure, unit tests, and fixtures.
    - Trigger phrases: backend feature, feature implementation, django app design, model design, admin integration, api exposure, fixtures, unit tests.
    - [Full spec](.agents/agents/ob-django-backend-feature-guide.md)

## Implementation Agents

These agents handle focused, concrete coding tasks and write code directly:

- `ob-frontend-developer`
    - Use when implementing, refactoring, reviewing, or testing TypeScript/Svelte frontend code.
    - Trigger phrases: typescript, frontend, svelte, component, tailwind, daisyui, ui, route, store, state, openapi client, npm, eslint.
    - [Full spec](.agents/agents/ob-frontend-developer.agent.md)

- `ob-python-developer`
    - Use for implementing, refactoring, reviewing, or testing Python/Django backend code.
    - Trigger phrases: python, django, backend, model, view, serializer, migration, unit test, pytest, manage.py, poetry, docstrings.
    - [Full spec](.agents/agents/ob-python-developer.agent.md)

- `ob-tech-writer`
    - Use when writing, editing, or reviewing documentation, manuals, changelogs, READMEs, or RST/Markdown content.
    - Trigger phrases: write docs, update documentation, document this, improve docs, add to manual, write README, edit changelog, RST, reStructuredText, Sphinx docs.
    - [Full spec](.agents/agents/ob-tech-writer.agent.md)

Routing rule for mixed tasks: choose the agent that owns most of the behavior change, and use the others only if the task later needs a focused handoff.
