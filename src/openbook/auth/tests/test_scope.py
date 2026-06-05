# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.contrib.contenttypes.models import ContentType

from django.test                        import TestCase
from openbook.test                      import ModelViewSetTestMixin

class ScopeType_ViewSet_Tests(ModelViewSetTestMixin, TestCase):
    """Test the ScopeTypeViewSet REST API."""
    base_name = "scope_type"
    model     = ContentType
    count     = -1
    pk_found  = "openbook_content.course"

    operations = {
        "list":           {"model_permission": ()},
        "retrieve":       {"model_permission": ()},
        "create":         {"supported": False},
        "update":         {"supported": False},
        "partial_update": {"supported": False},
        "destroy":        {"supported": False},
    }
