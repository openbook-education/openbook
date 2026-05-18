# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os, sys, typing

from django.core.exceptions            import ObjectDoesNotExist
from django.core.exceptions            import ValidationError
from django.core.files                 import File
from django.conf                       import settings
from django.contrib.admin              import display
from django.db                         import models
from django.utils.text                 import format_lazy as _f
from django.utils.translation          import gettext_lazy as _

from openbook.auth.models.mixins.audit import CreatedModifiedByMixin
from ..utils.html_library_archive      import HTMLLibraryArchive
from ..validators                      import split_library_fqn
from ..validators                      import split_library_version_fqn
from ..validators                      import validate_library_name_part
from ..validators                      import validate_version_number
from .mixins.file                      import FileUploadMixin
from .mixins.i18n                      import TranslatableMixin
from .mixins.text                      import NameDescriptionMixin
from .mixins.uuid                      import UUIDMixin
from .utils.json                       import PrettyPrintJSONEncoder

class HTMLLibrary(UUIDMixin, CreatedModifiedByMixin):
    """
    Store metadata for an installed HTML library.

    Textbooks are basically static HTML pages that embed the OpenBook JavaScript libraries to render
    custom components (web components). Those web components might in turn communicate with the server
    if necessary, but usually are working stand-alone. For this the distribution bundle needs to be
    loaded via the corresponding `<script>` and `<link rel="stylesheet">` tags.

    To make a library available to the server and especially the WYSIWYG editor, it must be "installed"
    on the server. This includes creating a few database entries (of which this is the main one) and
    placing the bundled library code in the directory `MEDIA_DIR/lib/{organization}/{library}/{version}`.
    """
    organization = models.CharField(verbose_name=_("Organization"), max_length=100, validators=[validate_library_name_part])
    name         = models.CharField(verbose_name=_("Name"), max_length=100, validators=[validate_library_name_part])
    author       = models.CharField(verbose_name=_("Author"), max_length=100, blank=True, default="")
    license      = models.CharField(verbose_name=_("License"), max_length=50, blank=True, default="")
    website      = models.URLField(verbose_name=_("Website"), blank=True, default="")
    coderepo     = models.URLField(verbose_name=_("Code Repository"), blank=True, default="")
    bugtracker   = models.URLField(verbose_name=_("Bug Tracker"), blank=True, default="")
    readme       = models.TextField(verbose_name=_("Read Me"), null=False, blank=True)

    text_format = models.CharField(
        verbose_name = _("Text Format"),
        max_length   = 10,
        choices      = NameDescriptionMixin.TextFormatChoices,
        null         = False,
        blank        = False,
        default      = NameDescriptionMixin.TextFormatChoices.MARKDOWN,
    )

    published = models.BooleanField(
        verbose_name = _("Published"),
        default      = True,
        help_text    = _("Allow other installations to download the library from this server"),
    )

    class Meta:
        verbose_name        = _("HTML Library")
        verbose_name_plural = _("HTML Libraries")
        constraints         = [models.UniqueConstraint(fields=("organization", "name"), name="unique_library_name")]

    def __str__(self):
        return self.fqn()

    @display(description=_("Fully Qualified Name"))
    def fqn(self):
        return f"@{self.organization}/{self.name}"

    @classmethod
    def get_by_fqn(cls, fqn):
        organization, name = split_library_fqn(fqn)
        return cls.objects.get(organization=organization, name=name)

    @classmethod
    def install_archive(cls,
        archive_file:      str|File,
        extract_archive:   bool = True,
        update_library:    bool = True,
        update_version:    bool = True,
        update_components: bool = True,
        library_version:   "HTMLLibraryVersion" = None,
        stdout:            typing.TextIO = sys.stdout,
        verbosity:         int  = 0,
    ):
        """
        Install a new library version from a library archive file.

        Depending on
        the flags, only the archive will be extracted or the database entries will also be updated.
        Missing database entries will then be created, already existing entries will be updated.

        :param archive_file: ``File`` object for the library archive (usually inside ``MEDIA/lib``).
        :param extract_archive: Extract archive file on filesystem.
        :param update_library: Update header data of the library.
        :param update_version: Update library version data.
        :param update_components: Update HTML component definitions.
        :param library_version: Skip database lookup and update this library and version entries instead.
        :param stdout: Output stream for console messages.
        :param verbosity: Print details on the console (default: 0 = off).
        """
        from .language import Language

        if verbosity > 0:
            if isinstance(archive_file, str):
                filename = os.path.basename(archive_file)
            elif hasattr(archive_file, "name"):
                filename = os.path.basename(archive_file.name)
            else:
                filename = str(archive_file)

            line = _f("Installing HTML library file {filename}", filename=filename)

            stdout.write("=" * len(line) + "\n")
            stdout.write(line + "\n")
            stdout.write("=" * len(line) + "\n")
            stdout.write("\n")

        # Validate archive file
        archive = HTMLLibraryArchive(archive_file)

        if not archive.is_valid_archive():
            raise ValidationError(_("The archive file is no valid HTML library archive."))

        if not extract_archive and not update_library and not update_version and not update_components:
            if verbosity > 0:
                stdout.write(_("No action selected. Nothing to do!") + "\n")

            return

        # Extract archive on filesystem
        if extract_archive:
            if verbosity > 0:
                stdout.write(_("Unpacking archive file") + "\n")

            archive.extract(
                install_dir = os.path.join(settings.MEDIA_ROOT, "lib"),
                verbosity   = verbosity,
            )

        # Create or update HTMLLibrary and HTMLLibraryText database entries
        if update_library:
            if verbosity > 0:
                stdout.write(_("Updating library header data") + "\n")

            manifest = archive.get_library_manifest()

            if library_version and library_version.parent:
                library = library_version.parent
            else:
                try:
                    library = HTMLLibrary.objects.get(
                        organization__iexact = manifest.organization,
                        name__iexact         = manifest.name,
                    )
                except HTMLLibrary.DoesNotExist:
                    library = None

            if not library:
                library = HTMLLibrary.objects.create(
                    organization = manifest.organization,
                    name         = manifest.name,
                    author       = manifest.author,
                    license      = manifest.license,
                    website      = manifest.website,
                    coderepo     = manifest.coderepo,
                    bugtracker   = manifest.bugtracker,
                    readme       = manifest.readme,
                )
            else:
                library.organization = manifest.organization
                library.name         = manifest.name
                library.author       = manifest.author
                library.license      = manifest.license
                library.website      = manifest.website
                library.coderepo     = manifest.coderepo
                library.bugtracker   = manifest.bugtracker
                library.readme       = manifest.readme
                library.save()

            if verbosity > 0:
                stdout.write(_("Updating library descriptions") + "\n")

            for language_code in manifest.description.keys():
                if verbosity > 1:
                    stdout.write(f" > {language_code}\n")

                try:
                    language = Language.objects.get(pk=language_code)
                except Language.DoesNotExist:
                    continue

                try:
                    library_text = HTMLLibraryText.objects.get(parent=library, language=language)
                    library_text.short_description = manifest.description[language_code]
                    library_text.save()
                except HTMLLibraryText.DoesNotExist:
                    HTMLLibraryText.objects.create(
                        parent            = library,
                        language          = language,
                        short_description = manifest.description[language_code],
                    )

        # Create or update HTMLLibraryVersion database entry
        if update_version:
            if verbosity > 0:
                stdout.write(_("Updating library version data") + "\n")

            if not library_version:
                if isinstance(archive_file, File):
                    file_data = archive_file
                else:
                    file_data = File(open(archive_file, "rb"), name=os.path.basename(archive_file))

                try:
                    library_version = HTMLLibraryVersion.objects.get(
                        parent          = library,
                        version__iexact = manifest.version,
                    )

                    library_version.dependencies = manifest.dependencies
                    library_version.file_data    = file_data

                    library_version.save()
                except HTMLLibraryVersion.DoesNotExist:
                    library_version = HTMLLibraryVersion.objects.create(
                        parent       = library,
                        version      = manifest.version,
                        dependencies = manifest.dependencies,
                        file_data    = file_data
                    )
                finally:
                    file_data.close()

        # Create or update HTMLComponent and HTMLComponentDefinition database entries
        if update_components:
            if verbosity > 0:
                stdout.write(_("Updating component definitions") + "\n")

            from .html_component import HTMLComponent
            from .html_component import HTMLComponentDefinition

            HTMLComponentDefinition.objects.filter(library_version=library_version).delete()

            for component_manifest in archive.get_html_component_manifests().values():
                if verbosity > 1:
                    stdout.write(f" > {component_manifest.tag_name}\n")

                try:
                    html_component = HTMLComponent.objects.get(
                        library          = library,
                        tag_name__iexact = component_manifest.tag_name,
                    )
                except HTMLComponent.DoesNotExist:
                    html_component = HTMLComponent.objects.create(
                        library  = library,
                        tag_name = component_manifest.tag_name,
                    )

                HTMLComponentDefinition.objects.create(
                    html_component  = html_component,
                    library_version = library_version,
                    definition      = component_manifest.to_dict(),
                )

            # Delete components without definition
            HTMLComponent.objects.filter(
                library             = library,
                definitions__isnull = True,
            ).distinct().delete()

        # Finish
        if verbosity > 0:
            stdout.write("\n")
            stdout.write(_("Done!") + "\n")

