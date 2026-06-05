# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.conf                import settings
from rest_framework.pagination  import PageNumberPagination as DRFPageNumberPagination

class PageNumberPagination(DRFPageNumberPagination):
    """
    Custom pagination class that allows changing the query parameters used for pagination
    in the Django config, following the same style the DRF uses for the filter backends.
    """
    page_query_param      = settings.REST_FRAMEWORK.get("PAGE_PARAM", "_page")
    page_size_query_param = settings.REST_FRAMEWORK.get("PAGE_SIZE_PARAM", "_page_size")