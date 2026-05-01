Accounts and Authentication
===========================

OpenBook uses Django allauth in headless mode for authentication and account
management. This gives the frontend a stable API surface for local login,
email-based flows, and social or SAML-based authentication.

This chapter is intentionally a curated overview. The full endpoint-level
examples remain documented in the specification source under
``doc/specs/django-allauth-headless-api`` and in the local OpenAPI docs
exposed by the running server.

Flow overview
-------------

OpenBook currently supports the following flow groups:

- Local account login and logout.
- Login by one-time code.
- Signup, email confirmation, and password reset.
- Social login via provider redirects, including SAML providers.

Important client-side behavior
------------------------------

All browser clients must handle CSRF tokens correctly:

- Safe requests establish the ``csrftoken`` cookie.
- Follow-up write requests must send ``X-CSRFToken``.

Clients should also treat authentication responses as flow-oriented responses.
Depending on account state and policy, successful primary login may still
require follow-up actions such as email verification.

Further reading
---------------

For full request and response examples, use:

- ``doc/specs/django-allauth-headless-api/api-principles.md``
- ``doc/specs/django-allauth-headless-api/basic-login-logout.md``
- ``doc/specs/django-allauth-headless-api/account-management.md``
- ``doc/specs/django-allauth-headless-api/social-login-saml.md``

For generated endpoint descriptions in a running development setup, open the
local ReDoc view at ``/auth-api/openapi.html``.
