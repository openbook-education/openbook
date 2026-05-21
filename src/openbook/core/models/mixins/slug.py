# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.db                  import models
from django.utils.translation   import gettext_lazy as _

class NonUniqueSlugMixin(models.Model):
    """
    Provide a mixin for models with a non-unique slug field.

    This is usually used if the slug itself cannot be unique but must be unique in
    combination with other fields. In that case, the child class can define a
    constraint like so::

        class MyModel(models.Model, NonUniqueSlugMixin):
            ...
            class Meta:
                constraints = (
                    models.UniqueConstraint(fields=("course", "slug"), name="unique_course_slug"),
                )
    """
    slug = models.SlugField(verbose_name=_("Slug"), unique=False, null=False, blank=False)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

class UniqueSlugMixin(models.Model):
    """
    Provide a mixin for models with a unique slug field.
    """
    slug = models.SlugField(verbose_name=_("Slug"), unique=True, null=False, blank=False)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
