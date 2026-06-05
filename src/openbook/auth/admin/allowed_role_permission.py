# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.contrib.admin              import RelatedOnlyFieldListFilter
from django.forms                      import ModelForm
from import_export.fields              import Field

from openbook.admin                    import CustomModelAdmin
from openbook.admin                    import ImportExportModelResource
from .mixins.scope                     import scope_type_filter
from ..models.allowed_role_permission  import AllowedRolePermission
from ..models.mixins.scope             import ScopedRolesMixin
from ..import_export.permission        import PermissionForeignKeyWidget
from ..import_export.scope             import ScopeTypeForeignKeyWidget
from ..validators                      import validate_scope_type

class AllowedRolePermissionResource(ImportExportModelResource):
    scope_type = Field(attribute="scope_type", widget=ScopeTypeForeignKeyWidget())
    permission = Field(attribute="permission", widget=PermissionForeignKeyWidget())

    class Meta:
        model = AllowedRolePermission
        fields = [
            "id", "delete",
            "scope_type", "permission",
        ]

class AllowedRolePermissionForm(ModelForm):
    class Meta:
        model  = AllowedRolePermission
        fields = "__all__"
    
    def __init__(self, *args, **kwargs):
        """
        Reduce scope type to allowed values.
        """
        super().__init__(*args, **kwargs)

        scope_types = []

        for content_type in ScopedRolesMixin.get_scope_model_content_types():
            scope_types.append((content_type.pk, content_type.name))

        self.fields["scope_type"].choices = scope_types

    def clean(self):
        """
        Check that only allowed scope types are assigned.
        """
        cleaned_data = super().clean()
        scope_type   = cleaned_data["scope_type"]

        validate_scope_type(scope_type)
        return cleaned_data

class AllowedRolePermissionAdmin(CustomModelAdmin):
    model              = AllowedRolePermission
    form               = AllowedRolePermissionForm
    resource_classes   = [AllowedRolePermissionResource]
    list_display       = ["scope_type", "perm_name", "perm"]
    list_display_links = ["scope_type", "perm_name", "perm"]
    list_filter        = [scope_type_filter, ("permission", RelatedOnlyFieldListFilter)]
    search_fields      = ["scope_type", "permission__codename"]

    fieldsets = [
        (None, {
            "fields": [("scope_type", "permission")]
        }),
    ]
