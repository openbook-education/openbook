# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.contrib                       import admin
from django.contrib.auth.models           import Permission
from django.db                            import models
from django.utils.translation             import gettext_lazy as _

from openbook.core.models.mixins.i18n     import TranslatableMixin
from openbook.core.models.mixins.uuid     import UUIDMixin
from ..utils                              import app_name_for_permission
from ..utils                              import perm_name_for_permission
from ..utils                              import perm_string_for_permission

class PermissionText(UUIDMixin, TranslatableMixin):
    """
    Store translated permission names.
    """
    parent = models.ForeignKey(Permission, verbose_name=_("Permission"), on_delete=models.CASCADE, related_name="translations")
    name   = models.CharField(verbose_name=_("Translated Name"), max_length=255, null=False, blank=False)

    class Meta(TranslatableMixin.Meta):
        verbose_name        = _("Permission: Translation")
        verbose_name_plural = _("Permission: Translations")

        constraints = (
            models.UniqueConstraint(fields=("parent", "language"), name="unique_permission_text_translation"),
        )

    @admin.display(description=_("Application"))
    def appname(self, obj=None):
        return app_name_for_permission(self.parent)

    @admin.display(description=_("Permission"))
    def perm_name(self, obj=None):
        return perm_name_for_permission(self.parent)

    @admin.display(description=_("Code"))
    def perm(self, obj=None):
        return perm_string_for_permission(self.parent)
