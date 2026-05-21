# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from import_export.widgets import ForeignKeyWidget
from ..models.auth_config  import AuthConfig

class AuthConfigForeignKeyWidget(ForeignKeyWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(model=AuthConfig, *args, **kwargs)

    def render(self, value, row=None, **kwargs):
        return value.site.domain if value and value.site else ""
    
    def clean(self, value, obj=None, **kwargs):
        return AuthConfig.objects.get(site__domain=value) if value else None