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
from django.utils.translation           import activate
from ..utils                            import content_type

class Utils_Test(TestCase):
    """
    Test cases for utility functions.
    """
    def setUp(self):
        activate("en")  # Set the language to English for testing
        
        self.model_string = "admin.logentry"
        self.content_type = ContentType.objects.get(app_label="admin", model="logentry")

    def test_for_content_type(self):
        """
        Test functions that take a content type object.
        """
        self.assertEqual(content_type.model_string_for_content_type(self.content_type), self.model_string)
        self.assertEqual(content_type.model_string_for_content_type(None), "")

    def test_for_model_string(self):
        """
        Test functions that take a model string.
        """
        self.assertIsInstance(content_type.content_type_for_model_string(self.model_string), ContentType)

        with self.assertRaises(ContentType.DoesNotExist):
            content_type.content_type_for_model_string("admin.invalid_model")
        
        with self.assertRaises(ContentType.DoesNotExist):
            content_type.content_type_for_model_string("invalid_app.logentry")


