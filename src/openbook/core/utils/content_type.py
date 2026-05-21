# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.contrib.contenttypes.models import ContentType

def model_string_for_content_type(content_type: "ContentType") -> str:
    """
    Serialize content type objet into model string as used by Django: `{app_label}.{model}`
    """
    return f"{content_type.app_label}.{content_type.model}".lower() if content_type else ""

def content_type_for_model_string(model_string: str) -> "ContentType":
    """
    Get content type object for a given model string or raise `ContentType.DoesNotExist`,
    when the content type cannot be found.
    """
    if not model_string:
        return None
    
    app_label, model = model_string.split(".", 1)
    return ContentType.objects.get(app_label=app_label, model=model)
