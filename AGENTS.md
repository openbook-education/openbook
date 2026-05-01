# AI Coding Agents

This repository defines custom agents in `.agents/agents/`.
Choose exactly one primary agent for a task:

- `frontend-typescript-developer`
    - Use when implementing, refactoring, reviewing, or testing TypeScript/Svelte frontend code.
    - Trigger phrases: typescript, frontend, svelte, component, tailwind, daisyui, ui, route, store, state, openapi client, npm, eslint.
    - Full spec: `.agents/agents/frontend-typescript-developer.agent.md`

- `python-developer`
    - Use for implementing, refactoring, reviewing, or testing Python/Django backend code.
    - Trigger phrases: python, django, backend, model, view, serializer, migration, unit test, pytest, manage.py, poetry, docstrings.
    - Full spec: `.agents/agents/python-developer.agent.md`

- `tech-writer`
    - Use when writing, editing, or reviewing documentation, manuals, changelogs, READMEs, or RST/Markdown content.
    - Trigger phrases: write docs, update documentation, document this, improve docs, add to manual, write README, edit changelog, RST, reStructuredText, Sphinx docs.
    - Full spec: `.agents/agents/tech-writer.agent.md`

Routing rule for mixed tasks: choose the agent that owns most of the behavior change, and use the others only if the task later needs a focused handoff.
