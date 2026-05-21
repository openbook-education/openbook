# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from json import JSONEncoder

class PrettyPrintJSONEncoder(JSONEncoder):
    """
    JSON encoder with pretty printing to make sure that saved values are indented
    for easier editing in the Django admin. See: https://unfoldadmin.com/docs/fields/json/
    """
    def __init__(self, *args, indent, sort_keys, **kwargs):
        super().__init__(*args, indent=4, sort_keys=False, **kwargs)