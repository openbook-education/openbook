# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.utils.translation import gettext_lazy as _

from openbook.admin           import CustomModelAdmin
from openbook.admin           import ImportExportModelResource
from ..models.site            import Site

class SiteResource(ImportExportModelResource):
    class Meta:
        model = Site
        fields = ["id", "delete", "domain", "name", "short_name", "about_url", "brand_color"]

class SiteAdmin(CustomModelAdmin):
    model              = Site
    resource_classes   = [SiteResource]
    list_display       = ["id", "domain", "name", "short_name"]
    list_display_links = ["id", "domain"]
    search_fields      = ["domain", "name", "short_name"]

    fieldsets = [
        (None, {
            "fields": ["domain", "about_url"],
        }),
        (_("Theming"), {
            "classes": ["tab"],
            "fields": ["name", "short_name", "brand_color"],
        }),
    ]