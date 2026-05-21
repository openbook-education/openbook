# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.core.exceptions         import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test                    import TestCase
from io                             import BytesIO
from PIL                            import Image
from ..                             import validators

class ValidateImage_Tests(TestCase):
    """
    Test cases for the `ValidateImage` validator class.
    """
    def setUp(self):
        image_object = Image.new('RGB', (100, 100), (255, 255, 255))
        image_bytes  = BytesIO()
        image_object.save(image_bytes, format="JPEG")

        self.validator     = validators.ValidateImage()
        self.valid_image   = SimpleUploadedFile("test.jpg", image_bytes.getvalue())
        self.invalid_image = SimpleUploadedFile("test.txt", b"not an image")

    def test_validate_image_valid(self):
        """
        Valid image should pass validation.
        """
        self.validator(self.valid_image)

    def test_validate_image_invalid(self):
        """
        Invalid image should fail validation.
        """
        with self.assertRaises(ValidationError):
            self.validator(self.invalid_image)

    def test_validate_image_too_large(self):
        """
        Too large image should fail validation.
        """
        validator = validators.ValidateImage(max_size=10)

        with self.assertRaises(ValidationError):
            validator(self.valid_image)

class ValidateLibrary_Tests(TestCase):
    """
    Test cases for validator functions.
    """
    
    def test_validate_library_fqn(self):
        validators.validate_library_fqn("@test/test")
        
        with self.assertRaises(ValidationError):
            validators.validate_library_fqn("a")
        with self.assertRaises(ValidationError):
            validators.validate_library_fqn("a#b")
        with self.assertRaises(ValidationError):
            validators.validate_library_fqn("@a")
        with self.assertRaises(ValidationError):
            validators.validate_library_fqn("@a$b")
        with self.assertRaises(ValidationError):
            validators.validate_library_fqn("@a/b")
        with self.assertRaises(ValidationError):
            validators.validate_library_fqn("@a/b!c")
        with self.assertRaises(ValidationError):
            validators.validate_library_fqn("@a/b.c-xyz")

    def test_split_library_fqn(self):
        (organization, name) = validators.split_library_fqn("@organization/name")

        self.assertEqual(organization, "organization")
        self.assertEqual(name, "name")

        with self.assertRaises(ValidationError):
            validators.split_library_fqn("@organization#name")
        
    def test_validate_library_version_fqn(self):
        validators.validate_library_version_fqn("@test/test 1.0.0-pre1")

        with self.assertRaises(ValidationError):
            validators.validate_library_version_fqn("test/test 1.0.0-pre1")
        
        with self.assertRaises(ValidationError):
            validators.validate_library_version_fqn("@test/test1.0.0-pre1")

        with self.assertRaises(ValidationError):
            validators.validate_library_version_fqn("@test/test")

        with self.assertRaises(ValidationError):
            validators.validate_library_version_fqn("1.0.0-pre1")

    def test_split_library_version_fqn(self):
        (organization, name, version) = validators.split_library_version_fqn("@organization/name 1.0.0-pre1")

        self.assertEqual(organization, "organization")
        self.assertEqual(name, "name")
        self.assertEqual(version, "1.0.0-pre1")

        with self.assertRaises(ValidationError):
            validators.split_library_version_fqn("@organization/name#1.0.0-pre1")

    def test_validate_version_number(self):
        validators.validate_version_number("1.2.3")
        validators.validate_version_number("1.2.3-beta")
        validators.validate_version_number("1.2.3+build")
        validators.validate_version_number("1.2.3-beta+build")
        
        with self.assertRaises(ValidationError):
            validators.validate_version_number("a")

    def test_validate_version_expression(self):
        validators.validate_version_expression("1.2.3")
        validators.validate_version_expression("<1.2.3")
        validators.validate_version_expression(">1.2.3")
        validators.validate_version_expression("<=1.2.3")
        validators.validate_version_expression(">=1.2.3")
        validators.validate_version_expression("!=1.2.3")
        validators.validate_version_expression("!=1.2.3")

        with self.assertRaises(ValidationError):
            validators.validate_version_expression("@")
        
        with self.assertRaises(ValidationError):
            validators.validate_version_expression("+1.2.3")
        
        with self.assertRaises(ValidationError):
            validators.validate_version_expression("1,2,3")
        
        with self.assertRaises(ValidationError):
            validators.validate_version_expression("#test")