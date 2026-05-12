# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from openbook.admin   import admin_site
from .course          import CourseAdmin
from .course_material import CourseMaterialAdmin
from .library_group   import LibraryGroupAdmin
from .library_link    import LibraryLinkAdmin
from .textbook        import TextbookAdmin
from .textbook_page   import TextbookPageAdmin
from ..               import models

admin_site.register(models.LibraryGroup,   LibraryGroupAdmin)
admin_site.register(models.LibraryLink,    LibraryLinkAdmin)
admin_site.register(models.Textbook,       TextbookAdmin)
admin_site.register(models.TextbookPage,   TextbookPageAdmin)
admin_site.register(models.Course,         CourseAdmin)
admin_site.register(models.CourseMaterial, CourseMaterialAdmin)
