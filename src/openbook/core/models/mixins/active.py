# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.db                  import models
from django.utils.translation   import gettext_lazy as _

class ActiveInactiveMixin(models.Model):
    """
    Mixin for models with an active/inactive state.
    
    The `__str__()` method returns `"(inactive)"`, if the object is inactive. This can be
    used in one's own `__str__()` implementation, if desired.
    """
    is_active = models.BooleanField(verbose_name=_("Active"), default=True)

    class Meta:
        abstract = True
    
    def __str__(self):
        return _("(inactive)") if not self.is_active else ""
