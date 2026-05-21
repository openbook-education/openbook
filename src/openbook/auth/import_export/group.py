# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from import_export.widgets import ForeignKeyWidget
from import_export.widgets import ManyToManyWidget
from ..models.group        import Group

class GroupForeignKeyWidget(ForeignKeyWidget):
    """Export and import groups by their slug in foreign-key fields."""
    def __init__(self, *args, **kwargs):
        super().__init__(model=Group, field="slug", *args, **kwargs)

class GroupManyToManyWidget(ManyToManyWidget):
    """Export and import groups by their slug in many-to-many fields."""
    def __init__(self, *args, **kwargs):
        super().__init__(model=Group, field="slug", *args, **kwargs)
