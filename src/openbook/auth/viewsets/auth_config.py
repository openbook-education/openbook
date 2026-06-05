# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from openbook.drf.flex_serializers import FlexFieldsModelSerializer
from ..models.auth_config          import AuthConfig
from ..models.auth_config          import AuthConfigText

class AuthConfigTextSerializer(FlexFieldsModelSerializer):
    __doc__ = "Authorization Setting Texts"

    class Meta:
        model  = AuthConfigText
        fields = ["parent", "language", "logout_next_text"]
        expandable_fields = {}

class AuthConfigSerializer(FlexFieldsModelSerializer):
    __doc__ = "Authorization Settings"

    class Meta:
        model  = AuthConfig
        fields = [
            "site",
            "local_signup_allowed", "signup_email_suffix", "logout_next_url",
            "signup_image", "login_image", "logout_image", "password_reset_image",
        ]
        expandable_fields = {
            "translations": (AuthConfigTextSerializer, {"many": True})
        }