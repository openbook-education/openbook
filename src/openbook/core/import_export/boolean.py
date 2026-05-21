# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from import_export.widgets import BooleanWidget as IEBooleanWidget

class BooleanWidget(IEBooleanWidget):
    """
    A customized boolean widget that renders its value as "true" and "false"
    instead of zero and one.
    """
    def render(self, value, row=None, **kwargs):
        return "true" if value else "false"
    
    def clean(self, value, obj=None, **kwargs):
        return str(value).upper() in ["1", "X", "YES", "TRUE"]