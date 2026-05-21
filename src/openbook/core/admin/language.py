# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from openbook.admin    import CustomModelAdmin
from openbook.admin    import ImportExportModelResource
from ..models.language import Language

class LanguageResource(ImportExportModelResource):
    class Meta:
        model = Language
        import_id_fields = ("language",)
        fields = ("language", "delete", "name")

class LanguageAdmin(CustomModelAdmin):
    model              = Language
    resource_classes   = (LanguageResource,)
    list_display       = ("language", "name")
    list_display_links = ("language", "name")
    search_fields      = ("language", "name")
    fields             = ("language", "name")
