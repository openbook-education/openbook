# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from import_export.widgets import ForeignKeyWidget
from ..models.html_library import HTMLLibrary
from ..models.html_library import HTMLLibraryVersion

class HTMLLibraryForeignKeyWidget(ForeignKeyWidget):
    """
    A customized foreign-key widget that exports and imports HTML libraries as
    npm-style strings: `@organization/library`-
    """
    def __init__(self, *args, **kwargs):
        super().__init__(model=HTMLLibrary, *args, **kwargs)

    def render(self, value, row=None, **kwargs):
        return value.fqn() if value else ""
    
    def clean(self, value, obj=None, **kwargs):
        return HTMLLibrary.get_by_fqn(value) if value else None

class HTMLLibraryVersionForeignKeyWidget(ForeignKeyWidget):
    """
    A customized foreign-key widget that exports and imports HTML library versions as
    npm-style strings: `@organization/library 1.0.0`-
    """
    def __init__(self, *args, **kwargs):
        super().__init__(model=HTMLLibraryVersion, *args, **kwargs)

    def render(self, value, row=None, **kwargs):
        return value.fqn() if value else ""
    
    def clean(self, value, obj=None, **kwargs):
        return HTMLLibraryVersion.get_by_fqn(value) if value else None