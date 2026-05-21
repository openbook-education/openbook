# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.contrib.contenttypes.models    import ContentType
from django.core.files.uploadedfile        import SimpleUploadedFile
from django.test                           import TestCase
from uuid                                  import uuid4

from openbook.auth.middleware.current_user import reset_current_user
from openbook.test                         import ModelViewSetTestMixin
from ..models.media_file                   import MediaFile

class MediaFile_Model_Tests(TestCase):
    """
    Test cases for the `save` method of `MediaFile`.
    """
    def setUp(self):
        reset_current_user()

    def test_save_populates_meta_data_fields(self):
        """
        Should populate the meta-data fields correctly for valid file data.
        """
        # Create a test file
        file_bytes = b"Hello, world!"
        file_data  = SimpleUploadedFile("test.txt", file_bytes)

        # Create an instance of MediaFile
        dummy_model = ContentType.objects.get_for_model(ContentType)
        file_model  = MediaFile(content_type=dummy_model, object_id=uuid4(), file_data=file_data)

        # Call the save method
        file_model.save()

        # Assert that the meta-data fields are populated correctly
        self.assertEqual(file_model.file_name, "test.txt")
        self.assertEqual(file_model.file_size, len(file_bytes))
        self.assertEqual(file_model.mime_type, "text/plain")

        # Clean up
        file_model.delete()

    def test_save_with_none_file_data(self):
        """
        Should not populate the meta-data fields for None file data.
        """
        # Create an instance of MediaFile with None file_data
        dummy_model = ContentType.objects.get_for_model(ContentType)
        file_model  = MediaFile(content_type=dummy_model, object_id=uuid4(), file_data=None)

        # Call the save method
        file_model.save()

        # Assert that the meta-data fields are not populated
        self.assertFalse(file_model.file_name)
        self.assertFalse(file_model.file_size)
        self.assertFalse(file_model.mime_type)

    def test_save_with_empty_file_data(self):
        """
        Should populate the meta-data fields correctly for empty file data.
        """
        # Create an empty file
        file_data = SimpleUploadedFile("empty.txt", b"")

        # Create an instance of MediaFile with empty file_data
        dummy_model = ContentType.objects.get_for_model(ContentType)
        file_model  = MediaFile(content_type=dummy_model, object_id=uuid4(), file_data=file_data)

        # Call the save method
        file_model.save()

        # Assert that the meta-data fields are populated correctly
        self.assertEqual(file_model.file_name, "empty.txt")
        self.assertEqual(file_model.file_size, 0)
        self.assertEqual(file_model.mime_type, "text/plain")

        # Clean up
        file_model.delete()

    def test_save_with_invalid_file_data(self):
        """
        Should raise an error for invalid file data.
        """
        # Create an instance of MediaFile with invalid file_data
        dummy_model = ContentType.objects.get_for_model(ContentType)
        file_model  = MediaFile(content_type=dummy_model, object_id=uuid4(), file_data=" invalid file data ")

        # Call the save method
        with self.assertRaises(FileNotFoundError):
            file_model.save()

class MediaFile_ViewSet_Tests(ModelViewSetTestMixin, TestCase):
    """
    Tests for the `MediaFileViewSet` REST API.
    """
    base_name     = "media_file"
    model         = MediaFile
    search_string = ".txt"
    search_count  = 3
    sort_field    = "file_name"
    
    def setUp(self):
        super().setUp()

        self.dummy_model = ContentType.objects.get_for_model(ContentType)

        file_bytes1 = b"alpha content"
        file_bytes2 = b"beta content"
        file_bytes3 = b"gamma content"

        self.file1 = MediaFile.objects.create(
            content_type = self.dummy_model,
            object_id    = uuid4(),
            file_name    = "alpha.txt",
            file_size    = len(file_bytes1),
            mime_type    = "text/plain",
            file_data    = SimpleUploadedFile("alpha.txt", file_bytes1),
        )

        self.file2 = MediaFile.objects.create(
            content_type = self.dummy_model,
            object_id    = uuid4(),
            file_name    = "beta.txt",
            file_size    = len(file_bytes2),
            mime_type    = "text/plain",
            file_data    = SimpleUploadedFile("beta.txt", file_bytes2),
        )

        self.file3 = MediaFile.objects.create(
            content_type = self.dummy_model,
            object_id    = uuid4(),
            file_name    = "gamma.txt",
            file_size    = len(file_bytes3),
            mime_type    = "text/plain",
            file_data    = SimpleUploadedFile("gamma.txt", file_bytes3),
        )

    def pk_found(self):
        return self.file1.pk

    def get_create_request_data(self):
        file_bytes = b"test content"
        file_data = SimpleUploadedFile("delta.txt", file_bytes)

        return {
            "content_type": self.dummy_model.pk,
            "object_id":    str(uuid4()),
            "file_name":    "delta.txt",
            "file_size":    len(file_bytes),
            "mime_type":    "text/plain",
            "file_data":    file_data,
        }

    def get_update_request_data(self):
        file_bytes = b"test content"
        file_data = SimpleUploadedFile("alpha-renamed.txt", file_bytes)

        return {
            "content_type": self.dummy_model.pk,
            "object_id":    str(self.file1.object_id),
            "file_name":    "alpha-renamed.txt",
            "file_size":    len(file_bytes),
            "mime_type":    "text/plain",
            "file_data":    file_data,
        }

    def get_partial_update_request_data(self):
        return {"object_id": self.file2.object_id}

    operations = {
        "create": {
            "request_data": get_create_request_data,
        },
        "update": {
            "request_data": get_update_request_data,
            "updates":      {"file_name": "alpha-renamed.txt"},
        },
        "partial_update": {
            "request_data": get_partial_update_request_data,
            "updates":      get_partial_update_request_data
        },
    }
