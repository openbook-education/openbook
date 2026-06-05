# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

import importlib, threading

from django.conf                   import settings
from drf_spectacular.extensions    import OpenApiAuthenticationExtension
from rest_framework.authentication import BaseAuthentication

thread_local = threading.local()

def CurrentUserMiddleware(get_response):
    """
    Save the current user in a thread-local variable.

    Do this so it can be accessed within the model layer to auto-populate the
    created_by and modified_by fields of models that use CreatedModifiedByMixin,
    without explicitly passing the user from the view layer to the model layer.
    """
    def middleware(request):
        thread_local.current_user = request.user
        return get_response(request)

    return middleware

class CurrentUserTrackingAuthentication(BaseAuthentication):
    """
    Track the current user for Django REST Framework authentication.

    Django REST Framework wraps the plain Django request object and resolves the
    user only when first accessed. Because of this, the middleware above only
    sees the initial anonymous user.
    """
    def __init__(self):
        """
        Dynamically import classes in the DRF setting _DEFAULT_AUTHENTICATION_CLASSES.

        Use this to re-implement the authentication logic in DRF, since we need
        to override DEFAULT_AUTHENTICATION_CLASSES to hook into it.
        """
        self.auth_classes = []

        for auth_class in settings.REST_FRAMEWORK["_DEFAULT_AUTHENTICATION_CLASSES"]:
            if isinstance(auth_class, str):
                auth_module, _, auth_class_name = auth_class.rpartition('.')
                auth_module = importlib.import_module(auth_module)
                auth_class = getattr(auth_module, auth_class_name)

            self.auth_classes.append(auth_class)

    def authenticate(self, request):
        result = False

        for auth_class in self.auth_classes:
            # Authenticate the same way DRF would do
            auth_obj = auth_class()
            result = auth_obj.authenticate(request)

            # Remember authenticated user
            if result is not None:
                user, _ = result
                thread_local.current_user = user
                break

        return result

def get_current_user():
    """Return the current request user, if any, or None otherwise."""
    return getattr(thread_local, "current_user", None)

def reset_current_user():
    """
    Reset the current user for unit tests.

    Unit tests run in a single thread. Forget the previous test's user, as it
    probably does not even exist anymore.
    """
    thread_local.current_user = None

class CurrentUserTrackingAuthExtension(OpenApiAuthenticationExtension):
    """
    Resolve the OpenApiAuthenticationExtension warning for the custom authenticator.

    As it is defined, we are using session authentication despite our custom
    permission class (which does not affect authentication at all).
    """
    target_class = CurrentUserTrackingAuthentication
    name         = "SessionAuthentication"  # name used in the schema"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in":   "header",
            "name": "sessionId",
        }
