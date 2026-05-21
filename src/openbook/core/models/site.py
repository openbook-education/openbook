# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from colorfield.fields           import ColorField
from django.contrib.sites.models import Site as DjangoSite
from django.db                   import models
from django.utils.translation    import gettext_lazy as _

class Site(DjangoSite):
    """
    Custom version of Django's built-in Site model with some custom fields.
    """
    short_name  = models.CharField(verbose_name=_("Short Name"), max_length=50, null=False, blank=False)
    about_url   = models.URLField(verbose_name=_("Information Website"), help_text=_("URL of your website with information for your users"))
    brand_color = ColorField(verbose_name=_("Brand Color"), default="#e2001a")

    class Meta:
        verbose_name        = _("Website")
        verbose_name_plural = _("Websites")

    def __str__(self):
        return self.name
