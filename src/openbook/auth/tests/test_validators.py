# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.core.exceptions           import ValidationError
from django.test                      import TestCase

from openbook.core.utils.content_type import content_type_for_model_string
from ..                               import validators

class Validators_Test(TestCase):
    """Test validator functions."""
    def test_validate_scope_type(self):
        """Ensure permission scope models implement ScopedRolesMixin."""
        scope_type_valid   = content_type_for_model_string("openbook_content.course")
        scope_type_invalid = content_type_for_model_string("openbook_auth.user")

        validators.validate_scope_type(scope_type_valid)

        with self.assertRaises(ValidationError):
            validators.validate_scope_type(scope_type_invalid)
