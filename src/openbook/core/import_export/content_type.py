# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.contrib.contenttypes.models import ContentType
from import_export.widgets              import ForeignKeyWidget

from ..utils.content_type               import content_type_for_model_string
from ..utils.content_type               import model_string_for_content_type

class ContentTypeForeignKeyWidget(ForeignKeyWidget):
    """
    A customized foreign-key widget that exports and imports content types as model strings.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(model=ContentType, *args, **kwargs)

    def render(self, value, row=None, **kwargs):
        return model_string_for_content_type(value)
    
    def clean(self, value, obj=None, **kwargs):
        return content_type_for_model_string(value)
