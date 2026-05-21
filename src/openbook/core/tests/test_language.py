# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.test       import TestCase

from openbook.test     import ModelViewSetTestMixin
from ..models.language import Language

class Language_ViewSet_Tests(ModelViewSetTestMixin, TestCase):
    """
    Tests for the `LanguageViewSet` REST API.
    """
    base_name     = "language"
    model         = Language
    pk_found      = "en"
    search_string = "deu"
    search_count  = 1
    sort_field    = "name"

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

        Language.objects.create(language="en", name="English")
        Language.objects.create(language="de", name="Deutsch")
        Language.objects.create(language="fr", name="Français")
