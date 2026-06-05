# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.apps               import AppConfig
from django.utils.translation  import gettext_lazy as _

class OpenBookServerApp(AppConfig):
    name         = "openbook.core"
    label        = "openbook_core"
    verbose_name = _("OpenBook Server")

    def ready(self):
        """
        Patch `ContentType.__str__` to return the model only, without prefixing it
        with the app name.
        """
        def content_type_str(self):
            return self.name

        from django.contrib.contenttypes.models import ContentType
        ContentType.__str__ = content_type_str