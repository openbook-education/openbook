# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.contrib.auth.models         import Permission
from django.db                          import models
from django.utils.translation           import gettext_lazy as _

from openbook.core.models.mixins.active import ActiveInactiveMixin
from openbook.core.models.mixins.slug   import NonUniqueSlugMixin
from openbook.core.models.mixins.text   import NameDescriptionMixin
from openbook.core.models.mixins.uuid   import UUIDMixin

from .mixins.audit                      import CreatedModifiedByMixin
from .mixins.scope                      import ScopeMixin

class Role(UUIDMixin, ScopeMixin, NonUniqueSlugMixin, NameDescriptionMixin, ActiveInactiveMixin, CreatedModifiedByMixin):
    """
    Define roles for object-based permissions in a given context (scope).

    Roles bundle one or more permissions granted to all users assigned to them. For example,
    textbooks and courses use roles to restrict who can use them and how.
    """
    priority    = models.PositiveSmallIntegerField(verbose_name=_("Priority"), help_text=_("Low values mean less privileges. Make sure to correctly prioritize the rolls to avoid privilege escalation."))
    permissions = models.ManyToManyField(Permission, verbose_name=_("Permissions"), blank=True, related_name="roles")

    class Meta:
        verbose_name        = _("Role")
        verbose_name_plural = _("Roles")

        constraints = [
            models.UniqueConstraint(fields=("scope_type", "scope_uuid", "slug"), name="unique_scope_slug"),
        ]

        indexes = [
            models.Index(fields=("scope_type", "scope_uuid", "slug")),
        ]

    def __str__(self):
        return f"{self.name} {ActiveInactiveMixin.__str__(self)}".strip()
