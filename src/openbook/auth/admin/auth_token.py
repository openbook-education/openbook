# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.utils.translation         import gettext_lazy as _
from import_export.fields             import Field

from openbook.admin                   import CustomModelAdmin
from openbook.admin                   import ImportExportModelResource
from ..import_export.user             import UserForeignKeyWidget
from ..models.auth_token              import AuthToken
from .mixins.audit                    import created_modified_by_fields
from .mixins.audit                    import created_modified_by_fieldset
from .mixins.audit                    import created_modified_by_filter
from .mixins.audit                    import created_modified_by_related

class AuthTokenResource(ImportExportModelResource):
    user = Field(attribute="user", widget=UserForeignKeyWidget())

    class Meta:
        model  = AuthToken
        fields = [
            "id", "delete",
            "user", "token",
            "name", "description", "text_format",
            "is_active", "start_date", "end_date",
        ]

class AuthTokenAdmin(CustomModelAdmin):
    model               = AuthToken
    resource_classes    = [AuthTokenResource]
    ordering            = ["user__username", "token"]
    list_display        = ["user__username", "name", "is_active", "start_date", "end_date", *created_modified_by_fields]
    list_display_links  = ["user__username", "name", "is_active", "start_date", "end_date"]
    list_filter         = ["user__username", "is_active", "start_date", "end_date", *created_modified_by_filter]
    list_select_related = ["user", *created_modified_by_related]
    search_fields       = ["user__username", "token", "name", "description"]
    readonly_fields     = ["token", *created_modified_by_fields]

    fieldsets = [
        (None, {
            "fields": ["token", "user", "name"]
        }),
        (_("Validity"), {
            "classes": ["tab"],
            "fields": ["start_date", "end_date", "is_active"]
        }),
        (_("Description"), {
            "classes": ["tab"],
            "fields": ["description", "text_format"],
        }),
        created_modified_by_fieldset,
    ]

    add_fieldsets = [
        (None, {
            "fields": ["user", "name"]
        }),
        (_("Validity"), {
            "classes": ["tab"],
            "fields": ["start_date", "end_date", "is_active"],
        }),
        (_("Description"), {
            "classes": ["tab"],
            "fields": ["description", "text_format"],
        }),
    ]
