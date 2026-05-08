# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from drf_spectacular.utils      import extend_schema_field
from rest_framework.serializers import SlugRelatedField

from ..models.user              import User

@extend_schema_field(str)
class UserField(SlugRelatedField):
    """Use usernames instead of raw primary keys for input and output."""
    def __init__(self, **kwargs):
        super().__init__(slug_field="username", **kwargs)

    def get_queryset(self):
        if not self.read_only:
            return User.objects.all()
