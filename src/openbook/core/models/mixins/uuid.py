# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import uuid

from django.db                  import models
from django.utils.translation   import gettext_lazy as _

class UUIDMixin(models.Model):
    """
    Mixin for models with a UUID primary key instead of Django's default Auto ID
    integer sequence. Since we might often use the IDs in APIs and URLs, for security
    reasons, we want to avoid predictable sequences. But unfortunately we cannot
    enforce this in Django, as Auto IDs needs to be integers.
    """
    id = models.UUIDField(verbose_name=_("Id"), primary_key=True, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Assign new UUID when saving a new entry.
        """
        if not self.id:
            self.id = uuid.uuid4()
        
        return super().save(*args, **kwargs)