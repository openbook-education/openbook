# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.utils.translation         import gettext_lazy as _
from import_export.fields             import Field
from unfold.admin                     import TabularInline

from openbook.admin                   import CustomModelAdmin
from openbook.admin                   import ImportExportModelResource
from openbook.core.import_export.site import SiteForeignKeyWidget
from ..import_export.group            import GroupManyToManyWidget
from ..models.signup_group_assignment import SecurityAssertion
from ..models.signup_group_assignment import SignupGroupAssignment

class SignupGroupAssignmentResource(ImportExportModelResource):
    site   = Field(attribute="site", widget=SiteForeignKeyWidget())
    groups = Field(attribute="groups", widget=GroupManyToManyWidget())

    class Meta:
        model  = SignupGroupAssignment
        fields = [
            "id", "delete",
            "site", "social_app", "groups",
            "name", "description", "text_format",
            "is_staff", "is_superuser",
        ]

    @classmethod
    def get_display_name(cls):
        return _("Group Assignments")
    
class SecurityAssertionResource(ImportExportModelResource):
    class Meta:
        model  = SecurityAssertion
        fields = [
            "id", "delete",
            "parent", "name", "value", "match_strategy",
        ]
    
    @classmethod
    def get_display_name(cls):
        return _("Checked Security Assertions")

    def filter_export(self, queryset, **kwargs):
        """
        Needed because by default it is not possible to export another model than the one
        from the admin view.
        """
        return self._meta.model.objects.all()

class _SecurityAssertionInline(TabularInline):
    model            = SecurityAssertion
    fields           = ["name", "value", "match_strategy"]
    ordering         = ["name"]
    extra            = 0
    show_change_link = False
    tab              = True

class SignupGroupAssignmentAdmin(CustomModelAdmin):
    model               = SignupGroupAssignment
    resource_classes    = [SignupGroupAssignmentResource, SecurityAssertionResource]
    ordering            = ["name"]
    list_display        = ["name", "site__domain", "site__name", "social_app"]
    list_display_links  = ["name", "site__domain", "site__name", "social_app"]
    list_select_related = ["site", "social_app"]
    search_fields       = [
        "site__domain", "site__name", "site__short_name",
        "social_app__name", "social_app__provider_id", "social_app__client_id",
        "name", "description"
    ]
    filter_horizontal   = ["groups"]
    inlines             = [_SecurityAssertionInline]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("assertions")

    fieldsets = [
        (None, {
            "fields": ["name", "site", "social_app", "is_active"]
        }),
        (_("Description"), {
            "classes": ["tab"],
            "fields": ["description", "text_format"],
        }),
        (_("Groups"), {
            "classes": ["tab"],
            "fields": ["groups"],
        }),
        (_("Global Permissions"), {
            "classes": ["tab"],
            "fields": ["is_staff", "is_superuser"],
        }),
    ]