# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.http                       import HttpResponse
from django.http                       import HttpRequest
from django.utils.translation          import gettext_lazy as _
from import_export.fields              import Field
from unfold.admin                      import StackedInline
from unfold.admin                      import TabularInline
from unfold.decorators                 import action
from unfold.sections                   import TableSection

from openbook.admin                    import CustomModelAdmin
from openbook.admin                    import ImportExportModelResource
from openbook.auth.admin.mixins.audit  import created_modified_by_fields
from openbook.auth.admin.mixins.audit  import created_modified_by_fieldset
from openbook.auth.admin.mixins.audit  import created_modified_by_filter
from openbook.auth.admin.mixins.audit  import created_modified_by_related
from ..import_export.boolean           import BooleanWidget
from ..models.html_component           import HTMLComponent
from ..models.html_library             import HTMLLibrary
from ..models.html_library             import HTMLLibraryText
from ..models.html_library             import HTMLLibraryVersion
from ..views.html_library              import UnpackHTMLLibraryArchivesView

# =======================
# Import/Export Resources
# =======================

class HTMLLibraryResource(ImportExportModelResource):
    published = Field(attribute="published", widget=BooleanWidget())

    class Meta:
        model = HTMLLibrary
        fields = [
            "id", "delete",
            "organization", "name",
            "author", "license",
            "website", "coderepo", "bugtracker",
            "published",
        ]

    @classmethod
    def get_display_name(cls):
        return _("HTML Libraries")

class HTMLLibraryTextResource(ImportExportModelResource):
    class Meta:
        model = HTMLLibraryText
        fields = (
            "id", "delete",
            "parent", "language", "short_description"
        )

    @classmethod
    def get_display_name(cls):
        return _("HTML Library Texts")
    
    def filter_export(self, queryset, **kwargs):
        """
        Needed because by default it is not possible to export another model than the one
        from the admin view.
        """
        return self._meta.model.objects.all()

class HTMLLibraryVersionResource(ImportExportModelResource):
    class Meta:
        model = HTMLLibraryVersion
        fields = [
            "id", "delete",
            "parent", "version", "dependencies", "frontend_url",
            "file_data", "file_name", "file_size", "mime_type",
        ]

    @classmethod
    def get_display_name(cls):
        return _("HTML Library Versions")

    def filter_export(self, queryset, **kwargs):
        """
        Needed because by default it is not possible to export another model than the one
        from the admin view.
        """
        return self._meta.model.objects.all()

# ====================
# Change List Sections
# ====================

class _HTMLLibraryVersionSection(TableSection):
    verbose_name = _("Versions")
    related_name = "versions"
    fields       = ["version", "frontend_url", "file_name", "file_size", "mime_type", *created_modified_by_fields]

class _HTMLComponentSection(TableSection):
    verbose_name = _("HTML Components")
    related_name = "components"
    fields       = ["tag_name", "min_version", "max_version"]

# ============
# Inline Views
# ============

class _HTMLLibraryTextInline(TabularInline):
    model               = HTMLLibraryText
    fields              = ["language", "short_description"]
    ordering            = ["language"]
    extra               = 0
    show_change_link    = True
    tab                 = True
    verbose_name        = _("Translated Text")
    verbose_name_plural = _("Translated Texts")

class _HTMLLibraryVersionInline(StackedInline):
    model               = HTMLLibraryVersion
    ordering            = ["-version"]
    readonly_fields     = ["frontend_url", "file_name", "file_size", "mime_type", *created_modified_by_fields]
    extra               = 0
    show_change_link    = True
    tab                 = True
    verbose_name        = _("Version")
    verbose_name_plural = _("Versions")

    fieldsets = [
        (None, {
                "fields": [
                    ("version", "frontend_url"),
                    ("file_data", "file_size"),
                    "dependencies",
                    ("created_by", "created_at"),
                    ("modified_by", "modified_at"),
                ],
        }),
    ]

    add_fieldsets = [
        (None, {
                "fields": [
                    ("version", "frontend_url"),
                    ("file_data", "file_size"),
                    "dependencies",
                ],
        }),
    ]

class _HTMLComponentInline(TabularInline):
    model               = HTMLComponent
    ordering            = ["tag_name"]
    fields              = ["tag_name"] #, "min_version", "max_version"
    read_only_fields    = ["min_version", "max_version"]
    extra               = 0
    show_change_link    = True
    tab                 = True
    verbose_name        = _("HTML Components")
    verbose_name_plural = _("HTML Components")

    def min_version(self, instance):
        return instance.min_version()
    
    def max_version(self, instance):
        return instance.max_version()
    
    min_version.short_description = _("Minimum Version")
    max_version.short_description = _("Maximum Version")

# ==========
# Admin View
# ==========

class HTMLLibraryAdmin(CustomModelAdmin):
    model               = HTMLLibrary
    resource_classes    = [HTMLLibraryResource, HTMLLibraryTextResource, HTMLLibraryVersionResource]
    list_display        = ["fqn", "author", "license", "published", *created_modified_by_fields]
    list_display_links  = ["fqn", "author", "license", "published"]
    list_filter         = ["organization", "author", "license", "published", *created_modified_by_filter]
    list_select_related = [*created_modified_by_related]
    readonly_fields     = ["fqn", *created_modified_by_fields]
    search_fields       = ["organization", "name", "author"]
    ordering            = ["organization", "name"]
    list_sections       = [_HTMLLibraryVersionSection, _HTMLComponentSection]
    inlines             = [_HTMLLibraryTextInline, _HTMLLibraryVersionInline, _HTMLComponentInline]
    actions_list        = []
    actions_detail      = ["unpack_archives"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("versions")

    fieldsets = [
        (None, {
            "fields": ["organization", "name", "published"],
        }),
        (_("Meta Data"), {
            "classes": ["tab"],
            "fields": ["author", "license", "website", "coderepo", "bugtracker"],
        }),
        (_("Read Me"), {
            "classes": ["tab"],
            "fields": ["readme", "text_format"],
        }),
        created_modified_by_fieldset,
    ]

    add_fieldsets = [
        (None, {
            "fields": ["organization", "name", "published"],
        }),
        (_("Meta Data"), {
            "classes": ["tab"],
            "fields": ["author", "license", "website", "coderepo", "bugtracker"],
        }),
        (_("Read Me"), {
            "classes": ["tab"],
            "fields": ["readme", "text_format"],
        }),
    ]

    @action(description=_("Unpack archive files"), icon="folder_zip", url_path="unpack")
    def unpack_archives(self, request: HttpRequest, object_id: str) -> HttpResponse:
        # Directly rendering the view instead of a redirect, since the view works stand-alone
        view = UnpackHTMLLibraryArchivesView.as_view(model_admin=self)
        return view(request, library_id=object_id)