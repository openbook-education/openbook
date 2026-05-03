======================
The OpenBook Community
======================

OpenBook is more than software. It is a growing community where students, educators, administrators,
and developers build better education together. People join with different goals, backgrounds, and
experiences, and that variety is one of our strengths. We aim to keep the community welcoming,
respectful, and open to different cultures, teaching traditions, and ways of thinking.

We invite you to take part in many ways. You may suggest improvements that make learning clearer and
more engaging. If you are an educator, you can shape workflows and content that work in real classrooms.
As an administrator, you can help improve reliability, deployment, and day-to-day operations. Developers,
testers, and technical writers are always needed to implement features, improve quality, extend documentation,
and support long-term maintainability. Contributing is low-threshold and rewarding because your work directly
helps others teach, learn, and collaborate more effectively.


----------------
Online Resources
----------------

General Information:

- Website: https://openbook.education
- Manual: https://openbook-education.readthedocs.org
- Community Discussions: https://github.com/openbook-education/openbook/discussions

Development:

- Source Code: https://github.com/openbook-education/openbook
- Project Planning: https://github.com/orgs/openbook-education/projects/1
- Issues: https://github.com/openbook-education/openbook/issues
- Pull Requests: https://github.com/openbook-education/openbook/pulls

Currently, most resources are on GitHub. For development, we will likely keep it this way to make it easy
for contributors to join. Once the community reaches critical mass, we will likely move community discussions
to more visible channels. LiberaChat, Matrix, Discord? Let us know what would serve the community best.


--------------------
From Idea to Feature
--------------------

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

The community turns ideas into working features through a transparent and iterative workflow:

.. rst-class:: spaced-list

1. Ideas, feature requests, bugs, and general development tasks are collected in the issue tracker.
   Anybody with a GitHub account is invited to submit issues and take part in the discussion.
   All open issues build the product backlog of things that developers want to work on in the future.

2. The GitHub Project board is used to plan short- and mid-term development. Here the issues are
   assigned to milestones (planned releases), and the overall project progress is tracked.

3. For each issue under development a feature branch is created in Git (see
   :doc:`development process <../developers/development-process>`). It is
   typically branched off from the main branch, which later becomes the next
   release.

4. Once ready, a pull request is opened to merge a feature branch into the main line. At this point,
   feature development is typically finished. Sometimes, however, it makes sense to split larger developments
   into smaller chunks and merge them early, even when the feature is not yet usable for end-users. In any case,
   the pull request facilitates code review by other developers.

5. When a new release is ready, it is tagged on the main branch and a GitHub release page is created.
   The release page collects the source code tarballs, Software Bill of Materials (SBOM), and changelogs.
   A release branch is created to allow subsequent hot fixes.

6. Documentation and website will be updated as required.

Because this is still a relatively small project, there are currently no dedicated module maintainers
(sometimes called product owners or product managers). Instead, feature and development decisions are
made jointly by community members participating on GitHub. Anybody is welcome to take part, and we are
happy to help you get started. We look forward to hearing from you.
