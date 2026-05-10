---
name: ob-git-commit-proposal
description: >
    Analyze staged git changes and propose a conventional commit message with summary.
    Use when you need a commit message following the pattern type(scope): subject plus
    change paragraphs. This skill NEVER commits—it only proposes.
argument-hint: Additional hints for the commit message
user-invocable: true
---

# Conventional Commit Proposal

Analyze staged changes and propose a Conventional Commit message.

## Workflow

1. Inspect staged changes:

   ```bash
   git diff --cached --name-status
   git diff --cached
   ```

2. Determine:

   * primary intent (`feat`, `fix`, `refactor`, etc.)
   * affected scope/module
   * whether multiple unrelated concerns should be split

3. Propose a commit message:

   * Header:

     ```text
     type(scope): subject
     ```
   * Keep subject concise, imperative, lowercase, no period
   * Add a body only when additional context is useful

4. Never execute `git commit`

## Type Selection

Use Conventional Commits / Angular conventions.

Prefer the dominant semantic intent:

* `feat` for user-visible functionality
* `fix` for bug fixes
* `refactor` for structural improvements without behavioral change
* `docs`, `test`, `build`, `ci`, `perf`, `style`, `chore` as appropriate

Avoid using `chore` or `refactor` as generic fallbacks.

## Scope Selection

Derive scope from the affected module, service, package, entity, or subsystem.

Prefer:

* short scopes,
* stable architectural names,
* parent module names for broad changes.

Examples:

* `auth`
* `creditReport`
* `subscriptions`
* `readme`

## Commit Body

When useful, explain:

* why the change was made,
* important behavioral changes,
* migrations, compatibility impacts, or operational implications.

Focus on intent and impact rather than low-level implementation details.

## Rules

* Never run `git commit`
* Never invent changes not present in the diff
* Suggest splitting unrelated staged changes
* Prefer semantic intent over file count
* Keep commits focused and cohesive

## Good Examples

```text
feat(auth): add refresh token rotation

Rotate refresh tokens after each successful authentication to reduce
token replay risk and improve session security.
```

```text
fix(cache): prevent duplicate coface requests

Avoid parallel cache misses triggering duplicate upstream requests for
identical report lookups.
```

## Bad Examples

```text
update stuff
```

```text
refactor(core): change code
```

```text
feat(auth): added login feature.
```
