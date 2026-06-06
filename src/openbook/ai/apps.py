# OpenBook: Interactive Online Textbooks
# © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.apps              import AppConfig
from django.utils.translation import gettext_lazy as _

class AIApp(AppConfig):
    name         = "openbook.ai"
    label        = "openbook_ai"
    verbose_name = _("AI Features")
