# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.contrib.admin              import RelatedOnlyFieldListFilter
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.translation          import gettext_lazy as _
from import_export.fields              import Field
from unfold.admin                      import TabularInline

from openbook.admin                    import CustomModelAdmin
from .mixins.audit                     import created_modified_by_fields
from .mixins.audit                     import created_modified_by_fieldset
from .mixins.audit                     import created_modified_by_filter
from .mixins.audit                     import created_modified_by_related
from .mixins.scope                     import ScopeFormMixin
from .mixins.scope                     import ScopeResourceMixin
from .mixins.scope                     import ScopeRoleFieldFormMixin
from .mixins.scope                     import ScopeRoleFieldInlineMixin
from .mixins.scope                     import scope_type_filter
from ..import_export.role              import RoleForeignKeyWidget
from ..import_export.user              import UserForeignKeyWidget
from ..models.access_request           import AccessRequest

class AccessRequestResource(ScopeResourceMixin):
    user = Field(attribute="user", widget=UserForeignKeyWidget())
    role = Field(attribute="role", widget=RoleForeignKeyWidget())

    class Meta:
        model = AccessRequest
        fields = [
            "id", "delete",
            *ScopeResourceMixin.Meta.fields,
            "role", "user",
            "duration_value", "duration_period", "end_date",
            "decision",
        ]

class AccessRequestForm(ScopeFormMixin, ScopeRoleFieldFormMixin):
    class Meta:
        model  = AccessRequest
        fields = "__all__"
    
    class Media:
        css = {
            "all": [*ScopeFormMixin.Media.css["all"], *ScopeRoleFieldFormMixin.Media.css["all"]],
        }
        js = [*ScopeFormMixin.Media.js, *ScopeRoleFieldFormMixin.Media.js]

class AccessRequestInline(ScopeRoleFieldInlineMixin, GenericTabularInline, TabularInline):
    model               = AccessRequest
    ct_field            = "scope_type"
    ct_fk_field         = "scope_uuid"
    fields              = ["user", "role", "decision", "decision_date"]
    ordering            = ["user", "role"]
    readonly_fields     = ["user", "role", "decision_date"]
    extra               = 0
    show_change_link    = True
    tab                 = True

    def has_add_permission(self, *args, **kwargs):
        return False

class AccessRequestAdmin(CustomModelAdmin):
    model               = AccessRequest
    form                = AccessRequestForm
    resource_classes    = [AccessRequestResource]
    list_display        = ["scope_type", "scope_object", "role", "user", "decision", "decision_date", *created_modified_by_fields]
    list_display_links  = ["scope_type", "scope_object", "role", "user"]
    list_select_related = ["scope_type", "role", "user", *created_modified_by_related]
    ordering            = ["scope_type", "scope_uuid", "role", "user"]
    search_fields       = ["role__name", "user__username", "user__first_name", "user__last_name"]
    readonly_fields     = ["decision_date", *created_modified_by_fields]

    list_filter = [
        scope_type_filter,
        ("role", RelatedOnlyFieldListFilter),
        ("user", RelatedOnlyFieldListFilter),
        "decision",
        "decision_date",
        *created_modified_by_filter
    ]

    fieldsets = [
        (None, {
            "fields": (
                ("scope_type", "scope_uuid"),
                ("role", "user"),
            ),
        }),
        (_("Validity"), {
            "classes": ("tab",),
            "description": _("Leave empty to request access for an unlimited period."),
            "fields": (
                ("duration_value", "duration_period"),
                "end_date"
            ),
        }),
        (_("Decision"), {
            "classes": ("tab",),
            "fields": (
                ("decision", "decision_date"),
            ),
        }),
        created_modified_by_fieldset,
    ]

    add_fieldsets = [
        (None, {
            "fields": [
                ("scope_type", "scope_uuid"),
                ("role", "user"),
            ],
        }),
        (_("Validity"), {
            "classes": ["tab"],
            "description": _("Leave empty to request access for an unlimited period."),
            "fields": [
                ("duration_value", "duration_period"),
                "end_date"
            ],
        }),
        (_("Decision"), {
            "classes": ["tab"],
            "fields": [
                ("decision", "decision_date"),
            ],
        }),
    ]