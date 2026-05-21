# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.contrib             import admin
from django.contrib.auth.admin  import GroupAdmin as DjangoGroupAdmin
from django.utils.translation   import gettext_lazy as _
from import_export.fields       import Field
from unfold.admin               import TabularInline
from unfold.widgets             import UnfoldBooleanSwitchWidget

from openbook.admin             import CustomModelAdmin
from openbook.admin             import ImportExportModelResource
from ..models.group             import Group
from ..import_export.permission import PermissionManyToManyWidget

class GroupResource(ImportExportModelResource):
    permissions = Field(attribute="permissions", widget=PermissionManyToManyWidget())

    class Meta:
        model = Group
        import_id_fields = ["slug"]
        fields = ["slug", "delete", "name", "permissions"]

class _UserInline(TabularInline):
    model               = Group.user_set.through
    fk_name             = "group"
    verbose_name        = _("User")
    verbose_name_plural = _("Users")
    fields              = ["get_username", "get_full_name", "get_user_type", "get_is_staff", "get_is_superuser"]
    readonly_fields     = fields
    extra               = 0
    show_change_link    = False
    tab                 = True

    def has_add_permission(self, *args, **kwargs):
        return False

    @admin.display(description=_("Username"))
    def get_username(self, obj):
        return obj.user.username

    @admin.display(description=_("Full Name"))
    def get_full_name(self, obj):
        return obj.user.get_full_name()

    @admin.display(description=_("User Type"))
    def get_user_type(self, obj):
        return obj.user.user_type

    @admin.display(description=_("Is Staff"))
    def get_is_staff(self, obj):
        widget = UnfoldBooleanSwitchWidget(attrs={"disabled": True})
        return widget.render("is_staff", obj.user.is_staff)

    @admin.display(description=_("Is Superuser"))
    def get_is_superuser(self, obj):
        widget = UnfoldBooleanSwitchWidget(attrs={"disabled": True})
        return widget.render("is_staff", obj.user.is_superuser)

class GroupAdmin(DjangoGroupAdmin, CustomModelAdmin):
    """
    Allow importing and exporting groups in Django's Group admin.
    """
    resource_classes    = [GroupResource]
    list_display        = ["name", "slug", "user_count"]
    list_display_links  = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}
    inlines             = [_UserInline]

    fieldsets = [
        (None, {
            "fields": [
                ("name", "slug"),
                "permissions"
            ],
        }),
    ]
