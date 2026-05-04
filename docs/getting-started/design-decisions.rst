==================
# Design Decisions
==================

.. TODO: Write documentation according to plan below. Then remove `#` from headline
.. For most points you must go into much more detail then the notes below.
.. `teaching-and-learning-with-ai.rst` provides the product idea and background-information for this page.

This page records the key educational and technical decisions that shape OpenBook and explains
the reasoning behind them.

.. contents:: Page Content
   :local:
   :depth: 1


1. Educational design decisions
      - Online Textbooks:
         - Letterpress printing for the first time allowed to efficiently conserve and replicate knowledge
         - For decades, if not centuries, teaching and learning evolved around textbooks
         - Computer assisted learning and multimedia enhancements
      - Learning model:
         - Made by students and educators for students and educators
         - Learning targets, competency targets, learning progress, ...
         - Different styles of teaching and learning
         - Similarities to Learning Management Systems but with a lean and modern twist
      - AI super powers:
         - The built-in AI, called ELISA (after Joseph Weizenbaum's Eliza), is not an add-on. It is central to the OpenBook functionality.
         - It creates a truly adaptive learning environment, guiding learners through their learning journey.
         - It doesn't merely answer questions or product output for prompts.
         - It pro-actively structures the whole learning experience, selects contents, provides extra activities and more.

2. Technological design decisions
   - Academia still often uses PHP even for modern developments
   - Python + Django (though also old by now) here for the stability, long-term maintenance and sweet stop between features and minimalism
   - Lean and focused feature set, not trying to be everything to everyone as modern LMS tend to do
   - Therefore, no plugin market place (but highly modular and extensible code)
   - Flexible core with configuration options instead of empty plugin host
   - Separation between frontend and admin panel

3. Commercial design decisions
   - Education and educational technology must be free and accessible to everyone
   - 100% Free and Libre Software
   - No premium version or closed-source addons
   - All sources available under AGPL3 license
   - Everyone is invited to join the community
