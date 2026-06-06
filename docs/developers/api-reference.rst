=============
API Reference
=============

OpenBook exposes two HTTP APIs: a REST API for application data and an authentication API powered by
Django Allauth. Both are described by machine-readable OpenAPI schemas and come with an interactive
ReDoc browser you can use to explore endpoints and try requests during local development.

.. contents:: Page Content
   :local:

.. hint::

  We recommend using the API schema shipped with your OpenBook installation.
  During development, you can run :command:`npm start` and substitute
  ``<your-openbook-host>`` with ``localhost:8000`` in the URLs below.

--------
REST API
--------

The OpenBook REST API contains machine-readable OpenAPI descriptions for clients to generate
type-safe remote stubs. Additionally, an interactive API browser powered by ReDoc is included.
The following URLs expose the API schema on your running OpenBook installation, or you can
preview the latest version included in this manual.

.. list-table::
   :header-rows: 1
   :width: 100%

   * - Format
     - Online
     - Local Installation
   * - YAML schema
     - :download:`Download <../_openapi/openbook.yaml>`
     - ``https://<your-openbook-host>/api/schema/``
   * - JSON schema
     - :download:`Download <../_openapi/openbook.json>`
     - ``https://<your-openbook-host>/api/schema/?format=json``
   * - Interactive ReDoc UI
     - `Open <../_static/openbook.html>`_
     - ``https://<your-openbook-host>/api/schema/redoc/``


------------------
Authentication API
------------------

All user management is handled by Django Allauth, which implements its own REST API.
The following URLs expose the API schema on your running OpenBook installation:

.. list-table::
   :header-rows: 1
   :width: 100%

   * - Format
     - Online
     - Local Installation
   * - YAML schema
     - :download:`Download <../_openapi/auth.yaml>`
     - ``https://<your-openbook-host>/auth-api/openapi.yaml``
   * - JSON schema
     - :download:`Download <../_openapi/auth.json>`
     - ``https://<your-openbook-host>/auth-api/openapi.json``
   * - Interactive ReDoc UI
     - `Open <../_static/auth.html>`_
     - ``https://<your-openbook-host>/auth-api/openapi.html``


-------------
WebSocket API
-------------

Certain features like the AI chat are available through an asynchronous WebSocket API.
The following URLs expose the API schema and documentation on your installation:

.. list-table::
   :header-rows: 1
   :width: 100%

   * - Format
     - Online
     - Local Installation
   * - YAML schema
     - :download:`Download <../_openapi/asyncapi.json>`
     - ``https://<your-openbook-host>/ws/schema/?format=yaml``
   * - JSON schema
     - :download:`Download <../_openapi/asyncapi.json>`
     - ``https://<your-openbook-host>/ws/schema/``
..   * - Interactive UI
..     - `Open <../_static/asyncapi.html>`_
..     - ``https://<your-openbook-host>/ws/docs/``

.. TODO: How to statically build and server the AsyncAPI docs?
