OpenBook Frontend
========================

1. [Directory Content](#directory-content)
1. [Dependency Installation](#dependency-installation)
1. [Adding New Sub-Projects](#adding-new-sub-projects)

Directory Content
-----------------

This is the JavaScript / TypeScript code for the OpenBook Frontend. This is not
the single page app that renders textbooks, but the user interface of server backend.
It is mainly used to pull external libraries from the NPM package index and build a
distribution bundle. The source code is split between two distinct directories:

* `admin`: JS/CSS bundle for the Django Admin
* `website`: JS/CSS bundle for the public website

The admin bundle is used in a few templates that extend the Django Admin. It is separate from
the rest of the website as the Django Admin evolves independently of our public website.

For the single page app, see the [libraries](../../../libraries) directory.

Dependency Installation
-----------------------

Install npm dependencies from the repository root only:

```sh
npm install --legacy-peer-deps
```

Do **not** run `npm install` in `src/frontend`, because this can create
`src/frontend/node_modules` and shadow root workspace dependencies.

If this directory exists, remove it and reinstall from the root:

```sh
npm run fix:frontend-install
```

Adding New Sub-Projects
-----------------------

Simply mirror the structure of one of the existing sub-directories if you need to create
a new sub-project here. Additionally, make sure to add a new entry to the `STATICFILES_DIRS`
variable in the [Django configuration](../openbook/settings.py) so that the build artifacts
or copied into the static directory for Django to pick up.
