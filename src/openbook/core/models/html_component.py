# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.contrib.admin     import display
from django.core.exceptions   import ValidationError
from django.db                import models
from django.utils.translation import gettext_lazy as _
from .mixins.uuid             import UUIDMixin
from .utils.json              import PrettyPrintJSONEncoder

class HTMLComponent(UUIDMixin):
    """
    HTML custom component defined in a HTML library. This model makes the custom elements known to
    the WYSIWYG editor.
    """
    library  = models.ForeignKey("htmllibrary", on_delete=models.CASCADE, related_name="components")
    tag_name = models.CharField(verbose_name=_("Tag Name"), max_length=100)

    @display(description=_("Minimum Version"))
    def min_version(self) -> str:
        return HTMLComponentDefinition.objects.filter(
            html_component=self
        ).aggregate(
            models.Min("library_version__version")
        )["library_version__version__min"]

    @display(description=_("Maximum Version"))
    def max_version(self) -> str:
        return HTMLComponentDefinition.objects.filter(
            html_component=self
        ).aggregate(
            models.Max("library_version__version")
        )["library_version__version__max"]

    class Meta:
        verbose_name        = _("HTML Component")
        verbose_name_plural = _("HTML Components")
        constraints         = [models.UniqueConstraint(fields=("library", "tag_name"), name="unique_html_component")]
    
    def __str__(self):
        return self.tag_name

    @classmethod
    def get_by_tag_name(cls, library_fqn: str, tag_name: str) -> "HTMLComponent":
        from .html_library import HTMLLibrary
        library = HTMLLibrary.get_by_fqn(library_fqn)
        return cls.objects.get(library=library, tag_name=tag_name)

class HTMLComponentDefinition(UUIDMixin):
    """
    Version dependent definition of a HTML component, containing a JSON manifest to be used by the
    WYSIWYG editor.
    """    
    html_component  = models.ForeignKey(HTMLComponent, on_delete=models.CASCADE, related_name="definitions")
    library_version = models.ForeignKey("htmllibraryversion", on_delete=models.CASCADE, related_name="components")
    definition      = models.JSONField(verbose_name=_("JSON Definition"), blank=True, default=None, encoder=PrettyPrintJSONEncoder)

    class Meta:
        verbose_name        = _("HTML Component Definition")
        verbose_name_plural = _("HTML Component Definitions")
        constraints         = [models.UniqueConstraint(fields=("html_component", "library_version"), name="unique_html_component_version")]

    def __str__(self):
        return f"{self.library_version}"

    @display(description=_("Version"))
    def library_version_version(self):
        return self.library_version.version if self.library_version else ""

    @display(description=_("Created By"))
    def library_version_created_by(self):
        return self.library_version.created_by if self.library_version else ""
    
    @display(description=_("Created At"))
    def library_version_created_at(self):
        return self.library_version.created_at if self.library_version else ""
    
    @display(description=_("Modified By"))
    def library_version_modified_by(self):
        return self.library_version.modified_by if self.library_version else ""
    
    @display(description=_("Modified At"))
    def library_version_modified_at(self):
        return self.library_version.modified_at if self.library_version else ""

    def clean(self):
        """
        Validate that HTML component and library version refer to the same library.
        """
        super().clean()

        if not self.html_component or not self.library_version:
            return
    
        if self.html_component.library.pk != self.library_version.parent.pk:
            raise ValidationError(_("HTML component and library version must belong to the same library"))
