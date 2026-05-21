# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os, shutil, sys, typing

from django.core.exceptions import ValidationError
from django.utils.text      import format_lazy as _f
from yaml                   import safe_load as yaml_safe_load
from zipfile                import is_zipfile
from zipfile                import ZipFile

from ..validators           import split_library_fqn
from ..validators           import validate_library_name_part
from ..validators           import validate_version_number

class HTMLLibraryArchive:
    """
    Low-level class to work with HTML library archives. Supports checking, if
    an archive is valid, reading its content and extracting it.
    """
    def __init__(self, file: str|typing.BinaryIO, mode: str = "r", **zipfile_kwargs):
        """
        Open a HTML library archive given either a filename of file-object.

        Note that currently only read operations are supported, as it is
        assumed that the archives are built with external tools.

        :param file: File name or file-like object.
        :param mode: Access mode to open the file (default = ``"r"``).
        :param zipfile_kwargs: Additional keyword arguments for the
            ``ZipFile`` constructor.
        """
        if is_zipfile(file):
            self._zip_file = ZipFile(file, mode, **zipfile_kwargs)

            try:
                with self._zip_file.open("openbook-library/library.yml") as manifest_file:
                    manifest_data = yaml_safe_load(manifest_file)
            except KeyError:
                manifest_data = None

            if isinstance(manifest_data, dict):
                self._manifest = HTMLLibraryManifest.from_dict(manifest_data)
        else:
            self._zip_file = None
            self._manifest = HTMLLibraryManifest()

    def close(self):
        """
        Close the archive file when it is not needed anymore.

        This method should always be called
        when done with the archive.
        """
        if self._zip_file:
            self._zip_file.close()

    def is_valid_archive(self):
        """
        Return ``True`` if the archive is a valid HTML library archive.

        This is the case if it is a ZIP file, containing a single directory with
        the name ``openbook-library``, which in turn contains a ``library.yml``
        file with at least the following content
        with a valid library name and semver version:

        ::

            name: "@organization/name"
            version: 1.0.0
        """
        if not self._zip_file:
            return False

        if not self._manifest.organization or not self._manifest.name or not self._manifest.version:
            return False

        try:
            validate_library_name_part(self._manifest.organization)
            validate_library_name_part(self._manifest.name)
            validate_version_number(self._manifest.version)
        except ValidationError:
            return False

        return True

    def get_library_manifest(self) -> "HTMLLibraryManifest":
        """
        Return a Python object with the parsed content of the library manifest file.

        Return ``None`` when the archive is no ZIP file or lacks the library manifest.
        """
        return self._manifest

    def get_html_component_manifests(self) -> dict[str, "HTMLComponentManifest"]:
        """
        Return a dictionary that maps HTML tag names to Python objects.

        The objects describe the HTML custom components. Return ``None`` when
        the archive is no ZIP file.
        """
        if not self._zip_file:
            return None

        result = {}

        for filename in self._zip_file.namelist():
            if filename.startswith("openbook-library/components/") and filename.endswith(".yml"):
                with self._zip_file.open(filename) as manifest_file:
                    manifest_data = yaml_safe_load(manifest_file)

                manifest = HTMLComponentManifest.from_dict(manifest_data)

                if manifest.tag_name:
                    result[manifest.tag_name] = manifest

        return result

    def get_raw_zip_file(self) -> ZipFile:
        """
        Return the raw ``ZipFile`` object so that its content can be inspected.

        Return ``None`` if the file is no valid ZIP file.
        """
        return self._zip_file

    def extract(
        self,
        install_dir: str,
        stdout:      typing.TextIO = sys.stdout,
        verbosity:   int = 0,
    ):
        """
        Extract archive content into the given installation directory.

        The directory should be the root directory where all libraries are
        installed, because this method will create the corresponding
        sub-directories for the library and its version. If a sub-directory for
        the same version of the same library already exists it will be deleted
        first.

        Note, no validation of the archive is done here. It is assumed that the client already
        called ``is_valid_archive()`` or wants to force-extract a possibly invalid archive.

        Does nothing if the archive is no ZIP file.

        :param install_dir: Root directory where libraries are installed.
        :param stdout: Output stream for console messages.
        :param verbosity: Print details on the console (default: 0 = off).
        """
        if not self._zip_file:
            return

        if not self._manifest.organization or not self._manifest.name or not self._manifest.version:
            return

        library_dir = os.path.join(install_dir, self._manifest.organization, self._manifest.name, self._manifest.version)

        if verbosity > 0:
            stdout.write(_f("Extracting to {library_dir}", library_dir=library_dir) + "\n")

        if os.path.exists(library_dir):
            shutil.rmtree(library_dir)

        os.makedirs(library_dir)

        root_dirname = "openbook-library/"

        for zipped_file in self._zip_file.infolist():
            if not zipped_file.filename.startswith(root_dirname) or zipped_file.is_dir():
                continue

            file_path = zipped_file.filename[len(root_dirname):].replace("/", os.path.sep)
            file_path = os.path.join(library_dir, file_path)

            if verbosity > 1:
                stdout.write(f" > {file_path}\n")

            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "bw") as extracted_file:
                extracted_file.write(self._zip_file.read(zipped_file.filename))

