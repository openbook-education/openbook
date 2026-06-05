# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db                          import models
from django.utils.translation           import gettext_lazy as _

from openbook.auth.models.mixins.audit  import CreatedModifiedByMixin
from .mixins.file                       import FileUploadMixin
from .mixins.uuid                       import UUIDMixin
from .utils.file                        import calc_file_path

class MediaFile(UUIDMixin, FileUploadMixin, CreatedModifiedByMixin):
    """
    Generic model for media files, when a model can have multiple media files like
    images or sounds that shall later be accessed by their file name. To use this
    model simply add a `GenericRelation` to the model that shall have media files.
    """
    content_type   = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id      = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta(FileUploadMixin.Meta):
        verbose_name        = _("Media File")
        verbose_name_plural = _("Media Files")
        ordering            = ["content_type", "object_id", "file_name"]
        indexes             = [models.Index(fields=["content_type", "object_id", "file_name"])]
    
    def calc_file_path_hook(self, filename):
        return calc_file_path(self.content_type, self.id, filename)