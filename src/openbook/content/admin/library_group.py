# OpenBook: Interactive Online Textbooks - Server
# © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.utils.translation              import gettext_lazy as _

from openbook.admin                        import CustomModelAdmin
from openbook.admin                        import ImportExportModelResource
from openbook.auth.admin.access_request    import AccessRequestInline
from openbook.auth.admin.enrollment_method import EnrollmentMethodInline
from openbook.auth.admin.mixins.audit      import created_modified_by_fields
from openbook.auth.admin.mixins.audit      import created_modified_by_fieldset
from openbook.auth.admin.mixins.audit      import created_modified_by_filter
from openbook.auth.admin.mixins.audit      import created_modified_by_related
from openbook.auth.admin.mixins.scope      import permissions_fieldset
from openbook.auth.admin.mixins.scope      import ScopedRolesFormMixin
from openbook.auth.admin.mixins.scope      import ScopedRolesResourceMixin
from openbook.auth.admin.role              import RoleInline
from openbook.auth.admin.role_assignment   import RoleAssignmentInline
from ..models.library_group                import LibraryGroup


class LibraryGroupResource(ScopedRolesResourceMixin, ImportExportModelResource):
    class Meta:
        model  = LibraryGroup
        fields = [
            "id", "delete",
            "slug", "name", "description", "text_format",
            "parent",
            *ScopedRolesResourceMixin.Meta.fields,
        ]


class LibraryGroupForm(ScopedRolesFormMixin):
    class Meta:
        model  = LibraryGroup
        fields = "__all__"


class LibraryGroupAdmin(CustomModelAdmin):
    model               = LibraryGroup
    form                = LibraryGroupForm
    resource_classes    = [LibraryGroupResource]
    list_display        = ["name", "slug", "parent", *created_modified_by_fields]
    list_display_links  = ["name", "slug"]
    list_filter         = ["parent", *created_modified_by_filter]
    list_select_related = ["parent", *created_modified_by_related]
    search_fields       = ["name", "slug", "parent__name"]
    ordering            = ["name"]
    readonly_fields     = [*created_modified_by_fields]
    prepopulated_fields = {"slug": ["name"]}
    filter_horizontal   = ["public_permissions"]
    inlines             = [RoleInline, RoleAssignmentInline, EnrollmentMethodInline, AccessRequestInline]

    fieldsets = [
        (None, {
            "fields": [("name", "slug"), "parent"],
        }),
        (_("Description"), {
            "classes": ["tab"],
            "fields": ["description", "text_format"],
        }),
        permissions_fieldset,
        created_modified_by_fieldset,
    ]

    add_fieldsets = [
        (None, {
            "fields": [("name", "slug"), "parent"],
        }),
        (_("Description"), {
            "classes": ["tab"],
            "fields": ["description", "text_format"],
        }),
        permissions_fieldset,
    ]
