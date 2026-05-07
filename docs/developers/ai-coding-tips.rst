=========================
How To Use AI Code Agents
=========================

AI coding agents like GitHub Copilot can significantly accelerate development — but only when
used with intention. An agent that is given the wrong task, too broad a scope, or too little
context will produce output that looks convincing but requires more effort to fix than it saved.
This page collects practical guidance from OpenBook developers on how to get consistent, useful
results from AI agents: which tasks to delegate, how to structure prompts, when to start fresh,
and how to keep the big picture in view across a multi-step session.

.. contents:: Page Content
   :local:
   :depth: 1


-----------------------
Know When Not to Use AI
-----------------------

AI coding agents are powerful, but there are situations where applying them creates more risk than
value. Before reaching for the AI, consider whether the task actually benefits from it. Avoid delegating
these kinds of tasks to an AI agent:

.. rst-class:: spaced-list

- **Security-critical logic** — authentication flows, permission checks, input sanitization, and
  cryptographic operations must be written by a human who understands the threat model. AI agents
  are getting better at this every day but weaker language models still can produce plausible-looking
  but subtly incorrect security code.

  Using AI to *review* security logic, on the other hand, is fine and actually makes a lot of sense.
  Spotting missing checks or common vulnerability patterns is a good fit as long as a human makes the
  final call.

- **Algorithms or domains you cannot review confidently** — if you cannot tell whether the output
  is correct, you cannot safely ship it. Only use AI for code you are able to critically evaluate.

- **Highly coupled refactors spanning many files** — large structural changes involve implicit
  dependencies and design intent that an AI agent is likely to misread. Plan and execute these by
  hand, using AI for well-scoped sub-tasks within the refactor.

.. note::

   Other tasks where AI works well even without generating code: explaining unfamiliar code,
   troubleshooting errors, exploring design options, and drafting documentation.

.. seealso::

   Also see :doc:`ai-code-policy` for the project's broader stance on responsible AI use.

.. code-block:: text
   :caption: **Example** --- Reviewing security logic

   Review the permission checks in openbook/courses/viewsets.py.
   Look for missing authorization guards, overly broad querysets, and any logic
   that could allow a student to access another student's data.
   Do not make any changes — only report findings.


--------------------------------
Choose the Right Agent and Skill
--------------------------------

OpenBook defines custom agents for each area of the codebase. Selecting the correct agent at the
start of a session feeds it the relevant rules, conventions, and domain knowledge upfront — saving
context and producing more consistent results.

When working in VS Code with GitHub Copilot (or similar AI coding harnesses), select the agent
directly from the chat interface. For example, use ``ob-python-developer`` for backend work,
``ob-frontend-developer`` for Svelte components, or ``ob-tech-writer`` for documentation.
If the tool does not support direct agent selection, name the agent explicitly in your first
prompt. The AI will then discover the agent definition via the ``AGENTS.md`` file at the
repository root.

Skills extend agents with narrower domain knowledge (for example, how to write Django model unit
tests). Auto-discovery works well in most cases, but you can name a skill explicitly in your prompt
if you want to guarantee it is applied.

.. code-block:: text
   :caption: **Example** --- Explicit agent and skill selection

   @ob-python-developer — use the ob-django-model-unit-tests skill.
   Write unit tests for the `is_published` field in openbook/library/models.py.
   Test the default value and validation behaviour.


-------------------------------
Prompt the Codebase Efficiently
-------------------------------

AI agents perform significantly better when you reduce the work they need to do to understand
context. Do not rely on the agent to discover relevant code on its own — point it there directly.

**Anchor to existing examples** — before describing what you want built, link the agent to a
similar existing implementation in the codebase. This communicates style, conventions, and
structure far more precisely than prose instructions alone.

**State your constraints upfront** — tell the agent what it should *not* do as early as what it
should. For example: "Add a ``validated`` field to this model. Do not refactor existing fields or
change the migration history." Constraints prevent the agent from over-engineering or making
unrequested changes.

**Keep changes co-located** — prompts that target a single file or a small cluster of closely
related files produce better results than prompts that span the whole codebase. When a task
requires wide-reaching changes, break it into per-file steps.

