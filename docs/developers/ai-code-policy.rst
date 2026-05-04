===============
AI Code Policy
===============

AI coding assistants have become ubiquitous in software development. This page defines how
contributors to OpenBook are expected to use them and why the human factor remains essential.

.. contents:: Page Content
   :local:
   :depth: 1


---------------
Our Perspective
---------------

Many in the industry fear that human software developers will become obsolete, and some are
actively working toward that outcome. We disagree. AI coding assistants are powerful tools, but
like any tool they have real limitations. Knowing those limitations, and how to work with them,
is what separates effective use from blind reliance.

OpenBook is an educational software built by people who care about both software quality and
learning. We do not see AI tools as a replacement for human developers. We see them as an
accelerant for developers who already know what they are doing, as well as an aid for developers
who are still learning (like we always do).


--------------
General Policy
--------------

Usage of AI coding assistants is permitted and fully encouraged where it improves productivity.
To this end, the repository ships with custom agent definitions and skill prompts to make
those tools more effective within this codebase.

However, we place a high value on the human factor. Software built for education must be
understood, owned, and shaped by the people who write it. Use AI agents as a tool to assist
your work, but do not hand over whole features to an autonomous agent with no human in the
loop. Every significant decision about behaviour, structure, and quality must involve a developer
who understands the consequences.

Remember, that you are responsible for every line of code you submit, regardless of how it was
produced. Specifically:

.. rst-class:: spaced-list

- Review all AI-generated code carefully and understand every line before committing it.
- Ensure the code complies with our development guidelines, coding style, and policies.
- Verify, or at least try to verify, that it respects copyrights and licenses, since
  AI tools may reproduce licensed code without attribution.
- Hand-edit generated code until it meets your quality standards and matches the style and
  patterns of the surrounding codebase.

As a rule of thumb, if you would not be comfortable explaining a piece of code in a review,
it should not be in your pull request (which is a code review, after all).


-------------------
Improving the Tools
-------------------

The quality of AI assistance depends directly on the quality of the instructions it receives.
When you find that an agent produces poor results, misses project conventions, or requires
excessive hand-editing, feel free to improve the tooling rather than accept the friction.
Extend the agent and skill prompts in ``.agents/`` to encode the missing knowledge. If you
find better tools, that aid AI coding assistants to achieve better results, let is know.
Better instructions and tools benefit every contributor who uses them after you.

