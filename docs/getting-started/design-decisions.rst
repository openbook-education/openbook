============================
Design Decisions in OpenBook
============================

OpenBook is shaped by deliberate choices in educational philosophy, technology, and licensing.
This page records the reasoning behind those choices so that contributors, educators, and
administrators understand what the project is trying to achieve and why.

.. contents:: Page Content
   :local:


------------------------------
Educational Design Decisions
------------------------------

OpenBook shares surface similarities with established Learning Management Systems such as Moodle
or ILIAS: It organises courses, tracks learner progress, and delivers interactive content. But
it differs from them in scope, focus, and underlying assumptions about how learning works.
While recognizing the value of said LMS, both didactically and to promote Free Software in
education, these differences are intentional and stem from three educational design decisions.

The Textbook as a Learning Medium
..................................

The printed textbook has been the dominant vehicle for transferring knowledge for centuries.
When Gutenberg's letterpress made it possible to replicate texts at scale, it also made systematic
education at scale possible for the first time. The textbook became the shared artefact around
which curricula, teachers, and students could coordinate. Decades of research in Computer-Aided
Teaching (CAT) then explored how digital media could enhance that artefact with multimedia,
interactivity, and immediate feedback without abandoning the clarity and structure that makes
a good textbook valuable.

OpenBook inherits this tradition deliberately. Rather than treating learning material as a
collection of files to download (LMS can do much more, but in practice are often used merely
to distribute static files), OpenBook organises content into structured textbook pages that
students read and interact with directly. PDFs remain available where they are the most practical
format, but the primary learning surface is the interactive page. Comprehension checks, quizzes,
and assignments are not bolt-on features; they are woven into the content itself, because
interactivity improves retention and reveals misunderstanding early.

A Modern Learning Model
........................

Traditional LMS platforms accumulated their feature sets over decades, resulting in systems that
are powerful but often difficult to navigate for both educators and learners. OpenBook takes a
different position: it is built by educators and students, for educators and students, and its
feature set reflects what those groups actually need rather than what is technically possible.
In certain cases, traditional LMS are therefore be a better choice to satisfy special demands,
but day to day teaching and learning can be greatly improved with OpenBook.

At the heart of the system is an explicit learner model. Every learner has associated learning
targets, competency goals, and a progress record that grows as they work through content. This
model is not hidden inside the platform; it is surfaced continuously to both the learner and the
educator. Students always know where they stand and what comes next. Educators gain a transparent
view of group-level progress that helps them direct attention where it is most needed, without
requiring them to master a complex analytics platform.

AI at the Core
..............

The built-in AI assistant, ELISA --- named in homage to Joseph Weizenbaum's ELIZA --- is not an
add-on. It is central to how OpenBook delivers on its educational promises.

Most AI tools in education act reactively: they answer a question when prompted and then fall
silent. ELISA works differently. It continuously assesses each learner's progress against their
goals and acts proactively: selecting the most relevant content from available textbooks, adding
supplementary explanations when a concept appears to be unclear, and suggesting or generating
additional exercises tailored to the individual. The learner is always in the loop since ELISA
remains in constant, visible interaction with the human it is supporting.


------------------------------
Technological Design Decisions
------------------------------

Python and Django
.................

Academia has a long history of building educational tools in PHP, a technology choice that
prioritised easy hosting over long-term maintainability. OpenBook deliberately moves away from
that tradition. Python was chosen for its readability and the quality of its ecosystem, and
Django for the stability and pragmatism it brings: a mature ORM, a built-in admin interface, a
strong security track record, and a community that takes long-term maintenance seriously.

Like PHP, Django is admittedly not a new framework, either. But that is precisely the point.
OpenBook is intended to run reliably in institutional environments for many years. A framework
with a decade-long track record and a clearly documented upgrade path is a safer foundation than
a more fashionable alternative, and it occupies a productive middle ground between a minimal
micro-framework (or plain programming language like PHP) and a heavyweight enterprise platform.

Lean by Design
..............

Modern LMS platforms have grown into sprawling systems that try to serve every possible use case.
The result is that they are difficult to deploy, difficult to maintain, and difficult for end
users to navigate. OpenBook takes the opposite approach: a lean, focused feature set that covers
the core teaching and learning workflow well, rather than everything marginally. Though we have
to admit, that hosting PHP applications is easier.

This philosophy has a direct structural consequence: there is no plugin marketplace. Marketplaces
tend to fragment the ecosystem, introduce unpredictable maintenance burdens, and gradually erode
the coherence of a platform as third-party extensions pull in different directions or stop being
adapted to new application versions. Instead, OpenBook provides a modular, well-structured codebase
and a flexible configuration layer that administrators can use to adapt the system to their institution's
needs without touching the source code.

Frontend and Admin Panel Separation
...................................

OpenBook maintains a clear architectural boundary between the educator and learner-facing frontend
and the Django-based administration panel. The frontend is a TypeScript/Svelte application that
communicates with the backend through a REST API and Websocket endpoint. The admin panel, by contrast,
uses Django's built-in administration framework, extended with Unfold for an improved interface.

This separation keeps the two surfaces focused: the frontend is optimised for the learner and
educator experience; the admin panel is optimised for operators managing the platform. It also
means that the frontend can evolve independently of the admin tooling, and that third parties
can build alternative frontends against the same API, or connect OpenBook with other systems,
without forking the entire application.


---------------------------
Commercial Design Decisions
---------------------------

OpenBook is 100% Free and Libre Software, licensed under the GNU Affero General Public License
version 3 (AGPL-3.0) or later. That choice is intentional. Education and the technology that
supports it must be accessible to everyone, without financial barriers, vendor lock-in, or
closed-source components that undermine trust in the tools learners and institutions depend on.

There is no premium version of OpenBook, no closed-source addon market, and no hosted-only
feature tier. Every capability in the system is available in the publicly distributed source
code. Anyone is free to download, install, modify, and redistribute OpenBook under the terms
of the AGPL-3.0. The copyleft provision of that licence ensures that improvements made to the
codebase remain available to the community, which sustains the project over time.

Side-note to other AI-assisted educational products: This should be the norm for any project
that receives even the smallest amount of public funding. Using public funding to build
closed-source systems is unacceptable to us!

Everyone is invited to participate --- as a user, a contributor, or a community member. The
:doc:`community` page describes how to get involved.
