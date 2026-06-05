# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

import typing

from .viewsets.html_component            import HTMLComponentViewSet
from .viewsets.html_component_definition import HTMLComponentDefinitionViewSet
from .viewsets.html_library              import HTMLLibraryViewSet
from .viewsets.html_library_text         import HTMLLibraryTextViewSet
from .viewsets.html_library_version      import HTMLLibraryVersionViewSet
from .viewsets.media_file                import MediaFileViewSet
from .viewsets.language                  import LanguageViewSet
from .viewsets.site                      import SiteViewSet

if typing.TYPE_CHECKING:
    from rest_framework.routers          import DefaultRouter

def register_api_routes(router: DefaultRouter, prefix: str) -> None:
    router.register(f"{prefix}/html_library/components",            HTMLComponentViewSet,           basename="html_component")
    router.register(f"{prefix}/html_library/component_definitions", HTMLComponentDefinitionViewSet, basename="html_component_definition")
    router.register(f"{prefix}/html_library/libraries",             HTMLLibraryViewSet,             basename="html_library")
    router.register(f"{prefix}/html_library/texts",                 HTMLLibraryTextViewSet,         basename="html_library_text")
    router.register(f"{prefix}/html_library/versions",              HTMLLibraryVersionViewSet,      basename="html_library_version")
    router.register(f"{prefix}/languages",                          LanguageViewSet,                basename="language")
    router.register(f"{prefix}/media_files",                        MediaFileViewSet,               basename="media_file")
    router.register(f"{prefix}/sites",                              SiteViewSet,                    basename="site")
