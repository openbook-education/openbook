# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.contrib.admin          import RelatedOnlyFieldListFilter
from import_export.fields          import Field

from openbook.admin                import CustomModelAdmin
from openbook.admin                import ImportExportModelResource
from ..models.anonymous_permission import AnonymousPermission
from ..import_export.permission    import PermissionForeignKeyWidget

class AnonymousPermissionResource(ImportExportModelResource):
    permission = Field(attribute="permission", widget=PermissionForeignKeyWidget())

    class Meta:
        model = AnonymousPermission
        fields = ["id", "delete", "permission"]

class AnonymousPermissionAdmin(CustomModelAdmin):
    model              = AnonymousPermission
    resource_classes   = [AnonymousPermissionResource]
    list_display       = ["perm_name", "perm"]
    list_display_links = ["perm_name", "perm"]
    list_filter        = [("permission", RelatedOnlyFieldListFilter)]
    search_fields      = ["permission__codename"]

    fieldsets = [
        (None, {
            "fields": ["permission"]
        }),
    ]
