# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import mimetypes

from django.db                import models
from django.utils.translation import gettext_lazy as _

class FileUploadMixin(models.Model):
    """
    Abstract base class for the generic file upload models below. Contains the common
    fields for the file data and meta data, which are populated when the model is saved.
    """
    def calc_file_path_hook(self, filename):
        """
        To be overridden by implementing class.
        """
        return filename
    
    def _calc_file_path(self, filename):
        return self.calc_file_path_hook(filename)

    file_data = models.FileField(verbose_name=_("File Data"), upload_to=_calc_file_path, null=False, blank=True)
    file_name = models.CharField(verbose_name=_("File Name"), max_length=255, blank=True)
    file_size = models.PositiveIntegerField(verbose_name=_("File Size"), null=True, blank=True)
    mime_type = models.CharField(verbose_name=_("MIME Type"), max_length=64, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.file_name

    def save(self, *args, **kwargs):
        """
        Populate meta-data fields when file is saved.
        """
        if self.file_data:
            self.file_name = self.file_data.name
            self.file_size = self.file_data.size
            self.mime_type, _ = mimetypes.guess_type(self.file_data.name)

            if not self.mime_type:
                self.mime_type = 'application/octet-stream'

        super().save(*args, **kwargs)
