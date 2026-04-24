Django Allauth API Principles
=============================

Authentication and account management uses [Django Allauth](https://allauth.org/) under the
hood. This greatly enhances Django's built-in user management to include modern features
like authentication policies (e.g. e-mail verification), multi-factor authentication (mfa)
or social authentication with different types of identity providers. It also provides the
API (the so-called Allauth Headless API) for the frontend SPA and other clients to authenticate.

This document collects some general information about the API that must be understood to
successfully implement it in a client. Some information is copied from the OpenAPI specification.
The rest is based on direct experimentation with the API.

1. [Local OpenAPI Specification](#local-openapi-specification)
1. [Response Format](#response-format)
1. [Authentication Flows](#authentication-flows)
1. [Input Sanitization](#input-sanitization)
1. [CSRF Token Handling in Browser Clients](#csrf-token-handling-in-browser-clients)

Local OpenAPI Specification
---------------------------

When starting the local development server (`npm start` in the root directory or `manage.py runserver`
in the `src` directory), the API specification is available at the following URL:

* JSON format: http://localhost:8000/auth-api/openapi.json
* YAML format: http://localhost:8000/auth-api/openapi.yaml
* HTML format: http://localhost:8000/auth-api/openapi.html

Use the HTML link to view the API in ReDoc.

Use the linked documentation as the actual full reference and the documentation contained in this
repository as an addendum based on manual test cases.

Response Format
---------------

From the OpenAPI specification: Unless documented otherwise, responses are objects with the
following properties:

* The status, matching the HTTP status code.
* Data, if any, is returned as part of the data key.
* Metadata, if any, is returned as part of the meta key.
* Errors, if any, are listed in the errors key.

Example for status code 200:

```json
{
  "status": 200,
  "meta": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdW",
    "is_authenticated": true,
    "session_token": "ufwcig0zen9skyd545jc0fkq813ghar2"
  },
  "data": {
    "methods": [
      {
        "at": 1711555057.065702,
        "email": "email@domain.org",
        "method": "password"
      }
    ],
    "user": {
      "display": "Magic Wizard",
      "email": "email@domain.org",
      "has_usable_password": true,
      "id": 123,
      "username": "wizard"
    }
  }
}
```

Example error:

```json
{
  "status": 400,
  "errors": [
    {
      "code": "invalid",
      "message": "Enter a valid email address.",
      "param": "email"
    }
  ]
}
```

Authentication Flows
--------------------

From the OpenAPI specification: In order to become authenticated, the user must complete a flow,
potentially consisting of several steps. For example:

* A login, after which the user is authenticated.
* A Login, followed by two-factor authentication, after which the user is authenticated.
* A signup, followed by mandatory email verification, after which the user is authenticated.

The API signals to the client that (re)authentication is required by means of a `401` or `410`
status code:

* Not authenticated: status `401`.
* Re-authentication required: status `401`, with `meta.is_authenticated = true`.
* Invalid session: status `410`. This only occurs for clients of type app.

All authentication related responses have status `401` or `410`, and, `meta.is_authenticated`
indicating whether authentication, or re-authentication is required.

The flows the client can perform to initiate or complete the authentication are communicates as part
of authentication related responses. The authentication can be initiated by means of these flows:

* Login using a local account (`login`).
* Signup for a local account (`signup`).
* Login or signup using the third-party provider redirect flow (`provider_redirect`).
* Login or signup by handing over a third-party provider retrieved elsewhere (`provider_token`).
* Login using a special code (`login_by_code`).
* Login using a passkey (`mfa_login_webauthn`).
* Signup using a passkey (`mfa_signup_webauthn`).

Depending on the state of the account, and the configuration of django-allauth, the flows above
can either lead to becoming directly authenticated, or, to followup flows:

* Provider signup (`provider_signup`).
* Email verification (`verify_email`).
* Phone verification (`phone_email`).
* Two-factor authentication required (TOTP, recovery codes, or WebAuthn) (`mfa_authenticate`).
* Trust this browser (`mfa_trust`).

While authenticated, re-authentication may be required to safeguard the account when sensitive
actions are performed. The re-authentication flows are the following:

* Re-authenticate using password (`reauthenticate`).
* Re-authenticate using a 2FA authenticator (TOTP, recovery codes, or WebAuthn) (`mfa_reauthenticate`).

Input Sanitization
------------------

From the OpenAPI specification: The Django framework, by design, does not perform input sanitization.
For example, there is nothing preventing end users from signing up using `<script>` or `Robert'); DROP
TABLE students` as a first name. Django relies on its template language for proper escaping of such
values and mitigate any XSS attacks.

As a result, any `allauth.headless` client must have proper XSS protection in place as well.
Be prepared that, for example, the WebAuthn endpoints could return authenticator names as follows:

```json
{
  "name": "<script>alert(1)</script>",
  "credential": {
    "type": "public-key",
    ...
  }
}
```

CSRF Token Handling in Browser Clients
--------------------------------------

For the client type `browser` Django's built-in CSRF token handling is active. When implementing
or testing the API this must be handled like this:

1. API responses set a `csrftoken` cookie.
1. Followup requests must be sent value in HTTP header `X-CSRFToken`.

For testing with the [Bruno API Client](https://www.usebruno.com/) the following collection pre-request
script can be used:

```js
let cookieJar = bru.cookies.jar();

let csrfToken = await cookieJar.getCookie(bru.interpolate("{{baseUrl}}"), "csrftoken");
csrfToken = csrfToken?.value || "";
if (csrfToken) console.log("Using Django CSRF Token:", csrfToken);

bru.setVar("csrfToken", csrfToken);
```

On the collection level the HTTP header `X-CSRFToken` must be set to `{{csrfToken}}`.

First a safe method like getting the auth configuration must be executed, which will set the Cookie
in Bruno's cookie jar. Then for each follow-up requrest the script will set the HTTP header.
