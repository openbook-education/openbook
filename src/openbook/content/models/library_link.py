# OpenBook: Interactive Online Textbooks - Server
# © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from openbook.auth.models.mixins.audit import CreatedModifiedByMixin
from openbook.core.models.mixins.uuid import UUIDMixin


class LibraryLink(UUIDMixin, CreatedModifiedByMixin):
    """
    Shortcut entry inside a library group.

    Links point to courses or textbooks whose home group is different from the link location.
    """

    group = models.ForeignKey(
        "openbook_content.LibraryGroup",
        verbose_name=_("Library Group"),
        on_delete=models.CASCADE,
        related_name="links",
    )

    course = models.ForeignKey(
        "openbook_content.Course",
        verbose_name=_("Course"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="library_links",
    )

    textbook = models.ForeignKey(
        "openbook_content.Textbook",
        verbose_name=_("Textbook"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="library_links",
    )

    position = models.PositiveIntegerField(
        verbose_name=_("Position"),
        default=0,
        help_text=_("Sort order inside the group."),
    )

    class Meta:
        verbose_name = _("Library Link")
        verbose_name_plural = _("Library Links")
        ordering = ("group", "position", "id")
        indexes = [
            models.Index(fields=("group", "position")),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    (Q(course__isnull=False) & Q(textbook__isnull=True))
                    | (Q(course__isnull=True) & Q(textbook__isnull=False))
                ),
                name="openbook_content_library_link_single_target",
            ),
            models.UniqueConstraint(
                fields=("group", "course"),
                condition=Q(course__isnull=False),
                name="openbook_content_unique_group_course_link",
            ),
            models.UniqueConstraint(
                fields=("group", "textbook"),
                condition=Q(textbook__isnull=False),
                name="openbook_content_unique_group_textbook_link",
            ),
        ]

    def clean(self):
        super().clean()

        if self.course and self.group_id and self.course.group_id == self.group_id:
            raise ValidationError(
                {"course": _("Links should only target courses from another group.")}
            )

        if self.textbook and self.group_id and self.textbook.group_id == self.group_id:
            raise ValidationError(
                {"textbook": _("Links should only target textbooks from another group.")}
            )

    def __str__(self):
        target = None

        if self.course_id:
            target = self.course.name
        elif self.textbook_id:
            target = self.textbook.name
        else:
            target = _("No target")

        return f"{self.group.name} -> {target}"
