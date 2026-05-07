---
name: restructured-text-docs-styleguide
description: 'Style guide for writing and editing documentation pages in RST (ReStructured Text) format in the `docs/` directory'
user-invocable: true
---

When creating or modifying documentation pages in ReStructured Text format (RST),
usually within the `docs/` directory, always apply the following style guide:

# File & Layout Structure

* Break lines at 100 characters. Minor overflow is acceptable to improve readability.
* Use exactly two blank lines to separate top-level sections.
* Use one blank line for all other separations (e.g. paragraphs, subsections, directives).
* Do not introduce trailing whitespace.
* Ensure files end with a single newline.

# Document Hierarchy & Headings

- Use a maximum depth of three levels:
    1. Page title
    2. Section
    3. Subsection (no deeper nesting)
- Use Title Case (APA-style) for all headings.
- Instead of multiple sub-sections with one paragraph prefer bold-facing the first words (see example below)
- Prefix incomplete pages or sections with # .
- Begin each page with a one to three sentences introduction.
- Add a local table of contents (title: Page Content) before the first top-level section.

Heading Syntax:

- Page title: overline + underline using =
- Section titles: overline + underline using -
- Subsection titles: underline using .
- Overlines and underlines must match title length.
- Don't mix heading styles.

Example:

```rst
==========
Page Title
==========

This page ... (one to three sentences introducing the page)

.. contents:: Page Content
   :local:


-------------
Section Title
-------------

Normal text paragraph.

Subsection Title
................

Another text paragraph.


-------------------------------
# Unfinished or Planned Section
-------------------------------

**Bold-faced sub-section** --- This is a single paragraph for which a dedicated
headline is a bit overwhelming.

**Another bold-faced sub-section** -- This is another single paragraph.
```

# Content Style & Writing Quality

- Use active voice and present tense.
- Keep sentences concise (one idea per sentence).
- Prefer short paragraphs (4-6 sentences).
- Prefer sentences over bullet/enumeration lists, but use lists when they improve clarity.
- Avoid sections consisting only of bullet points or enumeration lists unless the content is inherently list-based.
- Start sections with a short explanatory paragraph before any list.
- Encourage consistent terminology (define once, reuse).
- Avoid filler phrases and redundancy.
- Avoid vague qualifiers (e.g. ‘usually’, ‘somewhat’) unless necessary.

# Lists & Structure

- Use bullet or lists for enumerations and preconditions.
- Use numbered lists for ordered procedures.
- Keep list items structurally parallel.
- Avoid deeply nested lists (max depth: 2).

# Code, Literals & Formatting

- Use backticks for:
    - inline code
    - commands
    - file paths
    - variables
- Use :: for code blocks.
- Specify language for syntax highlighting where possible.
- Indent code blocks with four spaces.
- Avoid mixing and tabs, always indent with spaces.
- Use double quotes in examples unless conflicting.

# Directives & RST Features

- Prefer:
    - .. directives
    - semantic markup over raw formatting
- Use `:ref:` for cross-references sparingly.
- Avoid raw HTML unless absolutely necessary.

# Admonitions & Emphasis

- Use admonitions to highlight:
    - Important concepts
    - Warnings or dangerous operations
    - Notes and tips
- Keep admonitions except examples short (3-4 sentences, typically).
- Examples can be of any length.
- Collect references to other pages and links in a `.. seealso::` admonition.

Example:

```rst
.. warning::

   This operation deletes data permanently.
```

# Diagrams & Visual Elements

- Use `graphviz` for diagrams (e.g. architecture, flows).
- Insert diagrams for architecture explanations, workflows and similar.
- Use transparent background and colors to make diagrams less boring.
- Provide textual explanation alongside diagrams.
- Use screenshots to support documentation of program features.
- Insert a comment and tell me, when you can't find a good screenshot or visual.
- Horizontally center images and diagrams.
- Always add captions.

Example Diagram:

```rst
.. graphviz::
   :align: center
   :caption: Feature planing and development process

   digraph workflow {
      graph [bgcolor=transparent];
      rankdir = TB;
      node [shape=box, width=2, height=0.5, style="rounded,filled"];

      { rank=same;
         node     [fillcolor="#e3f2fd", color="#1e88e5"];
         ideas    [label="1. Ideas and Issues"];
         planning [label="2. Project Planning"];
      }

      { rank=same
         node     [fillcolor="#e8f5e9", color="#43a047"];
         branch   [label="3. Feature Branch"];
         pr       [label="4. Pull Request and Review"];
      }

      { rank=same;
         node     [fillcolor="#fff3e0", color="#fb8c00"];
         release  [label="5. Release"];
         docs     [label="6. Website Update"];
      }

      ideas -> planning -> branch -> pr -> release -> docs;
   }
```

# Consistency & Maintainability

- Keep terminology consistent across all documents.
- Avoid duplication: use cross-references instead.
- Update all affected references when renaming sections or files.
- Ensure documentation builds without warnings.
- Treat documentation like code: Changes must be complete and consistent.

# Anti-Patterns

- DO NOT mix heading styles
- DO NOT exceed subsection depth
- DO NOT create “TODO-only” sections without context
- DO NOT use bullet lists where prose is clearer
- DO NOT write overly long paragraphs (>5–6 sentences)
- DO NOT introduce unexplained abbreviations
- DO NOT rely on implicit formatting when explicit directives improve clarity