class HTMLLibraryText(UUIDMixin, TranslatableMixin):
    parent            = models.ForeignKey(HTMLLibrary, on_delete=models.CASCADE, related_name="translations")
    short_description = models.CharField(verbose_name=_("Short Description"), max_length=255)

    class Meta(TranslatableMixin.Meta):
        verbose_name        = _("HTML Library Text")
        verbose_name_plural = _("HTML Library Texts")

class HTMLLibraryVersion(UUIDMixin, FileUploadMixin, CreatedModifiedByMixin):
    parent       = models.ForeignKey(HTMLLibrary, on_delete=models.CASCADE, related_name="versions")
    version      = models.CharField(verbose_name=_("Version"), max_length=50, validators=[validate_version_number])
    dependencies = models.JSONField(verbose_name=_("Dependencies"), null=True, blank=True, default=None, encoder=PrettyPrintJSONEncoder)

    class Meta:
        verbose_name        = _("HTML Library Version")
        verbose_name_plural = _("HTML Library Versions")
        constraints         = [models.UniqueConstraint(fields=("parent", "version"), name="unique_library_version")]
        ordering            = ["parent", "-version"]

    def __str__(self):
        return f"{self.version}"

    @display(description=_("Fully Qualified Name"))
    def fqn(self):
        return f"{self.parent.fqn()} {self.version}"

    @display(description=_("Frontend URL"))
    def frontend_url(self) -> str:
        return f"{settings.MEDIA_URL}lib/{self.parent.organization}/{self.parent.name}/{self.version}/library.js"

    @classmethod
    def get_by_fqn(cls, fqn) -> "HTMLLibraryVersion":
        organization, name, version = split_library_version_fqn(fqn)
        library = HTMLLibrary.objects.get(organization=organization, name=name)
        return HTMLLibraryVersion.objects.get(parent=library, version=version)

    @classmethod
    def get_by_library_version(cls, library: str, version: str) -> "HTMLLibraryVersion":
        organization, name = split_library_fqn(library)
        library = HTMLLibrary.objects.get(organization=organization, name=name)
        return HTMLLibraryVersion.objects.get(parent=library, version=version)

    def calc_file_path_hook(self, filename):
        return f"lib/@{self.parent.organization}_{self.parent.name}_{self.version}.zip"

    def unpack_archive(
        self,
        extract_archive:   bool = True,
        update_library:    bool = True,
        update_version:    bool = True,
        update_components: bool = True,
        stdout:            typing.TextIO = sys.stdout,
        verbosity:         int  = 0,
    ):
        """
        Unpack the archive uploaded to this HTML library version.

        Optionally use the manifest
        data inside the archive to update the database entries.

        :param extract_archive: Extract archive file on filesystem.
        :param update_library: Update header data of the library.
        :param update_version: Update data of this library version.
        :param update_components: Update HTML component definitions.
        :param stdout: Output stream for console messages.
        :param verbosity: Print details on the console (default: 0 = off).
        :raises ObjectDoesNotExist: No archive file attached to this entry.
        """
        if not self.file_data:
            raise ObjectDoesNotExist(_("Archive for HTML library version not found."))

        self.parent.install_archive(
            archive_file      = self.file_data,
            extract_archive   = extract_archive,
            update_library    = update_library,
            update_version    = update_version,
            update_components = update_components,
            library_version   = self,
            stdout            = stdout,
            verbosity         = verbosity,
        )