T = typing.TypeVar("T")

class TypedAccessDict(dict):
    """
    Specialized dictionary that can apply runtime type checking when accessing
    its content. This is used for parsing the manifest files of a HTML library
    archive to make sure that values with unexpected types will be skipped.

    Nested dictionaries will automatically converted into typed dictionaries,
    to allow type-checking their content, too. Still the expected type must
    be given as ``dict``.
    """
    def __init__(self, data: any):
        """
        Initialize typed dictionary from untyped dictionary.

        If ``data`` is no ``dict``
        the initialized dictionary will be empty.
        """
        if not isinstance(data, dict):
            data = {}

        super().__init__(data)

    def get_typed(self, key: str, expected_type: typing.Type[T], default_value: any = None) -> T|None:
        """
        Dictionary access with type checking.

        :param key: Key name.
        :param expected_type: Type to be checked with ``isinstance()``.
        :param default_value: Default value if key is missing or value has wrong type.
        """
        value = self.get(key, default_value)

        if expected_type == dict:
            return TypedAccessDict(value) if isinstance(value, expected_type) else default_value
        else:
            return value if isinstance(value, expected_type) else default_value

    def get_string_list(self, key: str) -> list[str]:
        """
        Access a list of strings in the dictionary with runtime type-checking.
        """
        return [e for e in self.get_typed(key, list, []) if isinstance(e, str)]

    def get_string_dict(self, key: str) -> dict[str, str]:
        """
        Access a raw dictionary whose keys and values are both strings.
        """
        return {k: v for k, v in self.get_typed(key, dict, {}).items() if isinstance(k, str) and isinstance(v, str)}

class HTMLLibraryManifest:
    """
    Content of the ``library.yml`` file that describes the library as a whole.
    """
    def __init__(
        self,
        organization: str            = "",
        name:         str            = "",
        version:      str            = "",
        author:       str            = "",
        license:      str            = "",
        website:      str            = "",
        coderepo:     str            = "",
        bugtracker:   str            = "",
        description:  dict[str, str] = {},
        readme:       str            = "",
        dependencies: dict[str, str] = {},
    ):
        """
        :param organization: Organization from the fully qualified library name.
        :param name: Library name from the fully qualified library name.
        :param version: Library version.
        :param author: Author name and e-mail.
        :param license: License short-code.
        :param website: Website URL.
        :param coderepo: Source code URL.
        :param bugtracker: Bug tracker URL.
        :param description: Short description in multiple languages
            (key = language, value = description).
        :param readme: Content of the README file, assumed to be in markdown format.
        :param dependencies: Dependencies on other libraries
            (key = library, value = version expression).
        """
        self.organization = organization
        self.name         = name
        self.version      = version
        self.author       = author
        self.license      = license
        self.website      = website
        self.coderepo     = coderepo
        self.bugtracker   = bugtracker
        self.description  = description
        self.readme       = readme
        self.dependencies = dependencies

    @classmethod
    def from_dict(cls, manifest_data: dict) -> "HTMLLibraryManifest":
        """
        Create new instance from a dictionary in the YAML manifest file.
        """
        manifest_data = TypedAccessDict(manifest_data)

        library_fqn = manifest_data.get_typed("name", str, "")
        organization, name = split_library_fqn(library_fqn)

        return cls(
            organization = organization,
            name         = name,
            version      = manifest_data.get_typed("version",     str, ""),
            author       = manifest_data.get_typed("author",      str, ""),
            license      = manifest_data.get_typed("license",     str, ""),
            website      = manifest_data.get_typed("website",     str, ""),
            coderepo     = manifest_data.get_typed("coderepo",    str, ""),
            bugtracker   = manifest_data.get_typed("bugtracker",  str, ""),
            readme       = manifest_data.get_typed("readme",      str, ""),
            description  = manifest_data.get_string_dict("description"),
            dependencies = manifest_data.get_string_dict("dependencies"),
        )

