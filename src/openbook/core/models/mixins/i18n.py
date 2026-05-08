# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from typing                     import Optional
from django.conf                import settings
from django.db                  import models
from django.db.models           import Q
from django.utils.translation   import gettext_lazy as _, get_language

def LanguageField():
    """
    Return a special model field for language codes.

    Technically this is a simple foreign key to the ``Language`` model of the core app.
    """
    return models.ForeignKey("openbook_core.Language", on_delete=models.CASCADE)

class TranslatableMixin(models.Model):
    """
    Provide a mixin for translation models with translated texts for a parent model.

    Given a model named ``Example``, translations can be added like this::

        class Example_T(models.Model, TranslatableMixin):
            parent = models.ForeignKey(Example, on_delete=models.CASCADE, related_name="translations")

            text1  = models.CharField(verbose_name=_("Some Text 1"), max_length=255, null=False, blank=False)
            text2  = models.CharField(verbose_name=_("Some Text 2"), max_length=255, null=False, blank=False)
            text3  = models.CharField(verbose_name=_("Some Text 3"), max_length=255, null=False, blank=False)

            class Meta(TranslatableMixin.Meta):
                verbose_name        = _("My Model: Translation")
                verbose_name_plural = _("My Model: Translations")

    The translation model simply needs a foreign key to the parent model (usually called
    ``parent`` with related name ``translations``) and char fields for the translatable texts.

    This class can be combined with the ``UUIDMixin``, if the parent class used it, too.
    """
    language = LanguageField()

    class Meta:
        abstract = True
        ordering = ("parent", "language")
        indexes  = (models.Index(fields=("parent", "language")),)

    def __str__(self):
        return self.language.name

def get_translations(object: models.Model, language: str = "",
                     attr_id: str = "id", attr_translations: str = "translations",
                     attr_t_parent: str = "parent", attr_t_language: str = "language") -> Optional[models.Model]:
    """
    Get translations of a model with translations.

    By default translations are stored in a second model, that installs a
    ``translations`` (``attr_translations``) related attribute. The text model usually
    has the properties ``parent`` (``attr_t_parent``) pointing to the original model and
    ``language`` (``attr_t_language``) with the language code.

    Tries to find translations for the given language (default: language of the current thread)
    or the ``LANGUAGE_CODE`` setting as fallback, if different.

    :returns: The best found translation or ``None``, if none exists.
    """
    if not language:
        language = get_language()

    id = getattr(object, attr_id)

    default_language = settings.LANGUAGE_CODE or ""
    default_kwargs   = {attr_t_parent: id, attr_t_language: default_language}
    language_kwargs  = {attr_t_parent: id, attr_t_language: language}

    translations = getattr(object, attr_translations)

    if default_kwargs == language_kwargs:
        results = translations.filter(**language_kwargs);
    else:
        results = translations.filter(Q(**language_kwargs) | Q(**default_kwargs))

    if results.count() == 0:
        return None
    elif results.count() == 1:
        return results.first()
    else:
        return results.get(**language_kwargs)

class TranslationMissing(Exception):
    """
    Signal that a translation for something is missing.

    Note that the ``get_translations()`` function does not throw this exception but
    rather returns ``None``.
    """
    pass
