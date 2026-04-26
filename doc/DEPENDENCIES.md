Dependency Management Guidelines
================================

This document defines how we evaluate and choose new dependencies for OpenBook. The approach is based on a
lightweight but structured evaluation framework designed to balance the benefits of code reuse against the
risks of depending on someone else's work. The full academic treatment of the framework can be found in
(TODO: Insert link, once the paper is published).

1. [Guiding Principles](#guiding-principles)
1. [Baseline Eligibility Criteria](#baseline-eligibility-criteria)
1. [Choosing the Depth of Evaluation](#choosing-the-depth-of-evaluation)
1. [Phase 1 – Discovery](#phase-1--discovery)
1. [Phase 2 – Assessment](#phase-2--assessment)
1. [Phase 3 – Exploration](#phase-3--exploration)
1. [Version Upgrades and Security Fixes](#version-upgrades-and-security-fixes)

Guiding Principles
------------------

External dependencies reduce development effort, but they also mean giving up some control over the product.
An unmaintained package, a breaking API change, or an incompatible license can turn a convenience into a major
maintenance burden. Our goal is therefore to keep the number of dependencies as small as practical, and to
choose each one deliberately. As a rule of thumb, a dependency is acceptable when:

* It offers functionality that would be too costly or complex to reimplement.
* It is small and limited in scope, making it easy to replace or drop.

Even then, it must pass the baseline criteria below and, depending on its impact, should go through the
structured evaluation process described in the following sections.

Before adding a new dependency, please open an issue in GitHub to document the evaluation procedure.

Baseline Eligibility Criteria
------------------------------

Every dependency must satisfy **all** of the following before any further evaluation takes place.
If a candidate fails any one criterion, it is immediately disqualified and must not be integrated
in our codebase!

- [ ] **License:** Must carry a clear license statement, and the license must be compatible with
  [AGPL-3.0](https://www.gnu.org/licenses/agpl-3.0.html). Copyleft licenses (GPL, LGPL, AGPL) are
  acceptable for dependencies that are not distributed as part of the application binary / bundle.
  Permissive licenses (MIT, BSD, Apache 2.0, ISC) are always fine. Proprietary or "source-available"
  licenses need explicit review.

- [ ] **Formal release:** Must have at least one tagged, versioned release on its package registry
  (PyPI, npm, …). Depending on a git commit or an unreleased `main` branch is not acceptable,
  because this cannot guarantee maintenance and upgrades.

- [ ] **Semantic versioning:** Must use, or clearly commit to, [Semantic Versioning](https://semver.org/),
  or a similar versioning scheme, so that the impact of updates can be anticipated.

- [ ] **Active maintenance:** Must show evidence of active development: at least one commit **and** at least
  one release within the past 12 months. Projects that are archived, explicitly abandoned, or have had no
  activity for over a year are disqualified.

- [ ] **No active CVEs:** Must not carry known unpatched security vulnerabilities at the time it is introduced.
  Check the package's advisory database (e.g., [GitHub Advisory Database](https://github.com/advisories),
  `pip-audit`, `npm audit`).

Choosing the Depth of Evaluation
---------------------------------

Not every dependency warrants the same level of scrutiny. Before searching for candidates, estimate the **impact factor**
– an ordinal value from 0 to 7 that expresses how deeply the new dependency will affect the architecture and how difficult
it would be to replace later:

| Impact | Meaning                                                                                                                           |
|:------:|-----------------------------------------------------------------------------------------------------------------------------------|
| **0**  | Not influenceable (e.g., an `npm` peer-dependency required by another package). No evaluation needed; there is nothing to choose. |
| **1**  | Optional or minor – the product works fine without it. Evaluation can be skipped; just make sure scope is limited to a few files. |
| **2**  | Utility with locally limited scope – could be reimplemented if needed.                                                            |
| **3**  | Utility with potentially wide scope across multiple modules.                                                                      |
| **4**  | Supports a minor feature relevant to some users.                                                                                  |
| **5**  | Supports a major feature relevant to many users.                                                                                  |
| **6**  | Supports a critical feature relevant to most users.                                                                               |
| **7**  | Key architectural decision – replacing it would mean rewriting large parts of the codebase.                                       |

* **Impact 0–1:** Evaluation can be skipped (baseline criteria still apply).
* **Impact 2–3:** Brief assessment is sufficient; exploration/prototyping can be omitted.
* **Impact 4–6:** Full assessment is highly recommended; exploration should be considered.
* **Impact 7:** Full assessment **and** exploration are mandatory.

Phase 1 – Discovery
--------------------

The discovery phase produces a closed list of qualified candidates to carry into assessment.

### 1.1 Define search criteria

Start with the baseline eligibility criteria and extend them with any requirements specific to this dependency.
Express each criterion as an inclusion or exclusion rule and assign it a priority (must/should/may using
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) language). For example:

* **Must** provide an API for …
* **Should** support TypeScript type declarations.
* **May** include a built-in router.

### 1.2 Search for candidates

Search the relevant package registries and ecosystems for packages that satisfy the must-have criteria.
Record every candidate that passes, even if it looks weaker; the assessment phase will rank them objectively.

### 1.3 Document findings

Create an issue in GitHub and write down the search criteria, their rationale, and the resulting candidate list.

Phase 2 – Assessment
---------------------

The assessment phase narrows the candidate list to at most two or three finalists using measurable,
reproducible metrics.

### 2.1 Collect data

For each candidate, collect the following raw data from its public code repository (GitHub, GitLab, etc.) and
package registry:

| Metric                   | What to measure                                             | Dimension   |
|--------------------------|-------------------------------------------------------------|-------------|
| **Project Age**          | Number of months since the first commit / initial release   | Maturity    |
| **Project Size**         | Lines of source code (use `cloc`, `scc`, or `find … \| wc`) | Complexity  |
| **Development Activity** | Commits ÷ (Age × Lines of Code)                             | Maintenance |
| **Release Activity**     | Number of released versions ÷ (Age × Lines of Code)         | Maintenance |
| **Community Activity**   | Number of contributors ÷ (Age × Lines of Code)              | Maintenance |
| **Issue Handling**       | Closed issues ÷ Total issues (as a percentage)              | Quality     |

The maintenance metrics intentionally normalise raw counts by age and size so that older or larger projects
aren't unfairly penalised for having more commits or releases in absolute terms.

Supplementary, case-specific metrics (e.g., bundle size, transitive dependency count) may be added when the
impact factor warrants it.

### 2.2 Calculate the assessment score

For each metric, **rank** all candidates against one another: the best candidate receives `n` points
(where `n` is the number of candidates), the worst receives 1 point, ties share the same rank.
The **assessment score** for each candidate is the sum of all partial scores.

> For Project Size, *fewer* lines of code is better (less complexity to carry).
> For all other metrics, *higher* is better.

Use the assessment scores to reduce the list to the two or three candidates with the highest scores.
The goal is to eliminate candidates that are clearly inferior before investing time e.g. in prototyping.
If there is already a clear winner and the impact factor is 2–3, the result from this phase can be
treated as the final decision.

Phase 3 – Exploration
----------------------

The exploration phase adds practical, hands-on evidence to complement the data-driven assessment.
It is used when the impact factor is 4 or higher, or when the assessment scores are too close to
pick a winner objectively.

### 3.1 Define research questions

Before writing any code, list the questions that need to be answered in order to make a confident decision.
Frame each question so that the answer can be expressed numerically or on an ordinal scale:

- *Measured number:*, e.g. "How many lines of code are needed to implement X?"
- *Package attribute:*, e.g. "Does it support Y? No / Yes / Multiple alternatives"
- *Subjective quality:*, e.g.  "How readable is the resulting code? Very good / Good / Acceptable / Poor"

### 3.2 Build comparable prototypes

Build a small but representative prototype for each remaining candidate. You could choose to create a new
git repository for this, so as not to clutter our main git repository. Add the link to the new repo to
the issue.

The prototype should be large enough to give genuine insight into developer experience and architectural fit,
but small enough to be feasible for all candidates. Good targets include:

* A representative subset of the actual feature the dependency will support.
* Any integration point that is unclear from the documentation alone.

Document the insights from each prototype (README files or a dedicated section of the tracking issue are both fine).
Where possible, identify prototype code that could be carried over directly into the product.

### 3.3 Calculate the final score

Extend the assessment table with the prototype results and apply the same ranking method. The candidate with the
highest **final score** is the chosen dependency.

Document the complete evaluation – search criteria, raw data, scores, and the final decision – in the GitHub issue
or pull request that introduces the dependency.

Version Upgrades and Security Fixes
-------------------------------------

* **Routine upgrades** – Dependencies should be updated regularly. We use Renovate for this with two dedicated workflows:

  - `.github/workflows/renovate-minor.yml` runs each Monday morning and proposes patch/minor updates that are
    auto-merged after the Renovate PR checks succeed.

  - `.github/workflows/renovate-major.yml` runs on the first day of each month and proposes major updates in separate
    PRs for manual review.

  For `npm` and Poetry dependencies, Renovate uses a `bump` range strategy. This means weekly non-major updates do not
  just refresh `package-lock.json` or `poetry.lock`; they also raise the declared minimum version in `package.json` and
  `pyproject.toml` when a newer compatible release exists.

  The required CI checks for Renovate PRs regenerate the whole-project CycloneDX SBOM at
  `sbom/openbook.cyclonedx.json` and upload it as an artifact, but do not commit changes to
  the dependency PR branch itself.

  Persistent SBOM updates are produced by `.github/workflows/refresh-sbom.yml`, which creates
  or updates a dedicated SBOM PR on a weekly schedule, after successful Renovate workflow runs,
  or when manually dispatched (for example before a release).

  The same automation also tracks GitHub Actions versions and the pinned image tags in the Docker Compose example under
  `docker/`.

  **Always trigger dependency updates through Renovate rather than running `poetry update` or `npm update` by hand.**
  Manual updates skip the automated pull-request audit trail and the dedicated Renovate PR checks. You can trigger an
  out-of-band Renovate run from the command line or from the GitHub Actions tab:

  ```sh
  npm run deps:update:minor
  npm run deps:update:major
  ```

  The script requires the [GitHub CLI](https://cli.github.com/) (`gh`) to be installed and authenticated.

  The repository must define a `RENOVATE_TOKEN` secret for these automation workflows. Use a fine-grained personal
  access token or GitHub App token that can create pull requests and trigger follow-up workflows. The default
  `GITHUB_TOKEN` is not sufficient here, because PRs created with it do not reliably trigger the Renovate PR check
  workflow or the follow-up checks for SBOM refresh PRs.

* **Major version bumps** – These frequently introduce breaking changes. Review the migration guide before upgrading.
  If the effort is significant, create a dedicated issue and plan the migration explicitly rather than letting it accumulate.

* **Security fixes** – A known CVE in an actively used dependency is treated as a high-priority bug. Upgrade as soon as a
  patched version is available. If no patch exists, assess whether the vulnerability is reachable in our deployment and
  document the decision.

- **Abandoned dependencies** – If a dependency shows no commits or releases for 12 months, open an issue to assess the
  situation. Options are: forking and taking over maintenance, replacing with an alternative, or reimplementing if the
  scope is small enough.
