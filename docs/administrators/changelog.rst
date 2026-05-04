Changelog
=========

This page described the user-visible changes for each release.

.. contents:: Page Content
   :local:
   :depth: 1


0.0.1-pre1
^^^^^^^^^^

2026-04-26: Updated tooling
---------------------------

Proper documentation was set up and GitHub Actions workflows have been introduced to support the
following activities:

- Git branch protection
- Unit tests
- Code reviews and quality checks
- Dependency updates
- Release and SBOM generation

2026-03-17: Dependency updates and policy
-----------------------------------------

After the project reached a status, where the technical core is working (backend, REST API, ...)
it was put aside for a few months. Now to continue with the development, all dependencies have
been updated to their latest major versions and a policy for dependency handling as been documented.

2024-08-06: Development started
-------------------------------

The plan to reimplement and extend the old lecture-slides.js application is not at least
two years old. :-) Now that I want to extend the application with some basic feedback
elements (to collect feedback from students to improve my course materials) I finally
have an excuse to start this project.

Initial development will be slow. Initially I only want to implement the backend functionality
for feedback surveys and integrate this in my existing materials. But while doing so I want
to lay the groundwork for the following re-implementation, leveraging the scaffolding I did
for Lernspiel Online (another platform I wanted to start for a long time).
