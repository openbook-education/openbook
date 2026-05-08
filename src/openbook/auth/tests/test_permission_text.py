# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.contrib.auth.models    import Permission
from django.test                   import TestCase
from django.urls                   import reverse

from openbook.core.models.language import Language
from openbook.test                 import ModelViewSetTestMixin
from ..middleware.current_user     import reset_current_user
from ..models.permission_text      import PermissionText

class PermissionText_ViewSet_Tests(ModelViewSetTestMixin, TestCase):
    """Test the PermissionTextViewSet REST API."""
    base_name         = "permission_text"
    model             = PermissionText
    search_string     = "Permission"
    search_count      = 1
    sort_field        = "name"
    expandable_fields = ["parent"]

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
        reset_current_user()

        permission    = Permission.objects.first()
        language_en   = Language.objects.create(language="en", name="English")
        language_de   = Language.objects.create(language="de", name="Deutsch")

        self.translated_en = PermissionText.objects.create(
            parent  = permission,
            language= language_en,
            name    = "Test Permission Name",
        )

        PermissionText.objects.create(
            parent  = permission,
            language= language_de,
            name    = "Test Berechtigung",
        )

        self.url_list   = reverse("permission-list")
        self.url_detail = reverse("permission-detail", args=[self.translated_en.id])

    def pk_found(self):
        return self.translated_en.id
