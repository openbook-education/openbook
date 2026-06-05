# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

import base64, mimetypes
from django import template

register = template.Library()

@register.filter
def data_uri(file):
    """
    Generate a data URI with the content of the given file. The file usually will
    be an uploaded media file.
    """
    if not file:
        return ""

    mime = mimetypes.guess_type(file.name)[0] or "application/binary"

    with file.open('rb') as f:
        base64_data = base64.b64encode(f.read()).decode('utf-8')

    return f"data:{mime};base64,{base64_data}"