class HTMLComponentManifest:
    """
    Content of a component YAML file describing a single HTML custom component.
    """
    def __init__(
        self,
        tag_name:         str                                   = "",
        description:      dict[str, str]                        = {},
        text_allowed:     bool                                  = False,
        html_allowed:     bool                                  = False,
        allowed_children: list[str]                             = [],
        attributes:       dict[str, "HTMLAttributeDescription"] = {},
        events:           list[str]                             = [],
    ):
        """
        :param tag_name: HTML tag name.
        :param description: Short description in multiple languages
            (key = language, value = description).
        :param text_allowed: Whether the element may contain text content.
        :param html_allowed: Whether normal HTML child nodes are allowed.
        :param allowed_children: Names of the allowed HTML children, if
            ``htmlAllowed`` is ``False``.
        :param attributes: HTML attributes and their allowed values.
        :param events: DOM events raised by the component.
        """
        self.tag_name         = tag_name
        self.description      = description
        self.text_allowed     = text_allowed
        self.html_allowed     = html_allowed
        self.allowed_children = allowed_children
        self.attributes       = attributes
        self.events           = events

    @classmethod
    def from_dict(cls, manifest_data: dict) -> "HTMLComponentManifest":
        """
        Create new instance from a dictionary in the YAML manifest file.
        """
        manifest_data = TypedAccessDict(manifest_data)

        def attribute_dict(key: str) -> dict[str, HTMLAttributeDescription]:
            attributes = manifest_data.get_typed(key, dict, {})
            result = {}

            for attribute_name in attributes.keys():
                attribute_data = attributes.get_typed(attribute_name, dict, {})
                result[attribute_name] = HTMLAttributeDescription.from_dict(attribute_name, attribute_data)

            return result

        return cls(
            tag_name         = manifest_data.get_typed("tag-name",     str,  ""),
            text_allowed     = manifest_data.get_typed("text-allowed", bool, False),
            html_allowed     = manifest_data.get_typed("html-allowed", bool, False),
            description      = manifest_data.get_string_dict("description"),
            allowed_children = manifest_data.get_string_list("allowed-children"),
            events           = manifest_data.get_string_list("events"),
            attributes       = attribute_dict("attributes"),
        )

    def to_dict(self):
        attributes = {}

        for attribute_name in self.attributes.keys():
            attributes[attribute_name] = self.attributes[attribute_name].to_dict()

        return {
            "tag-name":         self.tag_name,
            "description":      self.description,
            "text-allowed":     self.text_allowed,
            "html-allowed":     self.html_allowed,
            "allowed-children": self.allowed_children,
            "attributes":       attributes,
            "events":           self.events,
        }

class HTMLAttributeDescription:
    """
    Description of a HTML attribute.
    """
    def __init__(
        self,
        name:        str            = "",
        description: dict[str, str] = {},
        regex:       str            = "",
        enum:        list[str]      = [],
    ):
        """
        :param name: HTML attribute name.
        :param description: Short description in multiple languages
            (key = language, value = description).
        :param regex: Optional regular expression to check property values.
        :param enum: Optional enumerated list of allowed property values.
        """
        self.name        = name
        self.description = description
        self.regex       = regex
        self.enum        = enum

    @classmethod
    def from_dict(cls, attribute_name: str, attribute_data: TypedAccessDict) -> "HTMLAttributeDescription":
        return cls(
            name        = attribute_name,
            description = attribute_data.get_string_dict("description"),
            regex       = attribute_data.get_typed("regex", str, ""),
            enum        = attribute_data.get_string_list("enum")
        )

    def to_dict(self) -> dict:
        return {
            "name":        self.name,
            "description": self.description,
            "regex":       self.regex,
            "enum":        self.enum,
        }
