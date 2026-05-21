# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.contrib.auth.models       import Group as DjangoGroup
from django.utils.translation         import gettext_lazy as _
from unfold.decorators                import display

from openbook.core.models.mixins.slug import UniqueSlugMixin

class Group(UniqueSlugMixin, DjangoGroup):
    """
    Move the Group model from ``django.contrib.auth`` into our own app.

    This makes users and groups appear together in the Admin.
    """
    class Meta:
        verbose_name        = _("User Group")
        verbose_name_plural = _("User Groups")


    @display(label=True, description=_("User Count"))
    def user_count(self):
        return self.user_set.count()
