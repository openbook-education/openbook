# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.contrib.auth.models import Permission
from django.test                import TestCase

from openbook.test              import ModelViewSetTestMixin

class Permission_ViewSet_Tests(ModelViewSetTestMixin, TestCase):
    """Test the PermissionViewSet REST API."""
    base_name     = "permission"
    model         = Permission
    search_string = "logentry"
    search_count  = 4
    sort_field    = "codename"

    operations = {
        "list":           {"requires_auth": False},
        "retrieve":       {"requires_auth": False},
        "create":         {"supported": False},
        "update":         {"supported": False},
        "partial_update": {"supported": False},
        "destroy":        {"supported": False},
    }

    def setUp(self):
        super().setUp()
        self.permission = Permission.objects.first()

    def pk_found(self):
        return self.permission.id
