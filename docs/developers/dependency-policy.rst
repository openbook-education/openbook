=================
Dependency Policy
=================

External dependencies reduce development effort, but they also mean giving up some control over
one's own product. An unmaintained package, a breaking API change, or an incompatible license can
turn a convenience into a major maintenance burden. OpenBook therefore keeps the number of dependencies
as small as practical, and chooses each one deliberately. This page documents how OpenBook evaluates,
adds, and updates dependencies. The policy favors maintainability and traceability over fast but
opaque upgrades.

.. contents:: Page Content
   :local:


---------------------------
Minimum Acceptance Criteria
---------------------------

When to Add Dependencies
........................

A dependency is a good candidate when it offers functionality that would be too costly or complex
to reimplement or is small and limited in scope, making it easy to replace or drop. Despite that,
if it deeply touches our feature set beyond technical infrastructure, rolling our own solution is
preferred. Because, of course, code reuse is generally a good idea. But we agree with Joel Spolsky
when he writes:

   *If it’s a core business function — do it yourself, no matter what.*

   -- `Joel on Software: In Defense of the Not-Invented-Here Syndrome
      <https://www.joelonsoftware.com/2001/10/14/in-defense-of-not-invented-here-syndrome/>`_

The linked blog post explains the rational behind this credo. The short version is, that there
needs to be space where you actually add value and, more importantly, you must be in control
of it. Plus, custom code allows to optimize for your actual requirements.

.. seealso::

   The blog post was later published in print. The book is a classic text on software development,
   still relevant today.

   *Joel on Software --- And on Diverse and Occasionally Related Matters That Will Prove of
   Interest to Software Developers, Designers, and Managers, and to Those Who, Whether by
   Good Fortune or Ill Luck, Work with Them in Some Capacity*; Joel Spolsky; 2004

Baseline Criteria
.................

Every dependency must satisfy all of the following before any further evaluation takes place.
If a candidate fails any one criterion, it  must not be integrated in the codebase.

**License**
  Must carry a clear license statement, and the license must be compatible with
  `AGPL-3.0 <https://www.gnu.org/licenses/agpl-3.0.html>`_. Copyleft licenses (GPL, LGPL, AGPL)
  are acceptable for dependencies that are not distributed as part of the application binary or
  bundle. Permissive licenses (MIT, BSD, Apache 2.0, ISC) are always acceptable. Proprietary or
  "source-available" licenses need explicit review.

**Formal Release**
  Must have at least one tagged, versioned release on its package registry (PyPI, npm, etc.).
  Depending on a git commit or an unreleased ``main`` branch is not acceptable, because this
  cannot guarantee maintenance and upgrades.

**Semantic Versioning**
  Must use, or clearly commit to, `Semantic Versioning <https://semver.org/>`_, or a similar
  versioning scheme, so that the impact of updates can be anticipated.

**Active Maintenance**
  Must show evidence of active development: at least one commit **and** at least one release
  within the past 12 months. Projects that are archived, explicitly abandoned, or have had no
  activity for over a year are disqualified. Exceptions are tiny and stable packages that
  typically don't need active maintenance beyond testing with upgraded peer dependencies.

**No Active CVEs**
  Must not carry known unpatched security vulnerabilities at the time it is introduced.
  Check the package's advisory database (e.g., `GitHub Advisory Database <https://github.com/advisories>`_,
  ``pip-audit``, ``npm audit``).


------------------------------
Assessment of New Dependencies
------------------------------

Choosing the right dependency requires deliberate, structured evaluation. The three phases below
walk through that process from initial search to final decision. All evaluation results should be
recorded in a dedicated GitHub issue for each intended dependency.

Phase 1: Discovery
..................

The discovery phase produces a closed list of qualified candidates to carry into assessment.

**1.1 Choosing the depth of evaluation.** Not every dependency warrants the same level of scrutiny.
Before searching for candidates, estimate the *impact factor* --- an ordinal value from 0 to 7
that expresses how deeply the new dependency will affect the architecture and how difficult it
would be to replace later:

.. rst-class:: spaced-list

- Impact 0–1: Evaluation can be skipped (baseline criteria still apply).
   - **0:** Not influenceable (e.g., an npm peer-dependency).
   - **1:** Optional or minor; the product works fine without it.
- Impact 2–3: Brief assessment is sufficient; exploration/prototyping can be omitted.
   - **2:** Utility with locally limited scope; could be reimplemented if needed.
   - **3:** Utility with potentially wide scope across multiple modules.
- Impact 4–6: Full assessment is highly recommended; exploration should be considered.
   - **4:** Supports a minor feature relevant to some users.
   - **5:** Supports a major feature relevant to many users.
   - **6:** Supports a critical feature relevant to most users.
- Impact 7: Full assessment and exploration are mandatory.
   - **7:** Key architectural component; replacing it would mean rewriting much code.

**1.2 Define search criteria.** Start with the baseline eligibility criteria and extend them with any
requirements specific to this dependency. Express each criterion as an inclusion or exclusion rule
and assign it a priority using `RFC 2119 <https://www.rfc-editor.org/rfc/rfc2119>`_ language.
For example:

- **Must** provide an API for …
- **Should** support TypeScript type declarations.
- **May** include a built-in router.