.. code-block:: text
   :caption: **Example** --- Provide example and declare constraints upfront

   I want to add a LinkedTextbook model to the library app.
   The model shall have the following fields:

   - Foreign key on Textbook
   - All fields from created by / modified by mixin
   - Alternate textbook name (translatable)

   See openbook/courses/models.py for similar examples.
   Do not create a migration yet.


----------------------------
Work in Small, Focused Loops
----------------------------

The most reliable way to use an AI agent is as an accelerator for tasks you have already defined,
not as a planner for tasks you have not. Vague, open-ended prompts for large tasks produce
inconsistent output that is difficult to review and usually doesn't cover your full intent.

Start each loop by asking the agent to analyze the relevant code and produce a plan — without
making any changes yet. Review the plan carefully and correct it before approving implementation.
Once the agent has produced code, review every changed line. Watch in particular for scope creep
(unrequested refactors or "improvements"), hallucinated imports or API calls, and subtle logic
errors that look plausible at first glance.

A mixed approach works best: let the agent generate a first draft, then hand-edit the parts that
matter most and prompt the agent again for remaining adjustments.

.. code-block:: text
   :caption: **Example** --- Plan-fist prompt

   Look at openbook/courses/serializers.py and plan how to add validation for the
   start_date field — it must not be set in the past. Do not make any changes yet,
   just describe your approach.

.. code-block:: text
   :caption: **Example** --- Implementation prompt after reviewing the plan

   The plan looks good. Please implement the validation now, following the approach
   you described. Only change openbook/courses/serializers.py.

.. tip::

   Keep each prompt focused on one concern. If you find yourself writing a prompt that touches
   authentication *and* serializers *and* a new model field, split it into three prompts.


----------------------
Manage Context Hygiene
----------------------

AI agents maintain a conversation context window. As a session grows longer, earlier instructions
and file contents get pushed out or diluted, and the agent begins to lose track of constraints,
conventions, and the current state of the code. This is the "confused agent" problem: the agent
continues to respond confidently but its output drifts from what you actually need.

Start a fresh conversation when you notice the agent contradicting earlier instructions, forgetting
project conventions, or producing increasingly generic output. A new session costs little and
immediately restores precision.

When starting a new session mid-task, re-anchor the agent explicitly: point it to the relevant
files, paste in the current plan or a short summary of where you are, and restate any constraints
that apply. Treat re-anchoring as a standard step, not a workaround.


.. code-block:: text
      :caption: **Example** --- Re-anchoring at the start of a new session

   New session. I am adding REST API endpoints for the Assignment model.
   The model is in openbook/assignments/models.py.
   The serializer is already done: openbook/assignments/serializers.py.
   Next step: add the ViewSet and register it in the router.
   Use openbook/courses/views.py as a reference for style and structure.


----------------------
Follow the Master Plan
----------------------

For any non-trivial feature or change, keep the big picture written down somewhere — even if only
as a short numbered list in a scratch file. An AI agent works on one prompt at a time and has no
awareness of where a task sits in a larger sequence. That awareness is your responsibility.

.. note::

   AI agents like Copilot *do* maintain TODO lists and attempt to follow a sequence when given
   large tasks. Experience shows, however, that more consistent and predictable results come from
   keeping the master plan under your own control.

Break the master plan into discrete, independently completable steps, and feed the agent one step
at a time. A typical master plan for adding a new feature might look like this:

1. Scaffold a new Django app
2. Design and create the main models
3. Add companion and relationship models
4. Finalize models and write migrations
5. Django Admin integration
6. REST API (serializers, viewsets, routing)
7. Unit tests
8. UI mockups
9. Frontend SPA integration

Each step becomes a focused session with the right agent. Using multiple agents across steps —
each expert in its own domain — produces better results than trying to drive the full sequence
with a single session.

.. code-block:: text
   :caption: **Example** --- Position within the master plan with tight scope for the current step

   We are on step 6 of 9 for the Assignment feature (REST API integration).
   Add a ViewSet for the Assignment model in openbook/assignments/views.py.
   Use openbook/courses/views.py as a reference. Do not touch any other files.
