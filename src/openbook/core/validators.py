# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

import semver

from django.core.exceptions   import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from PIL                      import Image

@deconstructible
class ValidateImage:
    """
    Validate image uploads against the allowed maximum file size.
    """
    def __init__(self, max_size=1024*1024):
        self.max_size = max_size

    def __call__(self, value):
        try:
            image = Image.open(value)
            image.verify()
            image.close()
        except IOError:
            raise ValidationError(_("Invalid image file"))

        if value.size > self.max_size:
            max_size_mb = self.max_size / (1024*1024)
            raise ValidationError(_("Image file too large (max %(max_size_mb).2fMB)"), params={"max_size_mb": max_size_mb})

def validate_library_name_part(part: str) -> None:
    """
    Validate a library name part.

    Each part of a library name must be alpha-numeric and at least three
    characters long.
    """
    if len(part) < 3 \
    or not all(c.isalnum() \
    or c in ('.', '_', '-') for c in part) \
    or not part.islower():
        raise ValidationError(_("Expected alpha-numeric name with at least three letters"))

def validate_version_number(version: str) -> None:
    """
    Validate a semantic version number.

    Version numbers use semver with numeric major, minor, patch and optional
    ``-prerelease`` and ``+build`` tags.
    """
    if not semver.Version.is_valid(version):
        raise ValidationError(_("The version must be in semver format with optional -prerelease and +build tags."))

def validate_version_expression(version_expression: str) -> None:
    """
    Validate a semantic version expression.

    The expression contains a valid semver, optionally with one of the
    following operators supported by the ``semver`` package:

    * ``<``: smaller than
    * ``>``: greater than
    * ``<=``: smaller or equal than
    * ``>=``: greater or equal than
    * ``==``: equal
    * ``!=``: not equal

    See https://python-semver.readthedocs.io/en/latest/usage/compare-versions-through-expression.html.
    """
    if not version_expression:
        return

    # Order is important: One-letter operators must come last!
    operators = ["<=", ">=", "==", "!=", "<", ">"]

    for operator in operators:
        if version_expression.startswith(operator):
            validate_version_number(version_expression[len(operator):])
            return

    validate_version_number(version_expression)

def validate_library_fqn(fqn: str) -> None:
    """
    Validate a fully qualified library name.

    The fully qualified name of a library roughly follows the same guidelines
    as for Node.js packages in npmjs.org: ``@organization/package``. Each part
    is at least three characters long and may only contain alpha-numerics,
    underline, minus, or dot.

    Unlike on npmjs.org, the organization is mandatory for us.
    """
    if not fqn.startswith("@") or not "/" in fqn:
        raise ValidationError(_("Expected format: @organization/package with each part alpha-numeric and at least three letters"))

    org, lib = fqn.split("/", 1)
    org = org[1:]

    validate_library_name_part(org)
    validate_library_name_part(lib)

def validate_library_version_fqn(fqn: str) -> None:
    """
    Validate a fully qualified library version.

    Expected format: ``@organization/library 1.0.0``.
    """
    if not " " in fqn:
        raise ValidationError(_("Library name and version expected"))

    library_fqn, version = fqn.split(" ", 1)
    validate_library_fqn(library_fqn)
    validate_version_number(version)

def split_library_fqn(fqn: str) -> tuple[str, str]:
    """
    Split a fully qualified library name into organization and library name.

    The organization is returned without ``@``.

    :param fqn: Fully qualified library name.
    :returns: A tuple with organization and library name.
    :raises ValidationError: If the input string does not match the expected format.
    """
    validate_library_fqn(fqn)
    organization, name = fqn.split("/", 1)
    return (organization[1:], name)

def split_library_version_fqn(fqn: str) -> tuple[str, str, str]:
    """
    Split a fully qualified library version into organization, library, and version.

    The organization is returned without ``@``.

    :param fqn: Fully qualified library version.
    :returns: A tuple with organization, library name, and version.
    :raises ValidationError: If the input string does not match the expected format.
    """
    validate_library_version_fqn(fqn)

    library_fqn, version = fqn.split(" ", 1)
    validate_library_fqn(library_fqn)
    validate_version_number(version)

    organization, name = split_library_fqn(library_fqn)
    return (organization, name, version)
