# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.db import models
from django.utils.translation import gettext_lazy as _

class Language(models.Model):
    """
    Simple data model for available languages. Administrators need to customize a list of
    languages that should be supported by the installation. This allows to maintain translations
    of these langauges for all translatable database models.

    NOTE: Some translated texts come from the application itself. They need to be translated
    with the Django `manage.py` command and gettext.
    """
    language = models.CharField(verbose_name=_("Language Code"), max_length=3, primary_key=True)
    name     = models.CharField(verbose_name=_("Translated Name"), max_length=64)

    def __str__(self):
        return self.language
