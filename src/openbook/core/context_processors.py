# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.conf              import settings
from django.contrib           import messages
from django.http              import HttpRequest
from django.utils.translation import gettext_lazy as _
from .models                  import Site

def site(request: HttpRequest = None) -> dict:
    """
    Add the current site as customized in Django's Sites app to all templates.
    """
    try:
        site_id   = settings.SITE_ID or 1
        site_obj  = Site.objects.get(pk=site_id)

        return {
            "site": site_obj,
        }
    except Site.DoesNotExist:
        warning = _("WARNING: Website %s is not customized. Please login to the Admin and maintain its data.") % site_id
        messages.warning(request, warning)
        print(warning)

        return {}