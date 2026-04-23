# OpenBook: Interactive Online Textbooks - Server
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.templatetags.static import static
from django.urls                import reverse_lazy
from django.utils.translation   import gettext_lazy as _
from pathlib                    import Path

# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
#
# SECURITY WARNING: keep the secret key used in production secret!
# SECURITY WARNING: don"t run with debug turned on in production!
SECRET_KEY = "django-insecure-jeo+.}_}9(Q.t_IU$WJ!%eL=b:MDbAL.~NY_=a:>D@:W[XPh4["
DEBUG = True
ALLOWED_HOSTS = ["*"]

OB_ROOT_REDIRECT = "/app/index.html"

# Application definition
#
# NOTE: Sort the apps in the order they should appear in the Admin Dashboard.
# We override the default alphabetical order with the order defined here.
INSTALLED_APPS = [
    # OpenBook Server (order determines order in the Django Admin)
    "openbook.core",
    "openbook.auth",
    "openbook.content",

    # 3rd-party reusable apps
    "daphne",
    "channels",

    # Django REST framework
    #"rest_wind",
    "rest_framework",

    "django_filters",
    "drf_spectacular",
    "drf_spectacular_sidecar",

    # Django Unfold (Modern Admin)
    "unfold.apps.BasicAppConfig",            # before django.contrib.admin
    "unfold.contrib.filters",                # optional, if special filters are needed
    "unfold.contrib.forms",                  # optional, if special form elements are needed
    "unfold.contrib.inlines",                # optional, if special inlines are needed
    "unfold.contrib.import_export",          # optional, if django-import-export package is used
    #"unfold.contrib.guardian",              # optional, if django-guardian package is used
    #"unfold.contrib.simple_history",        # optional, if django-simple-history package is used
    "crispy_forms",                          # Better forms for custom admin views

    # Django built-in apps
    "openbook.apps.OpenBookAdmin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # django-allauth
    "allauth",
    "allauth.account",
    "allauth.headless",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.saml",

    # Other useful apps
    "django_cleanup.apps.CleanupConfig",    # Django Cleanup: Automatically delete files when models are deleted or updated
    "django_extensions",                    # Django Extensions (additional management commands)
    "dbbackup",                             # Django DBBackup: Database and Media Files Backups
    "import_export",                        # Django Import/Export: Import and export data in the Django Admin
    "djangoql",                             # Django QL: Advanced search language for Django
    "colorfield",                           # Django Color Field: Color field for models with color-picker in the admin
]

MIDDLEWARE = [
    # Django
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",

    # django-allauth
    "allauth.account.middleware.AccountMiddleware",

    # OpenBook
    "openbook.auth.middleware.current_user.CurrentUserMiddleware",
    "openbook.core.middleware.current_language.CurrentLanguageMiddleware",
]

ROOT_URLCONF = "openbook.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "openbook.core.context_processors.site",
            ],
        },
    },
]

WSGI_APPLICATION = "openbook.wsgi.application"
ASGI_APPLICATION = "openbook.asgi.application"

FORM_RENDERER = "django.forms.renderers.DjangoTemplates"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django Channels
CHANNEL_LAYERS = {
    "default": {
        #"BACKEND": "channels.layers.InMemoryChannelLayer",
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("localhost", 6379)],
        },
    },
}

# Django REST framework
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "openbook.drf.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,

    "DEFAULT_AUTHENTICATION_CLASSES": [
        # Remember authenticated user (similar to our custom middleware)
        "openbook.auth.middleware.current_user.CurrentUserTrackingAuthentication",
    ],

    "_DEFAULT_AUTHENTICATION_CLASSES": [
        "openbook.drf.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],

    # Serve authenticated users only, checking Django object permissions (with
    # our own permission backend that falls back on regular Django permissions
    # on the user/group if the object-based permission check fails)
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
        "openbook.drf.permissions.DjangoObjectPermissionsOnly",
    ],

    "DEFAULT_FILTER_BACKENDS": (
        "rest_flex_fields2.filter_backends.FlexFieldsFilterBackend",    # (Not possible here due to circular import): drf-flex-fields2: Automatic query optimization
        "django_filters.rest_framework.DjangoFilterBackend",            # Query filters
        "rest_framework.filters.SearchFilter",                          # _search query parameter
        "openbook.drf.filters.DjangoObjectPermissionsFilter",           # Object-permission based filter
        "rest_framework.filters.OrderingFilter",                        # _sort query parameter
    ),

    "SEARCH_PARAM": "_search",
    "ORDERING_PARAM": "_sort",
    "PAGE_PARAM": "_page",
    "PAGE_SIZE_PARAM": "_page_size",
}

