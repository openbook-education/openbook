# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

import typing

from .viewsets.course                     import CourseViewSet
from .viewsets.course_material            import CourseMaterialViewSet
from .viewsets.course_material_page_range import CourseMaterialPageRangeViewSet
from .viewsets.library_group              import LibraryGroupViewSet
from .viewsets.library_link               import LibraryLinkViewSet
from .viewsets.textbook                   import TextbookViewSet
from .viewsets.textbook_page              import TextbookPageViewSet

if typing.TYPE_CHECKING:
    from rest_framework.routers           import DefaultRouter

def register_api_routes(router: DefaultRouter, prefix: str) -> None:
    router.register(f"{prefix}/courses", CourseViewSet, basename="course")
    router.register(f"{prefix}/library_groups", LibraryGroupViewSet, basename="library-group")
    router.register(f"{prefix}/library_links", LibraryLinkViewSet, basename="library-link")
    router.register(f"{prefix}/textbooks", TextbookViewSet, basename="textbook")
    router.register(f"{prefix}/textbook_pages", TextbookPageViewSet, basename="textbook-page")
    router.register(f"{prefix}/course_materials", CourseMaterialViewSet, basename="course-material")
    router.register(f"{prefix}/course_material_page_ranges", CourseMaterialPageRangeViewSet, basename="course-material-page-range")
