# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import glob, os

from django.conf                 import settings
from django.core.exceptions      import ValidationError
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.utils.text           import format_lazy as _f
from django.utils.translation    import gettext_lazy as _
from ...models.html_library      import HTMLLibrary

class Command(BaseCommand):
    help = "Install HTML libraries from archive files"

    def __init__(self, *args, **kwargs):
        """
        Patch `self.stdout` to behave like Python's `sys.stdout`, which doesn't add newlines
        and takes no keyword arguments. It was well meant by the Django developers, but it
        really should make no difference where the stream is coming from.
        """
        super().__init__(*args, **kwargs)

        _write = self.stdout.write
        self.stdout.write = lambda x: _write(x, ending="")

    def add_arguments(self, parser):
        lib_install_dir = os.path.join(settings.MEDIA_ROOT, "lib-install")
        parser.add_argument(
            "-f", "--archive-file",
            dest    = "archive_file",
            type    = str,
            default = lib_install_dir,
            help    = _f(
                "HTML library archive file or directory with archives (default: {lib_install_dir})",
                lib_install_dir = lib_install_dir,
            ),
        )

        parser.add_argument(
            "-x",  "--extract-archive",
            dest    = "extract_archive",
            type    = bool,
            default = True,
            help    = _("Extract archive file on filesystem (default: true)"),
        )

        parser.add_argument(
            "-ul", "--update-library",
            dest    = "update_library",
            type    = bool,
            default = True,
            help    = _("Update header data of the library (default: true)"),
        )
        
        parser.add_argument(
            "-uv", "--update-version",
            dest    = "update_version",
            type    = bool,
            default = True,
            help    = _("Update library version data (default: true)"),
        )
        
        parser.add_argument(
            "-uc", "--update-components",
            dest    = "update_components",
            type    = bool,
            default = True,
            help    = _("Update HTML component definitions (default: true)"),
        )

    def handle(self, *args, **options):
        if os.path.isdir(options["archive_file"]):
            archive_files = glob.glob(os.path.join(options["archive_file"], "*.zip"))
        elif os.path.exists(options["archive_file"]):
            archive_files = [options["archive_file"]]
        else:
            raise CommandError(_f("Path not found: {path}", path=options["archive_file"]))

        for archive_file in archive_files:
            try:
                HTMLLibrary.install_archive(
                    archive_file      = archive_file,
                    extract_archive   = options["extract_archive"],
                    update_library    = options["update_library"],
                    update_version    = options["update_version"],
                    update_components = options["update_components"],
                    verbosity         = options["verbosity"],
                    stdout            = self.stdout,
                )
            except ValidationError as e:
                raise CommandError(e.message) from e
