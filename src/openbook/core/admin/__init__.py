# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from openbook.admin              import admin_site
from .html_component             import HTMLComponentAdmin
from .html_library               import HTMLLibraryAdmin
from .language                   import LanguageAdmin
from .media_file                 import MediaFileAdmin
from .site                       import SiteAdmin
from ..                          import models

admin_site.register(models.Site,          SiteAdmin)
admin_site.register(models.Language,      LanguageAdmin)
admin_site.register(models.HTMLLibrary,   HTMLLibraryAdmin)
admin_site.register(models.HTMLComponent, HTMLComponentAdmin)
admin_site.register(models.MediaFile,     MediaFileAdmin)