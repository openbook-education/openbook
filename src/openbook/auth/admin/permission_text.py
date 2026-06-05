# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.utils.translation           import gettext_lazy as _
from import_export.fields               import Field
from import_export.widgets              import ForeignKeyWidget

from openbook.admin                     import CustomModelAdmin
from openbook.admin                     import ImportExportModelResource
from openbook.core.models.language      import Language
from ..import_export.permission         import PermissionForeignKeyWidget
from ..models.permission_text           import PermissionText

class PermissionTextResource(ImportExportModelResource):
    parent   = Field(attribute="parent",   widget=PermissionForeignKeyWidget())
    language = Field(attribute="language", widget=ForeignKeyWidget(model=Language, field="language"))

    class Meta:
        model  = PermissionText
        fields = ["id", "delete", "parent", "language", "name"]

class PermissionTextAdmin(CustomModelAdmin):
    model              = PermissionText
    resource_classes   = [PermissionTextResource]
    list_display       = ["appname", "perm_name", "perm", "language", "name"]
    list_display_links = ["appname", "perm_name", "perm", "language"]
    list_editable      = ["name"]
    search_fields      = ["appname", "perm_name", "perm", "language", "name"]
    readonly_fields    = ["appname", "perm_name", "perm"]

    fieldsets = [
        (None, {
            "fields": ["perm", ("appname", "perm_name"), ("language", "name")]
        }),
    ]

    add_fieldsets = [
        (None, {
            "fields": ["parent", ("language", "name")]
        }),
    ]