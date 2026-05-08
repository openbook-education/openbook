# OpenBook: Interactive Online Textbooks - Server
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from allauth.account.models              import EmailAddress
from django.contrib.auth.admin           import UserAdmin as DjangoUserAdmin
from django.utils.translation            import gettext_lazy as _
from import_export.fields                import Field
from import_export.widgets               import ManyToManyWidget
from unfold.admin                        import TabularInline
from unfold.forms                        import AdminPasswordChangeForm
from unfold.forms                        import UserChangeForm
from unfold.forms                        import UserCreationForm
from unfold.sections                     import TableSection

from openbook.admin                      import CustomModelAdmin
from openbook.admin                      import ImportExportModelResource
from openbook.core.import_export.boolean import BooleanWidget
from ..models.auth_token                 import AuthToken
from ..models.group                      import Group
from ..models.user                       import User
from ..import_export.permission          import PermissionManyToManyWidget
from .mixins.audit                       import created_modified_by_fields

class _GroupSection(TableSection):
    verbose_name = _("User Groups")
    related_name = "groups"
    fields       = ["name", "slug"]

class _PermissionSection(TableSection):
    verbose_name = _("User Permissions")
    related_name = "user_permissions"
    fields       = ["name", "content_type__app_label", "codename"]

class _EmailAddressSection(TableSection):
    verbose_name = _("E-Mail Addresses")
    related_name = "emailaddress_set"
    fields       = ["email", "verified", "primary"]

class _EmailAddressInline(TabularInline):
    model            = EmailAddress
    fields           = ["email", "verified", "primary"]
    ordering         = ["email"]
    extra            = 0
    show_change_link = True
    tab              = True

class _AuthTokenSection(TableSection):
    verbose_name = _("Authentication Tokens")
    related_name = "auth_tokens"
    fields       = ["name", "is_active", "start_date", "end_date", *created_modified_by_fields]

class _AuthTokenInline(TabularInline):
    model            = AuthToken
    fk_name          = "user"
    fields           = ["token", "name", "is_active"]
    ordering         = ["token"]
    readonly_fields  = ["token"]
    extra            = 0
    show_change_link = True
    tab              = True

class UserResource(ImportExportModelResource):
    is_active        = Field(attribute="is_active",        widget=BooleanWidget())
    is_staff         = Field(attribute="is_staff",         widget=BooleanWidget())
    is_superuser     = Field(attribute="is_superuser",     widget=BooleanWidget())
    groups           = Field(attribute="groups",           widget=ManyToManyWidget(model=Group, field="slug"))
    user_permissions = Field(attribute="user_permissions", widget=PermissionManyToManyWidget())

    class Meta:
        model = User
        import_id_fields = ["username"]
        fields = [
            "username", "delete", "user_type", "email",
            "first_name", "last_name", "date_joined",
            "is_active", "is_staff", "is_superuser",
            "groups", "user_permissions",
            "description", "picture"
        ]

class UserAdmin(CustomModelAdmin, DjangoUserAdmin):
    """
    Integrate additional application-user fields into Django's User admin.
    """
    form                 = UserChangeForm
    add_form             = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    resource_classes     = [UserResource]
    list_display         = ["full_name", "username", "is_staff", "is_superuser", "user_type"]
    list_display_links   = ["full_name", "username"]
    list_filter          = [*DjangoUserAdmin.list_filter, "is_superuser", "user_type"]
    list_sections        = [_GroupSection, _PermissionSection, _EmailAddressSection, _AuthTokenSection]
    inlines              = [_EmailAddressInline, _AuthTokenInline]

    def get_queryset(self, request):
        """
        Prefetch relations to optimize database performance for the changelist sections.
        """
        return super().get_queryset(request).prefetch_related(
            "groups",
            "user_permissions",
            "user_permissions__content_type",
            "emailaddress_set",
        )

    add_fieldsets = [
        (None, {
            "classes": ["wide"],
            "fields": ["user_type", "username", "usable_password", "password1", "password2"],
        }),
        (_("Personal Information"), {
            "classes": ["wide"],
            "fields": ["first_name", "last_name", "email", "description", "picture"],
        }),
    ]

    def get_form(self, request, obj=None, **kwargs):
        """
        Require the e-mail field.

        See: https://stackoverflow.com/a/66562177
        """
        form = super().get_form(request, obj, **kwargs)

        if "email" in form.base_fields:
            form.base_fields["email"].required = True

        return form

UserAdmin.fieldsets[0][1]["fields"] += ("user_type",)

UserAdmin.fieldsets[1][1]["classes"] = ["tab"]
UserAdmin.fieldsets[1][1]["fields"] += ("description", "picture")
UserAdmin.fieldsets[2][1]["classes"] = ["tab"]
