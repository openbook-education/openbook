========================
# The OpenBook Community
========================

.. TODO: Write documentation according the notes below. Then remove `#` from headline.
.. be creative.

A welcoming introduction here, welcoming all kinds of users to the community:
educators, students, administrators, developers ... Highlight that we are a
friendly community valuing tolerance, diversity, cultural backgrounds and
more.

Also add a few sentences how different kind of persons could use the software
or contribute and why this is rewarding.


----------------
Online Resources
----------------

Where to find what:

- Website: https://openbook.education
- Manual: https://openbook-education.readthedocs.org
- Source Code: https://github.com/openbook-education/openbook
- Project Planing: https://github.com/orgs/openbook-education/projects/1
- Issues: https://github.com/openbook-education/openbook/issues
- Pull Requests: https://github.com/openbook-education/openbook/pulls
- Community Discussions: https://github.com/openbook-education/openbook/discussions

Once the community grows large enough we will

--------------------
From Idea to feature
--------------------

Describe the typical workflow how ideas are injected into the project and turned
into features:

1. Ideas, feature requests, bugs and general development tasks are collected in
   the issue tracker. Anybody with a GitHub account is invited to submit issues
   and take part in the discussion. All open issues build the product backlog
   of things that developers want to work on in the future.

2. The GitHub Project board is used to plan short- and mid-term development.
   Here the issues are assigned to milestones (planned releases) and the overall
   project progress is tracked.

3. For each issue under development a feature branch is created in Git. (Cross-reference
   to the development process page in the developer section). It is typically branched
   of from the main branch, which later will become the next release.

4. Once ready, a pull request will be opened to merge a feature branch into the
   main line. At this point feature development can be finished. But sometimes
   it makes sense to split larger developments into smaller chunks and merge them
   early, even when the feature is not usable for end-users. In any case, the
   pull requests facilitates code review by other developers.

5. When a new release is ready, it will be tagged on the main branch and a GitHub
   release page will be created. The release page collects the source code tarballs,
   SBOM and changelogs. A release branch will be created to allow subsequent hot
   fixes.

6. Documentation and website will be updated as required.

Since this is a small project, yet, we don't have dedicated module maintainers (product
owners). All feature and development decisions are joint-made by the community,
participating in the discussions on GitHub. Anybody is welcome to take part in any
of these steps.
