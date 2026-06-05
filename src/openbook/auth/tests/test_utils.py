# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.contrib.auth.models         import Permission
from django.test                        import TestCase
from django.utils.translation           import activate
from ..                                 import utils

class Utils_Test(TestCase):
    """Test utility functions."""
    def setUp(self):
        activate("en")  # Set the language to English for testing

        self.model_string = "admin.logentry"
        self.perm_string  = "admin.view_logentry"
        self.permission   = Permission.objects.get(codename="view_logentry", content_type__app_label="admin")

    def test_for_permission(self):
        """Test functions that take a permission object."""
        # Valid permission object
        self.assertEqual(utils.app_label_for_permission(self.permission),   "admin")
        self.assertEqual(utils.perm_string_for_permission(self.permission), self.perm_string)
        self.assertEqual(utils.model_for_permission(self.permission),       "logentry")
        self.assertEqual(utils.app_name_for_permission(self.permission),    "Administration")
        self.assertEqual(utils.model_name_for_permission(self.permission),  "log entry")
        self.assertEqual(utils.perm_name_for_permission(self.permission),   "Can view log entry")

        # None permission object
        self.assertEqual(utils.app_label_for_permission(None),   "")
        self.assertEqual(utils.perm_string_for_permission(None), "")
        self.assertEqual(utils.model_for_permission(None),       "")
        self.assertEqual(utils.app_name_for_permission(None),    "")
        self.assertEqual(utils.model_name_for_permission(None),  "")
        self.assertEqual(utils.perm_name_for_permission(None),   "")

    def test_for_perm_string(self):
        """Test functions that take a permission string."""
        self.assertIsInstance(utils.permission_for_perm_string(self.perm_string), Permission)

        with self.assertRaises(Permission.DoesNotExist):
            utils.permission_for_perm_string("invalid_app.view_logentry")

        with self.assertRaises(Permission.DoesNotExist):
            utils.permission_for_perm_string("admin.invalid_permission")



