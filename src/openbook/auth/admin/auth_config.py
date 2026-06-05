# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.utils.translation         import gettext_lazy as _
from import_export.fields             import Field
from import_export.widgets            import ForeignKeyWidget
from unfold.admin                     import TabularInline

from openbook.admin                   import CustomModelAdmin
from openbook.admin                   import ImportExportModelResource
from openbook.core.import_export.site import SiteForeignKeyWidget
from openbook.core.models.language    import Language
from ..import_export.auth_config      import AuthConfigForeignKeyWidget
from ..models.auth_config             import AuthConfig
from ..models.auth_config             import AuthConfigText

class AuthConfigResource(ImportExportModelResource):
    site = Field(attribute="site", widget=SiteForeignKeyWidget())

    class Meta:
        model  = AuthConfig
        fields = [
            "site", "delete",
            "local_signup_allowed", "signup_email_suffix", "logout_next_url",
            "signup_image", "login_image", "logout_image", "password_reset_image",
        ]
        import_id_fields = ["site"]

    @classmethod
    def get_display_name(cls):
        return _("Authentication Settings")

class AuthConfigTextResource(ImportExportModelResource):
    parent   = Field(attribute="parent", widget=AuthConfigForeignKeyWidget())
    language = Field(attribute="language", widget=ForeignKeyWidget(model=Language, field="language"))

    class Meta:
        model  = AuthConfigText
        fields = [
            "id", "delete",
            "parent", "language", "logout_next_text",
        ]

    @classmethod
    def get_display_name(cls):
        return _("Authorization Setting Texts")

    def filter_export(self, queryset, **kwargs):
        """
        Export all rows for this model.

        Use this because by default it is not possible to export another model than
        the one from the admin view.
        """
        return self._meta.model.objects.all()

class _AuthConfigTextInline(TabularInline):
    model            = AuthConfigText
    fields           = ["language", "logout_next_text"]
    ordering         = ["language"]
    extra            = 0
    show_change_link = False
    tab              = True

class AuthConfigAdmin(CustomModelAdmin):
    model               = AuthConfig
    resource_classes    = [AuthConfigResource, AuthConfigTextResource]
    ordering            = ["site__domain"]
    list_display        = ["site__domain", "site__name", "local_signup_allowed", "signup_email_suffix", "logout_next_url"]
    list_display_links  = ["site__domain", "site__name", "local_signup_allowed", "signup_email_suffix"]
    list_editable       = ["logout_next_url"]
    list_select_related = ["site"]
    search_fields       = ["site__domain", "site__name", "site__short_name", "signup_email_suffix", "logout_next_url"]
    inlines             = [_AuthConfigTextInline]

    fieldsets = [
        (None, {
            "fields": ["site"]
        }),
        (_("Local User Registration"), {
            "classes": ["tab"],
            "fields": ["local_signup_allowed", "signup_email_suffix"]
        }),
        (_("Pages"), {
            "classes": ["tab"],
            "fields": ["signup_image", "login_image", "logout_image", "password_reset_image", "logout_next_url"]
        }),
    ]
