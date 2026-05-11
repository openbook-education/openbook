# OpenBook: Interactive Online Textbooks - Server
# © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from openbook.auth.models.mixins.audit import CreatedModifiedByMixin
from openbook.auth.models.mixins.scope import ScopedRolesMixin
from openbook.core.models.mixins.slug import NonUniqueSlugMixin
from openbook.core.models.mixins.text import NameDescriptionMixin
from openbook.core.models.mixins.uuid import UUIDMixin


class LibraryGroup(UUIDMixin, NonUniqueSlugMixin, NameDescriptionMixin, ScopedRolesMixin, CreatedModifiedByMixin):
    """
    Recursive library tree for organizing textbooks and courses.

    The group itself acts as permission scope so nested role inheritance can be added later.
    """

    parent = models.ForeignKey(
        "self",
        verbose_name=_("Parent Group"),
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Library Group")
        verbose_name_plural = _("Library Groups")
        ordering = ("name",)
        indexes = [
            models.Index(fields=("parent", "name")),
            models.Index(fields=("parent", "slug")),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("parent", "slug"),
                condition=Q(parent__isnull=False),
                name="openbook_content_unique_library_group_slug_in_parent",
            ),
            models.UniqueConstraint(
                fields=("slug",),
                condition=Q(parent__isnull=True),
                name="openbook_content_unique_library_group_slug_root",
            ),
        ]
