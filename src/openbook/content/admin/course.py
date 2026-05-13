# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.contrib.admin                  import TabularInline
from django.utils.translation              import gettext_lazy as _
from import_export.fields                  import Field

from openbook.admin                        import CustomModelAdmin
from openbook.admin                        import ImportExportModelResource
from openbook.auth.admin.access_request    import AccessRequestInline
from openbook.auth.admin.enrollment_method import EnrollmentMethodInline
from openbook.auth.admin.mixins.audit      import created_modified_by_fields
from openbook.auth.admin.mixins.audit      import created_modified_by_fieldset
from openbook.auth.admin.mixins.audit      import created_modified_by_related
from openbook.auth.admin.mixins.scope      import permissions_fieldset
from openbook.auth.admin.mixins.scope      import ScopedRolesResourceMixin
from openbook.auth.admin.mixins.scope      import ScopedRolesFormMixin
from openbook.auth.admin.role              import RoleInline
from openbook.auth.admin.role_assignment   import RoleAssignmentInline
from openbook.core.import_export.boolean   import BooleanWidget
from ..models.course                       import Course
from ..models.course_material              import CourseMaterial


class _CourseMaterialInline(TabularInline):
    model            = CourseMaterial
    extra            = 0
    show_change_link = True
    tab              = True
    fields           = ["textbook", "position"]
    ordering         = ["position"]

class CourseResource(ScopedRolesResourceMixin, ImportExportModelResource):
    is_template = Field(attribute="is_template", widget=BooleanWidget())

    class Meta:
        model = Course
        fields = [
            "id", "delete",
            "slug", "name",
            "description", "text_format",
            "group",
            *ScopedRolesResourceMixin.Meta.fields,
            "is_template"
        ]

class CourseForm(ScopedRolesFormMixin):
    class Meta:
        model  = Course
        fields = "__all__"

class CourseAdmin(CustomModelAdmin):
    model               = Course
    form                = CourseForm
    resource_classes    = [CourseResource]
    list_display        = ["name", "slug", "group", "is_template", *created_modified_by_fields]
    list_display_links  = ["name", "slug"]
    list_filter         = ["is_template", "group", *created_modified_by_fields]
    list_select_related = ["group", *created_modified_by_related]
    search_fields       = ["name", "slug", "group__name", "description"]
    ordering            = ["group", "name"]
    readonly_fields     = [*created_modified_by_fields]
    prepopulated_fields = {"slug": ["name"]}
    filter_horizontal   = ["public_permissions",]
    inlines             = [_CourseMaterialInline, RoleInline, RoleAssignmentInline, EnrollmentMethodInline, AccessRequestInline]

    fieldsets = [
        (None, {
            "fields": [("name", "slug"), ("group", "is_template")]
        }),
        (_("Description"), {
            "classes": ["tab"],
            "fields": ["description", "text_format"], # Description, Text Format, AI Notes
        }),
        permissions_fieldset,
        created_modified_by_fieldset,
    ]

    add_fieldsets = [
        (None, {
            "fields": [("name", "slug"), ("group", "is_template")]
        }),
        (_("Description"), {
            "classes": ["tab"],
            "fields": ["description", "text_format"], # Description, Text Format, AI Notes
        }),
        permissions_fieldset,
    ]
