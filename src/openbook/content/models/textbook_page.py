# OpenBook: Interactive Online Textbooks
# © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.db import models
from django.utils.translation import gettext_lazy as _

from openbook.auth.models.mixins.audit import CreatedModifiedByMixin
from openbook.core.models.mixins.text import NameDescriptionMixin
from openbook.core.models.mixins.uuid import UUIDMixin


class TextbookPage(UUIDMixin, NameDescriptionMixin, CreatedModifiedByMixin):
    """
    Ordered tree node inside a textbook.

    Intermediate nodes represent chapters/subchapters and leaf nodes usually contain page content.
    """

    textbook = models.ForeignKey(
        "Textbook",
        verbose_name=_("Textbook"),
        on_delete=models.CASCADE,
        related_name="pages",
    )

    parent = models.ForeignKey(
        "self",
        verbose_name=_("Parent Page"),
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True,
    )

    position = models.PositiveIntegerField(
        verbose_name=_("Position"),
        default=0,
        help_text=_("Position among siblings in ascending order."),
    )

    content = models.JSONField(
        verbose_name=_("Content Tree"),
        default=dict,
        blank=True,
        help_text=_("DOM-like content tree with text and interactive components."),
    )

    class Meta:
        verbose_name = _("Textbook Page")
        verbose_name_plural = _("Textbook Pages")
        ordering = ("textbook_id", "parent_id", "position", "name")
        indexes = [
            models.Index(fields=("textbook", "parent", "position")),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("textbook", "parent", "position"),
                name="openbook_content_unique_page_position_within_parent",
            ),
        ]

    def clean(self):
        super().clean()

        if self.parent and self.parent.textbook_id != self.textbook_id:
            from django.core.exceptions import ValidationError

            raise ValidationError(
                {"parent": _("Parent page must belong to the same textbook.")}
            )
