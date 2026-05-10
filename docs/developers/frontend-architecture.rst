=====================
Frontend Architecture
=====================

.. contents:: Page Content
   :local:


------------------
Technology Choices
------------------

The frontend is a single-page app composed of a core library and several add-on libraries that can
also run standalone without a server backend. In part, this is due to the development history of the
project, which started as a pure static single-page app in 2017. To upgrade the tech stack, we are
now using the following frontend tools and frameworks.

.. list-table::
   :width: 100%
   :widths: 1 4

   * - **npm**
     - Package Manager
   * - **esbuild**
     - Code bundler
   * - **TypeScript**
     - Type annotations for JavaScript
   * - **Svelte**
     - Core frontend framework
   * - **TailwindCSS**
     - Styling and theming
   * - **DaisyUI**
     - Pre-defined UI components

.. note::

   More to come as the UI will be built.