**1.3 Search for candidates.** Search the relevant package registries and ecosystems for packages that
satisfy the must-have criteria. Record every candidate that passes, even if it looks weaker; the
assessment phase will rank them objectively. The latest now, create an issue in GitHub and write
down the search criteria, their rationale, and the resulting candidate list.


Phase 2: Assessment
...................

The assessment phase narrows the candidate list to at most two or three finalists using
measurable, reproducible metrics.

**2.1 Define Measurable Metrics.** Decide, whether additional metrics beyond the ones
shown below are needed. Typically, the default set is sufficient.

**2.2 Collect data.** For each candidate, collect the following raw data from its public code
repository (GitHub, GitLab, etc.) and package registry:

=====================  =============================================  =============
Metric                 What to Measure                                Dimension
=====================  =============================================  =============
Project Age            Months since first commit / initial release    Maturity
Project Size           Lines of source code (use ``cloc``, ``scc``)   Complexity
Development Activity   Commits ÷ (Age × Lines of Code)                Maintenance
Release Activity       Released versions ÷ (Age × Lines of Code)      Maintenance
Community Activity     Contributors ÷ (Age × Lines of Code)           Maintenance
Issue Handling         Closed issues ÷ Total issues (percentage)      Quality
=====================  =============================================  =============

The maintenance metrics intentionally normalize raw counts by age and size so that older or larger
projects aren't unfairly penalized for having more commits or releases in absolute terms.
Supplementary, case-specific metrics (e.g., bundle size, transitive dependency count) may be
added when the impact factor warrants it.

**2.3 Calculate the assessment score.** For each metric, rank all candidates against one another:
the best candidate receives ``n`` points (where ``n`` is the number of candidates), the worst
receives one point, and ties share the same rank. The *assessment score* for each candidate is
the sum of all its partial scores.

.. note::

   For Project Size, *fewer* lines of code is better (less complexity to carry).
   For all other metrics, *higher* is better.

Use the assessment scores to reduce the list to the two or three candidates with the highest
scores. The goal is to eliminate candidates that are clearly inferior before investing time in
prototyping. On the other hand, if there is already a clear winner and the impact factor falls
between two and three, the result from this phase can be treated as the final decision.

Phase 3: Exploration
....................

The exploration phase adds practical, hands-on evidence to complement the data-driven assessment.
It is used when the impact factor is 4 or higher, or when the assessment scores are too close
to pick a winner objectively.

**3.1 Define research questions.** Before writing any code, list the questions that need to be
answered in order to make a confident decision. Frame each question so that the answer can be
expressed numerically or on an ordinal scale:

- *Measured number:* e.g. "How many lines of code are needed to implement X?"
- *Package attribute:* e.g. "Does it support Y? No / Yes / Multiple alternatives"
- *Subjective quality:* e.g. "How readable is the code? Very good / Good / Acceptable / Poor"

There are no default questions. For each evaluation new highly-relevant questions must be defined.

**3.2 Build comparable prototypes.** Build a small but representative prototype for each remaining
candidate. You could choose to create a new git repository for this, so as not to clutter the
main git repository. Add the link to the new repo to the tracking issue. The prototype should be
large enough to give genuine insight into developer experience and architectural fit, but small
enough to be feasible for all candidates. Good targets include:

- A representative subset of the actual feature the dependency will support.
- Any integration point that is unclear from the documentation alone.

Document the insights from each prototype (README files or a dedicated section of the tracking
issue are both fine). Where possible, identify prototype code that could be carried over directly
into the product.

**3.3 Calculate the final score.** Extend the assessment table with the prototype results and apply
the same ranking method. The candidate with the highest *final score* is the chosen dependency.
Document the complete evaluation --- search criteria, raw data, scores, and the final decision ---
in the GitHub issue or pull request that introduces the dependency.


-----------------------------------
Version Upgrades and Security Fixes
-----------------------------------

Keeping dependencies current reduces the risk of security vulnerabilities and ensures OpenBook
benefits from bug fixes and improvements in upstream packages. At the same time, unchecked upgrades
can introduce regressions. The process described here strikes a balance between automation, timely
upgrades, and manageable reviewer workload.

Automated Upgrades
..................

OpenBook uses `Renovate <https://docs.renovatebot.com/>`_ to automate version management. A
scheduled CI job runs every week and scans all package manifests --- ``pyproject.toml``,
``package.json``, and related lock files --- for outdated dependencies. For every detected update,
Renovate opens a pull request with the version bump applied.

Each pull request triggers the full test suite matrix across all supported environments. Pull
requests for patch and minor releases are merged automatically once all checks pass. Major
version bumps require manual review, because they may contain breaking API changes that the test
suite does not fully cover. A developer reviews the upstream changelog, checks for deprecations,
and merges the pull request when satisfied.

Security Patches
................

Upgraded dependencies land in a customer installation only when a new OpenBook release is cut and
deployed. For routine upgrades this is acceptable, but for fixing security vulnerabilities this is
too late. For this reason, OpenBook maintains a release branch in Git for each supported version.
When a critical vulnerability is confirmed, the dependency fix is backported to the relevant release
branch and a patch release is tagged from there. This allows administrators to apply the fix to
running installations without also pulling in unrelated feature changes.

.. seealso::

   :doc:`versioning-and-releases` describes how release branches are managed and when a patch
   release is warranted.
