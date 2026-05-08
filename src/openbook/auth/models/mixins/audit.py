# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.conf                import settings
from django.contrib             import admin
from django.db                  import models
from django.utils.translation   import gettext_lazy as _

from ...middleware.current_user import get_current_user

class CreatedModifiedByMixin(models.Model):
    """
    Record the user and time of creation and last modification.
    """
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Created By"), on_delete=models.SET_NULL, blank=True, null=True)
    created_at  = models.DateTimeField(verbose_name=_("Created At"), auto_now_add=True, blank=True, null=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Modified By"), on_delete=models.SET_NULL, blank=True, null=True, related_name="+")
    modified_at = models.DateTimeField(verbose_name=_("Modified At"), auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Automatically populate the `created_by` and `modified_by` fields.
        Care must be taken to call `super().save(*args, **kwargs)` when this method is overridden.
        """
        user = get_current_user()

        if user and user.is_authenticated:
            if not self.created_by:
                self.created_by = user

            self.modified_by = user

        super().save(*args, **kwargs)

    @property
    @admin.display(description=_("Last Changed"))
    def created_modified_by(self):
        """
        Return a formatted string for display in the Admin or on the website.
        """
        if self.created_by and self.created_at:
            created = _("Created by {created_by} at {created_at}.").format(
                created_by = self.created_by,
                created_at = self.created_at.strftime("%x"),
            )
        elif self.created_by:
            created = _("Created by {created_by}.").format(created_by=self.created_by)
        elif self.created_at:
            created = _("Created at {created_at}.").format(created_at=self.created_at.strftime("%x"))

        if self.modified_by and self.modified_at:
            modified = _("Modified by {modified_by} at {modified_at}.").format(
                modified_by = self.modified_by,
                modified_at = self.modified_at.strftime("%x"),
            )
        elif self.modified_by:
            modified = _("Modified by {modified_by}.").format(modified_by=self.modified_by)
        elif self.modified_at:
            modified = _("Modified at {modified_at}.").format(modified_at=self.modified_at.strftime("%x"))

        if created and modified:
            return "%s %s" % (created, modified)
        elif created:
            return created
        elif modified:
            return modified
        else:
            return ""
