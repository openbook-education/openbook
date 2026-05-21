# OpenBook: Interactive Online Textbooks
# © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from openbook.auth.models.mixins.audit import CreatedModifiedByMixin
from openbook.core.models.mixins.uuid import UUIDMixin


class CourseMaterial(UUIDMixin, CreatedModifiedByMixin):
    """
    Ordered syllabus item of a course.

    Each item references one textbook and optionally narrows it to multiple page ranges.
    """

    course = models.ForeignKey(
        "openbook_content.Course",
        verbose_name=_("Course"),
        on_delete=models.CASCADE,
        related_name="materials",
    )

    textbook = models.ForeignKey(
        "openbook_content.Textbook",
        verbose_name=_("Textbook"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="used_in_courses",
    )

    position = models.PositiveIntegerField(
        verbose_name=_("Position"),
        default=0,
        help_text=_("Reading order index inside the course syllabus."),
    )

    class Meta:
        verbose_name = _("Course Material")
        verbose_name_plural = _("Course Materials")
        ordering = ("course", "position")
        indexes = [
            models.Index(fields=("course", "position")),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("course", "position"),
                name="openbook_content_unique_course_material_position",
            ),
            models.UniqueConstraint(
                fields=("course", "textbook"),
                name="openbook_content_unique_course_textbook_material",
            ),
        ]

    def clean(self):
        super().clean()

        if not self.textbook:
            raise ValidationError(
                {"textbook": _("A material entry must reference a textbook.")}
            )

    def __str__(self):
        textbook = self.textbook.name if self.textbook_id else _("No textbook")
        return f"{self.course.name}: {textbook} ({self.position})"


class CourseMaterialPageRange(UUIDMixin, CreatedModifiedByMixin):
    """Page range selection for a course material entry."""

    material = models.ForeignKey(
        "openbook_content.CourseMaterial",
        verbose_name=_("Course Material"),
        on_delete=models.CASCADE,
        related_name="page_ranges",
    )

    start_page = models.ForeignKey(
        "openbook_content.TextbookPage",
        verbose_name=_("Start Page"),
        on_delete=models.CASCADE,
        related_name="course_material_range_starts",
    )

    end_page = models.ForeignKey(
        "openbook_content.TextbookPage",
        verbose_name=_("End Page"),
        on_delete=models.CASCADE,
        related_name="course_material_range_ends",
    )

    position = models.PositiveIntegerField(
        verbose_name=_("Position"),
        default=0,
        help_text=_("Order of the selected ranges within one syllabus item."),
    )

    class Meta:
        verbose_name = _("Course Material Page Range")
        verbose_name_plural = _("Course Material Page Ranges")
        ordering = ("material", "position", "id")
        indexes = [
            models.Index(fields=("material", "position")),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("material", "position"),
                name="openbook_content_unique_material_page_range_position",
            ),
            models.UniqueConstraint(
                fields=("material", "start_page", "end_page"),
                name="openbook_content_unique_material_page_range",
            ),
        ]

    def clean(self):
        super().clean()

        if self.start_page.textbook_id != self.material.textbook_id:
            raise ValidationError(
                {"start_page": _("Start page must belong to the same textbook as the material.")}
            )

        if self.end_page.textbook_id != self.material.textbook_id:
            raise ValidationError(
                {"end_page": _("End page must belong to the same textbook as the material.")}
            )

    def __str__(self):
        start = self.start_page.name if self.start_page_id else "?"
        end = self.end_page.name if self.end_page_id else "?"
        return f"{self.material}: {start} - {end}"
