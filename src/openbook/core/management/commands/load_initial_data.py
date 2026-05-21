# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.core                 import management
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Load fixtures will initial data for the OpenBook Server"

    FIXTURES = [
        "openbook_core/site",
        "openbook_core/languages",
        "openbook_auth/auth_config",
        "openbook_auth/mocksaml",
        "openbook_auth/anonymous_permissions",
        "openbook_auth/groups",
        "openbook_auth/signup_group_assignments",
        "openbook_content/library_groups",
        "openbook_content/courses",
    ]

    def handle(self, *args, **options):
        for fixture in self.FIXTURES:
            management.call_command("loaddata", fixture, verbosity=1)
