# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.contrib.admin             import display
from django.forms                     import JSONField
from django.forms                     import ModelChoiceField
from django.forms                     import inlineformset_factory
from django.utils.translation         import gettext_lazy as _
from import_export.fields             import Field
from import_export.widgets            import CharWidget
from unfold.admin                     import StackedInline
from unfold.sections                  import TableSection
from unfold.widgets                   import UnfoldAdminSelectWidget
from unfold.widgets                   import UnfoldAdminTextareaWidget

from openbook.admin                   import CustomModelAdmin
from openbook.admin                   import ImportExportModelResource
from ..import_export.html_library     import HTMLLibraryForeignKeyWidget
from ..models.html_component          import HTMLComponent
from ..models.html_component          import HTMLComponentDefinition
from ..models.html_library            import HTMLLibraryVersion
from ..models.utils.json              import PrettyPrintJSONEncoder

# =======================
# Import/Export Resources
# =======================

class HTMLComponentResource(ImportExportModelResource):
    library = Field(attribute="library", widget=HTMLLibraryForeignKeyWidget())

    class Meta:
        model = HTMLComponent
        fields = ["id", "delete", "library", "tag_name"]

    @classmethod
    def get_display_name(cls):
        return _("HTML Components")

class HTMLComponentDefinitionResource(ImportExportModelResource):
    library  = Field(attribute="library_version__library", widget=HTMLLibraryForeignKeyWidget())
    version  = Field(attribute="library_version__version", widget=CharWidget())
    tag_name = Field(attribute="html_component__tag_name", widget=CharWidget())

    class Meta:
        model = HTMLComponentDefinition
        #fields = ["id", "delete", "html_component", "library_version", "definition"]
        fields = ["id", "delete", "library", "version", "tag_name", "definition"]

    def import_field(self, field: Field, instance: HTMLComponentDefinition, row: dict, is_m2m=False, **kwargs):
        match field.column_name:
            case "library":
                pass
            case "version":
                instance.library_version = HTMLLibraryVersion.get_by_library_version(row["library"], row["version"])
            case "tag_name":
                instance.html_component = HTMLComponent.get_by_tag_name(row["library"], row["tag_name"])
            case _:
                super().import_field(field, instance, row, is_m2m, **kwargs)

    @classmethod
    def get_display_name(cls):
        return _("HTML Component Definitions")

# ====================
# Change List Sections
# ====================

class _HTMLComponentDefinitionSection(TableSection):
    verbose_name = _("Versions")
    related_name = "definitions"
    fields = [
        "library_version_version",
        "library_version_created_by", "library_version_created_at",
        "library_version_modified_by", "library_version_modified_at",
    ]

# ============
# Inline Views
# ============

class _HTMLComponentDefinitionInline(StackedInline):
    model               = HTMLComponentDefinition
    ordering            = ["-library_version__version"]
    fields              = ["library_version", "definition"]
    extra               = 0
    show_change_link    = True
    verbose_name        = _("Definition")
    verbose_name_plural = _("Definitions")

    read_only_fields = [
        "library_version_created_by", "library_version_created_at",
        "library_version_modified_by", "library_version_modified_at",
    ]

    def get_formset(self, request, obj=None, **kwargs):
        """
        Provide customized formset that only allowed to choose library versions for the
        library set on the HTML component parent object.
        
        NOTE: this breaks the formfield overrides in Django Unfold, that overrides the stock
        widgets with styled widgets. Therefor we need to initialize even the non-customized
        fields here to assign the styled widgets.
        """
        def formfield_callback(dbfield, **kwargs):
            match dbfield.name:
                case "library_version":
                    qs = HTMLLibraryVersion.objects.none()

                    if obj.library is not None:
                        qs = HTMLLibraryVersion.objects.filter(parent = obj.library)

                    return ModelChoiceField(queryset=qs, widget=UnfoldAdminSelectWidget())
                case "definition":
                    return JSONField(widget=UnfoldAdminTextareaWidget(), encoder=PrettyPrintJSONEncoder)
                case _:
                    return dbfield.formfield(**kwargs)

        return inlineformset_factory(
            model              = HTMLComponentDefinition,
            parent_model       = HTMLComponent,
            fields             = "__all__",
            formfield_callback = formfield_callback,
            extra              = 0,
        )

    def library_version_created_by(self, instance):
        return instance.library_version_created_by()
    
    def library_version_created_at(self, instance):
        return instance.library_version_created_at()
    
    def library_version_modified_by(self, instance):
        return instance.library_version_modified_by()
    
    def library_version_modified_at(self, instance):
        return instance.library_version_modified_at()
    
    library_version_created_by.short_description  = _("Created By")
    library_version_created_at.short_description  = _("Created At")
    library_version_modified_by.short_description = _("Modified By")
    library_version_modified_at.short_description = _("Modified At")

# ==========
# Admin View
# ==========

class HTMLComponentAdmin(CustomModelAdmin):
    model               = HTMLComponent
    resource_classes    = [HTMLComponentResource, HTMLComponentDefinitionResource]
    list_display        = ["library", "tag_name", "min_version", "max_version"]
    list_display_links  = ["library", "tag_name", "min_version", "max_version"]
    list_filter         = ["library__organization", "library__author"]
    list_select_related = ["library"]
    readonly_fields     = ["library_readonly", "min_version", "max_version"]
    search_fields       = ["library__organization", "library__name", "library__author", "tag_name"]
    ordering            = ["library__organization", "library__name", "tag_name"]
    list_sections       = [_HTMLComponentDefinitionSection]
    inlines             = [_HTMLComponentDefinitionInline]

    fieldsets = [
        (None, {
            "fields": ["library_readonly", "tag_name"]
        })
    ]

    add_fieldsets = [
        (None, {
            "fields": ["library", "tag_name"]
        })
    ]

    def get_formsets_with_inlines(self, request, obj=None):
        """
        Hide inlines in the add view, since first the model must be saved to know
        from which library the allowed versions come from.
        """
        for inline in self.get_inline_instances(request, obj):
            if obj is not None:
                yield inline.get_formset(request, obj), inline
    
    @display(description=_("Library"))
    def library_readonly(self, obj):
        return obj.library