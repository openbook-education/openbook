# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.test import TestCase
from django.urls import reverse

class APISchemaTestCase(TestCase):
    def test_get_schema(self):
        """
        Don't crash when downloading the API schema.
        """
        response = self.client.get(reverse("api-schema"))
        self.assertEqual(response.status_code, 200)