# See: https://drf-spectacular.readthedocs.io/
SPECTACULAR_SETTINGS = {
    "TITLE": "OpenBook API",
    "DESCRIPTION": "Beautiful and Engaging Learning Materials",
    "VERSION": "1.0.0",
    "LICENSE": {
        "name": "GNU Affero General Public License, Version 3 (or later)",
        "url": "https://www.gnu.org/licenses/agpl-3.0.html.en",
    },
    "SERVERS": [
        # This surpresses a warnign durign OpenAPI generation. But we need to be careful to
        # manually set the base URL when instantiating the generated API client classes in
        # the frontend.
        {
            "url": f"http://localhost:8000",
            "description": "Local Development"
        }
    ],
    "SERVE_INCLUDE_SCHEMA": False,

    # Self-serve Swagger and Redoc instead of loading from CDN
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",

    "DEBUG": True,

    # Create a custom group in the ReDoc documentation for each app, using the custom
    # tags set on each viewset class. Because otherwise drf-spectacular creates a group
    # for each app using the app label and puts all operations in one large group.
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
        "openbook.drf.viewsets.add_tag_groups",
    ],
}

# See: https://github.com/openbook-education/drf-flex-fields2/blob/master/docs/guide/advanced.rst
# Must be defined before the first import of rest_flex_fields2!
REST_FLEX_FIELDS2 = {
    "EXPAND_PARAM": "_expand",
    "FIELDS_PARAM": "_fields",
    "OMIT_PARAM": "_omit",
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "openbook_auth.User"

AUTHENTICATION_BACKENDS = (
    "openbook.auth.backends.RoleBasedObjectPermissionsBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

# Allauth – Local accounts
# See: https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_ADAPTER = "openbook.auth.allauth.adapter.AccountAdapter"
ACCOUNT_LOGIN_BY_CODE_ENABLED = True
ACCOUNT_LOGIN_BY_CODE_TIMEOUT = 300
ACCOUNT_SIGNUP_FIELDS = ["username*", "email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_USERNAME_BLACKLIST = ["admin", "Administrator", "root", "superuser"]
ACCOUNT_USERNAME_MIN_LENGTH = 5

SOCIALACCOUNT_ADAPTER = "openbook.auth.allauth.adapter.SocialAccountAdapter"

# Allauth - Headless API
# See: https://docs.allauth.org/en/latest/headless/configuration.html
HEADLESS_ONLY = False
HEADLESS_ADAPTER = "allauth.headless.adapter.DefaultHeadlessAdapter"
HEADLESS_SERVE_SPECIFICATION = True
HEADLESS_FRONTEND_URLS = {
    #"account_confirm_email": "https://app.project.org/account/verify-email/{key}",
    #"account_reset_password": "https://app.project.org/account/password/reset",
    #"account_reset_password_from_key": "https://app.project.org/account/password/reset/key/{key}",
    #"account_signup": "https://app.project.org/account/signup",
    #"socialaccount_login_error": "https://app.project.org/account/provider/callback",
}

# Recommended settings for SAML behind a reverse proxy
# See: https://django-allauth.readthedocs.io/en/latest/socialaccount/providers/saml.html#guidelines
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Django Unfold Admin
CRISPY_TEMPLATE_PACK = "unfold_crispy"
CRISPY_ALLOWED_TEMPLATE_PACKS = ["unfold_crispy"]

UNFOLD = {
    "SITE_TITLE":  _("OpenBook: Admin"),
    "SITE_HEADER": _("OpenBook: Admin"),
    "STYLES": [
        lambda request: static("openbook/admin/bundle.css"),
    ],
    "SCRIPTS": [
        lambda request: static("openbook/admin/bundle.js"),
    ],

    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "128x128",
            "type": "image/vnd",
            "href": lambda request: static("favicon.ico"),
        },
    ],

    "SIDEBAR": {
        "show_search": True,
    },

    # Icons: https://fonts.google.com/icons
    "SITE_DROPDOWN": [
        {
            "icon": "settings",
            "title": _("Administration"),
            "link": reverse_lazy("admin:index"),
        },
        {
            "icon": "home",
            "title": _("Website"),
            "link": "/",
        },
        {
            "icon": "api",
            "title": _("API Explorer"),
            "link": reverse_lazy("api-root"),
        },
        {
            "icon": "menu_book",
            "title": _("Documentation"),
            "link": "https://github.com/DennisSchulmeister/openbook/blob/main/README.md",
        },
        {
            "icon": "code",
            "title": _("GitHub"),
            "link": "https://github.com/DennisSchulmeister/openbook/",
        },
    ],

    # Changelist tabs to clean-up the menu structure
    # See: https://unfoldadmin.com/docs/tabs/changelist/
    #
    # Note: In openbook.admin.CustomAdminSite we have a custom logic that hides all models
    # from the menu structure, that are listed as the non-first tab here, to tidy up the menus.
    "TABS": [
        {
            "ob_group_name": _("HTML Libraries"),
            "models": [
                "openbook_core.htmllibrary",
                "openbook_core.htmlcomponent",
            ],
            "items": [
                {
                    "title":      _("HTML Libraries"),
                    "link":       reverse_lazy("admin:openbook_core_htmllibrary_changelist"),
                    "permission": lambda req: req.user.has_perm("openbook_core.view_htmllibrary"),
                },
                {
                    "title":      _("HTML Components"),
                    "link":       reverse_lazy("admin:openbook_core_htmlcomponent_changelist"),
                    "permission": lambda req: req.user.has_perm("openbook_core.view_htmlcomponent"),
                },

                # TODO: Repository Servers (Model)
                # TODO: Install Libraries (Custom View)
                # TODO: Upgrade Libraries (Custom View)
                # See: https://unfoldadmin.com/docs/configuration/crispy-forms/
            ],
        },
        {
            "ob_group_name": _("Authentication Methods"),
            "models": [
                "openbook_auth.authconfig",
                "socialaccount.socialapp",
                "openbook_auth.signupgroupassignment",
                "socialaccount.socialtoken",
            ],
            "items": [
                {
                    "title":      _("Authentication Settings"),
                    "link":       reverse_lazy("admin:openbook_auth_authconfig_changelist"),
                    "permission": lambda req: req.user.has_perm("openbook_auth.view_authconfig"),
                },
                {
                    "title":      _("Social Applications"),
                    "link":       reverse_lazy("admin:socialaccount_socialapp_changelist"),
                    "permission": lambda req: req.user.has_perm("socialaccount.view_socialapp"),
                },
                {
                    "title":      _("Group Assignment on Sign-Up"),
                    "link":       reverse_lazy("admin:openbook_auth_signupgroupassignment_changelist"),
                    "permission": lambda req: req.user.has_perm("openbook_auth.view_signupgroupassignment"),
                },
                {
                    "title":      _("Social Application Tokens"),
                    "link":       reverse_lazy("admin:socialaccount_socialtoken_changelist"),
                    "permission": lambda req: req.user.has_perm("socialaccount.view_socialtoken"),
                },
            ],
        },
        {
            "ob_group_name": _("Users and Groups"),
            "models": [
                "openbook_auth.user",
                "openbook_auth.group",
                "account.emailaddress",
                "socialaccount.socialaccount",
                "openbook_auth.authtoken",
            ],
            "items": [
                {
                    "title":      _("Users"),
                    "link":       reverse_lazy("admin:openbook_auth_user_changelist"),
                    "permission": lambda req: req.user.has_perm("openbook_auth.view_user"),
                },
                {
                    "title":      _("User Groups"),
                    "link":       reverse_lazy("admin:openbook_auth_group_changelist"),
                    "permission": lambda req: req.user.has_perm("openbook_auth.view_group"),
                },
                {
                    "title":      _("E-Mail Addresses"),
                    "link":       reverse_lazy("admin:account_emailaddress_changelist"),
                    "permission": lambda req: req.user.has_perm("account.view_emailaddress"),
                },
                {
                    "title":      _("Social Accounts"),
                    "link":       reverse_lazy("admin:socialaccount_socialaccount_changelist"),
                    "permission": lambda req: req.user.has_perm("socialaccount.view_socialaccount"),
                },
                {
                    "title":      _("Authentication Tokens"),
                    "link":       reverse_lazy("admin:openbook_auth_authtoken_changelist"),
                    "permission": lambda req: req.user.has_perm("openbook_auth.authtoken_token"),
                },
            ],
        },
        {
            "ob_group_name": _("Permissions"),
            "models": [
                "openbook_auth.permissiontext",
                "openbook_auth.anonymouspermission",
                "openbook_auth.allowedrolepermission",
            ],
            "items": [
                {
                    "title":      _("Translated Permissions"),
                    "link":       reverse_lazy("admin:openbook_auth_permissiontext_changelist"),
                    "permission": lambda req: req.user.has_perm("openbook_auth.view_permissiontext"),
                },
                {
                    "title":      _("Anonymous Permissions"),
                    "link":       reverse_lazy("admin:openbook_auth_anonymouspermission_changelist"),
                    "permission": lambda req: req.user.has_perm("openbook_auth.view_anonymouspermission"),
                },
                {
                    "title":      _("Allowed Role Permissions"),
                    "link":       reverse_lazy("admin:openbook_auth_allowedrolepermission_changelist"),
                    "permission": lambda req: req.user.has_perm("openbook_auth.view_allowedrolepermission"),
                },
            ],
        },
        {
            "ob_group_name": _("Scopes and Roles"),
            "models": [
                "openbook_auth.role",
                "openbook_auth.enrollmentmethod",
                "openbook_auth.accessrequest",
                "openbook_auth.roleassignment",
            ],
            "items": [
                {
                    "title":      _("Roles"),
                    "link":       reverse_lazy("admin:openbook_auth_role_changelist"),
                    "permission": lambda req: req.user.has_perm("openbook_auth.view_role"),
                },
                {
                    "title":      _("Enrollment Methods"),
                    "link":       reverse_lazy("admin:openbook_auth_enrollmentmethod_changelist"),
                    "permission": lambda req: req.user.has_perm("openbook_auth.view_enrollmentmethod"),
                },
                {
                    "title":      _("Access Requests"),
                    "link":       reverse_lazy("admin:openbook_auth_accessrequest_changelist"),
                    "permission": lambda req: req.user.has_perm("openbook_auth.view_accessrequest"),
                },
                {
                    "title":      _("Role Assignments"),
                    "link":       reverse_lazy("admin:openbook_auth_roleassignment_changelist"),
                    "permission": lambda req: req.user.has_perm("openbook_auth.view_roleassignment"),
                },
            ],
        }
    ]
}

# Interlal IPs (required by Django Debug Toolbar)
INTERNAL_IPS = ["127.0.0.1"]

# E-Mail Settings
# See: https://docs.djangoproject.com/en/5.0/ref/settings/#std-setting-EMAIL_BACKEND
# The values below assume you started maildev with "npm start" at the root directory.
DEFAULT_FROM_EMAIL   = "noreply@example.com"
EMAIL_SUBJECT_PREFIX = "[OpenBook] "

#EMAIL_BACKEND        = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST          = "localhost"
EMAIL_PORT          = 1025
# EMAIL_HOST_USER     = ""
# EMAIL_HOST_PASSWORD = ""
# EMAIL_TIMEOUT       = 30

# Website information
SITE_ID = 1
LOGIN_REDIRECT_URL = "/"

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/
USE_TZ = True
TIME_ZONE = "UTC"

LANGUAGE_CODE = "en-us"
USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "_static"

STATICFILES_DIRS = [
    BASE_DIR / "frontend" / "admin" / "dist",
    BASE_DIR / "frontend" / "allauth" / "dist",
    BASE_DIR / "frontend" / "app" / "dist",
]

# Uploaded media files
# https://docs.djangoproject.com/en/5.0/topics/files/
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "_media"

# Database and media files backups
DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
DBBACKUP_STORAGE_OPTIONS = {"location": BASE_DIR / "_backup"}

# Import deployment-specific local settings which can override single values here
try:
    EXTRA_INSTALLED_APPS = []

    from .local_settings import *

    INSTALLED_APPS = [*INSTALLED_APPS, *EXTRA_INSTALLED_APPS]
except ImportError:
    pass
