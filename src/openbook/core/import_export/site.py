# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from import_export.widgets import ForeignKeyWidget
from ..models.site         import Site

class SiteForeignKeyWidget(ForeignKeyWidget):
    """
    A customized foreign-key widget that exports and imports sites as domain strings.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(model=Site, *args, **kwargs)

    def render(self, value, row=None, **kwargs):
        return value.domain if value else ""
    
    def clean(self, value, obj=None, **kwargs):
        return Site.objects.get(domain=value) if value else None
