# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.contrib.contenttypes.admin   import GenericTabularInline
from django.utils.translation            import gettext_lazy as _
from import_export.fields                import Field
from unfold.admin                        import TabularInline
from unfold.sections                     import TableSection

from openbook.admin                      import CustomModelAdmin
from openbook.core.import_export.boolean import BooleanWidget
from .mixins.audit                       import created_modified_by_fields
from .mixins.audit                       import created_modified_by_fieldset
from .mixins.audit                       import created_modified_by_filter
from .mixins.audit                       import created_modified_by_related
from .mixins.scope                       import ScopeFormMixin
from .mixins.scope                       import ScopeResourceMixin
from .mixins.scope                       import scope_type_filter
from ..import_export.permission          import PermissionManyToManyWidget
from ..models.access_request             import AccessRequest
from ..models.enrollment_method          import EnrollmentMethod
from ..models.role                       import Role
from ..models.role_assignment            import RoleAssignment
from ..validators                        import validate_permissions

class RoleResource(ScopeResourceMixin):
    is_active   = Field(attribute="is_active",   widget=BooleanWidget())
    permissions = Field(attribute="permissions", widget=PermissionManyToManyWidget())

    class Meta:
        model = Role
        fields = [
            "id", "delete",
            *ScopeResourceMixin.Meta.fields,
            "name", "slug", "priority", "is_active",
            "description", "text_format",
            "permissions",
        ]

class RoleForm(ScopeFormMixin):
    class Meta:
        model  = Role
        fields = "__all__"
    
    class Media:
        css = {
            "all": ScopeFormMixin.Media.css["all"],
        }
        js = ScopeFormMixin.Media.js
    
    def clean(self):
        """
        Check that only allowed permissions are assigned.
        """
        cleaned_data = super().clean()
        scope_type  = cleaned_data["scope_type"]
        permissions = cleaned_data["permissions"]
        
        validate_permissions(scope_type, permissions)
        return cleaned_data

class RoleInline(GenericTabularInline, TabularInline):
    model               = Role
    ct_field            = "scope_type"
    ct_fk_field         = "scope_uuid"
    fields              = ["priority", "name", "slug", "is_active"]
    ordering            = ["priority", "name"]
    readonly_fields     = []
    prepopulated_fields = {"slug": ["name"]}
    extra               = 0
    show_change_link    = True
    tab                 = True

class _EnrollmentMethodInline(TabularInline):
    model               = EnrollmentMethod
    fields              = ["name", "is_active", "passphrase"]
    ordering            = ["name"]
    extra               = 0
    show_change_link    = True
    tab                 = True

class _EnrollmentMethodSection(TableSection):
    verbose_name = _("Enrollment Methods")
    related_name = "enrollment_methods"
    fields       = ["name", "is_active", "passphrase"]

class _AccessRequestInline(TabularInline):
    model               = AccessRequest
    fields              = ["user", "decision", "decision_date"]
    ordering            = ["user"]
    readonly_fields     = ["user", "decision_date"]
    extra               = 0
    show_change_link    = True
    tab                 = True

    def has_add_permission(self, *args, **kwargs):
        return False

class _AccessRequestSection(TableSection):
    verbose_name = _("Access Requests")
    related_name = "access_requests"
    fields       = ["user", "decision", "decision_date"]

class _RoleAssignmentInline(TabularInline):
    model            = RoleAssignment
    fields           = ["user", "is_active", "assignment_method", "enrollment_method", "access_request"]
    ordering         = ["user"]
    readonly_fields  = ["assignment_method", "enrollment_method", "access_request"]
    extra            = 0
    show_change_link = True
    tab              = True

class _RoleAssignmentSection(TableSection):
    verbose_name = _("Role Assignments")
    related_name = "role_assignments"
    fields       = ["user", "is_active", "assignment_method", "enrollment_method", "access_request"]
    
class RoleAdmin(CustomModelAdmin):
    model               = Role
    form                = RoleForm
    resource_classes    = [RoleResource]
    list_display        = ["scope_type", "scope_object", "priority", "name", "slug", "is_active", *created_modified_by_fields]
    list_display_links  = ["scope_type", "scope_object", "priority", "name", "slug"]
    list_filter         = [scope_type_filter, "name", "slug", *created_modified_by_filter]
    list_sections       = [_EnrollmentMethodSection, _AccessRequestSection, _RoleAssignmentSection]
    list_select_related = [*created_modified_by_related]
    ordering            = ["scope_type", "scope_uuid", "priority", "name"]
    search_fields       = ["name", "slug", "description"]
    readonly_fields     = [*created_modified_by_fields]
    prepopulated_fields = {"slug": ["name"]}
    filter_horizontal   = ["permissions"]
    inlines             = [_EnrollmentMethodInline, _AccessRequestInline, _RoleAssignmentInline]

    def get_queryset(self, request):
        """
        Prefetch relations to optimize database performance for the changelist sections.
        """
        return super().get_queryset(request).prefetch_related(
            "enrollment_methods",
            "access_requests",
            "role_assignments",
        )
    
    fieldsets = [
        (None, {
            "fields": [
                ("scope_type", "scope_uuid"),
                ("name", "slug"),
                "priority",
                "is_active"
            ],
        }),
        (_("Description"), {
            "classes": ["tab"],
            "fields": ["description", "text_format"],
        }),
        (_("Permissions"), {
            "classes": ["tab"],
            "fields": ["permissions"],
        }),
        created_modified_by_fieldset,
    ]

    add_fieldsets = [
        (None, {
            "fields": [
                ("scope_type", "scope_uuid"),
                ("name", "slug"),
                "priority",
                "is_active"
            ],
        }),
        (_("Description"), {
            "classes": ["tab"],
            "fields": ["description", "text_format"],
        }),
        (_("Permissions"), {
            "classes": ["tab"],
            "fields": ["permissions"],
        }),
    ]
