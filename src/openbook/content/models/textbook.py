# OpenBook: Interactive Online Textbooks
# © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from openbook.auth.models.mixins.audit import CreatedModifiedByMixin
from openbook.core.models.mixins.slug import NonUniqueSlugMixin
from openbook.core.models.mixins.text import NameDescriptionMixin
from openbook.core.models.mixins.uuid import UUIDMixin


class Textbook(UUIDMixin, NonUniqueSlugMixin, NameDescriptionMixin, CreatedModifiedByMixin):
    """Reusable textbook that can be referenced by multiple courses."""

    group = models.ForeignKey(
        "openbook_content.LibraryGroup",
        verbose_name=_("Library Group"),
        on_delete=models.PROTECT,
        related_name="textbooks",
    )

    class Meta:
        verbose_name = _("Textbook")
        verbose_name_plural = _("Textbooks")
        ordering = ("group", "name")
