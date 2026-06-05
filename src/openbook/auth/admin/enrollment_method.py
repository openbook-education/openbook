# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.contrib.admin                import RelatedOnlyFieldListFilter
from django.contrib.contenttypes.admin   import GenericTabularInline
from django.utils.translation            import gettext_lazy as _
from import_export.fields                import Field
from unfold.admin                        import TabularInline

from openbook.admin                      import CustomModelAdmin
from openbook.core.import_export.boolean import BooleanWidget
from .mixins.audit                       import created_modified_by_fields
from .mixins.audit                       import created_modified_by_fieldset
from .mixins.audit                       import created_modified_by_filter
from .mixins.audit                       import created_modified_by_related
from .mixins.scope                       import ScopeFormMixin
from .mixins.scope                       import ScopeResourceMixin
from .mixins.scope                       import ScopeRoleFieldFormMixin
from .mixins.scope                       import ScopeRoleFieldInlineMixin
from .mixins.scope                       import scope_type_filter
from ..import_export.role                import RoleForeignKeyWidget
from ..models.enrollment_method          import EnrollmentMethod

class EnrollmentMethodResource(ScopeResourceMixin):
    role      = Field(attribute="role",      widget=RoleForeignKeyWidget())
    is_active = Field(attribute="is_active", widget=BooleanWidget())

    class Meta:
        model = EnrollmentMethod
        fields = [
            "id", "delete",
            *ScopeResourceMixin.Meta.fields,
            "name", "role", "passphrase", "is_active",
            "duration_value", "duration_period", "end_date",
            "description", "text_format",
        ]

class EnrollmentMethodForm(ScopeFormMixin, ScopeRoleFieldFormMixin):
    class Meta:
        model  = EnrollmentMethod
        fields = "__all__"
    
    class Media:
        css = {
            "all": [*ScopeFormMixin.Media.css["all"], *ScopeRoleFieldFormMixin.Media.css["all"]],
        }
        js = [*ScopeFormMixin.Media.js, *ScopeRoleFieldFormMixin.Media.js]

class EnrollmentMethodInline(ScopeRoleFieldInlineMixin, GenericTabularInline, TabularInline):
    model               = EnrollmentMethod
    ct_field            = "scope_type"
    ct_fk_field         = "scope_uuid"
    fields              = ["name", "role", "is_active", "passphrase"]
    ordering            = ["name", "role"]
    extra               = 0
    show_change_link    = True
    tab                 = True

class EnrollmentMethodAdmin(CustomModelAdmin):
    model               = EnrollmentMethod
    form                = EnrollmentMethodForm
    resource_classes    = [EnrollmentMethodResource]
    list_display        = ["scope_type", "scope_object", "name", "role", "passphrase", "is_active", *created_modified_by_fields]
    list_display_links  = ["scope_type", "scope_object", "name", "role"]
    list_select_related = [*created_modified_by_related]
    ordering            = ["scope_type", "scope_uuid", "name", "role"]
    search_fields       = ["name", "role__name", "user__username"]
    readonly_fields     = [*created_modified_by_fields]

    list_filter = [
        scope_type_filter,
        ("role", RelatedOnlyFieldListFilter),
        "end_date",
        "is_active",
        *created_modified_by_filter
    ]

    fieldsets = [
        (None, {
            "fields": [
                ("scope_type", "scope_uuid"),
                ("name", "role"),
                ("passphrase", "is_active"),
            ],
        }),
        (_("Description"), {
            "classes": ["tab"],
            "fields": ["description", "text_format"],
        }),
        (_("Validity"), {
            "classes": ["tab"],
            "description": _("Leave empty to make the enrollment valid for an unlimited period. Otherwise either set a duration or an end date."),
            "fields": [
                ("duration_value", "duration_period"),
                "end_date"
            ],
        }),
        created_modified_by_fieldset,
    ]

    add_fieldsets = [
        (None, {
            "fields": [
                ("scope_type", "scope_uuid"),
                ("name", "role"),
                ("passphrase", "is_active"),
            ],
        }),
        (_("Description"), {
            "classes": ["tab"],
            "fields": ["description", "text_format"],
        }),
        (_("Validity"), {
            "classes": ["tab"],
            "description": _("Leave empty to make the enrollment valid for an unlimited period. Otherwise either set a duration or an end date."),
            "fields": [
                ("duration_value", "duration_period"),
                "end_date"
            ],
        }),
    ]
