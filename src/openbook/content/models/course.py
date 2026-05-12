# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.db                         import models
from django.utils.translation          import gettext_lazy as _

from openbook.auth.models.mixins.audit import CreatedModifiedByMixin
from openbook.auth.models.mixins.scope import ScopedRolesMixin
from openbook.core.models.mixins.uuid  import UUIDMixin
from openbook.core.models.mixins.slug  import NonUniqueSlugMixin
from openbook.core.models.mixins.text  import NameDescriptionMixin

class Course(UUIDMixin, NonUniqueSlugMixin, NameDescriptionMixin, ScopedRolesMixin, CreatedModifiedByMixin):
    """
    A concrete course for one audience and time frame.

    Courses define a reading order over one or more textbooks/pages and can be reused from templates.
    """
    group = models.ForeignKey(
        "openbook_content.LibraryGroup",
        verbose_name = _("Library Group"),
        on_delete    = models.PROTECT,
        related_name = "courses",
    )

    # License (via new model in core)
    # Image
    # AI Notes (new mixin)
    # Learning Target Taxonomy
    # Activity Taxonomy
    is_template = models.BooleanField(
        verbose_name = _("Is Template"),
        help_text    = _("Flag that this course is only used for creating other courses."),
        default      = False,
    )

    class Meta():
        verbose_name        = _("Course")
        verbose_name_plural = _("Courses")
        ordering            = ("group_id", "name")
