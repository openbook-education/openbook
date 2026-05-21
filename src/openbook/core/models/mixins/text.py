# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import markdown

from django.db                  import models
from django.utils.translation   import gettext_lazy as _

class NameDescriptionMixin(models.Model):
    """
    Mixin for models with a clear-text short name and long description in either plain text,
    HTML or Markdown format.
    """
    class TextFormatChoices(models.TextChoices):
        """
        Formatted text content can either be in plain text, HTML or Markdown format.
        """
        PLAIN_TEXT = "TEXT", _("Plain Text")
        HTML       = "HTML", _("HTML")
        MARKDOWN   = "MD",   _("Markdown")

    name        = models.CharField(verbose_name=_("Name"), max_length=255, null=False, blank=False)
    description = models.TextField(verbose_name=_("Description"), null=False, blank=True)

    text_format = models.CharField(
        verbose_name = _("Text Format"),
        max_length   = 10,
        choices      = TextFormatChoices,
        null         = False,
        blank        = False,
        default      = TextFormatChoices.MARKDOWN,
    )

    class Meta:
        abstract = True
    
    def __str__(self):
        return self.name
    
    def get_formatted_description(self):
        """
        Return the description in a format that can be directly embedded into HTML.

        If the description is in HTML format, it will be returned as is. If it is in Markdown format,
        it will be converted to HTML first. If it is in plain text format, it will be wrapped in a
        `<pre>` tag.
        """
        if self.text_format == self.TextFormatChoices.MARKDOWN:
            return markdown.markdown(self.description)
        elif self.text_format == self.TextFormatChoices.PLAIN_TEXT:
            return "<pre>{}</pre>".format(self.description)
        else:
            return self.description
