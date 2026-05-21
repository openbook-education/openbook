# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.utils.translation        import gettext_lazy as _
from rest_framework.authentication   import BaseAuthentication
from rest_framework.authentication   import get_authorization_header
from rest_framework.exceptions       import AuthenticationFailed

from openbook.auth.models.auth_token import AuthToken

class TokenAuthentication(BaseAuthentication):
    """
    Token authentication for app users. Works hand in hand with the `AuthToken` model
    in the `openbook_auth` app. Based on the class `TokenAuthentication` in DRF.
    """
    keyword = "Token"

    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of `(user, token)` or `None`.
        """
        # Extract token from HTTP Authorization header
        authorization_header = get_authorization_header(request).split()

        if not authorization_header or authorization_header[0].lower() != self.keyword.lower().encode():
            return None

        if len(authorization_header) != 2:
            raise AuthenticationFailed(_("Invalid Authorization header received."))

        try:
            token = authorization_header[1].decode()
        except UnicodeError:
            raise AuthenticationFailed(_("Invalid token received."))

        # Authenticate with the token
        try:
            auth_token = AuthToken.objects.get(token=token)
        except AuthToken.DoesNotExist:
            raise AuthenticationFailed(_("Invalid token received."))

        if not auth_token.user.is_active:
            raise AuthenticationFailed(_("User is inactive or deleted."))

        return (auth_token.user, auth_token)

    def authenticate_header(self, request):
        """
        Return string to be used as the value of the `WWW-Authenticate` header in a
        `401 Unauthenticated` response.
        """
        return self.keyword
