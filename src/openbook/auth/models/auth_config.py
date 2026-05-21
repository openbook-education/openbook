# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.conf                      import settings
from django.db                        import models
from django.utils.translation         import gettext_lazy as _

from openbook.core.models.mixins.i18n import TranslatableMixin
from openbook.core.models.mixins.uuid import UUIDMixin
from openbook.core.models.site        import Site
from openbook.core.models.utils.file  import calc_file_path

class AuthConfig(models.Model):
    """
    Store authentication-related configuration for the site.
    """
    def _calc_file_path(self, filename):
        return calc_file_path(self._meta, self.site.id, filename)

    site = models.OneToOneField(
        to           =  Site,
        verbose_name = _("Site"),
        primary_key  = True,
        on_delete    = models.CASCADE,
        related_name = "auth_config",
    )

    local_signup_allowed = models.BooleanField(
        verbose_name = _("Local Sign-Up Allowed"),
        default      = True,
        help_text    = _("This only affects registration of local users without social authentication or federated identities."),
    )

    signup_email_suffix = models.CharField(
        verbose_name = _("E-Mail Suffix"),
        blank        = True,
        null         = False,
        help_text    = _("This limits local user registration to e-mail addresses ending with a given suffix."),
    )

    logout_next_url = models.CharField(
        verbose_name = _("Next URL after logout"),
        default      = "/",
        blank        = False,
        null         = False,
        help_text    = _("Link on the confirmation page shown after logout."),
    )

    signup_image         = models.FileField(verbose_name=_("Sign-Up Page Image"), upload_to=_calc_file_path, null=True, blank=True)
    login_image          = models.FileField(verbose_name=_("Login Page Image"), upload_to=_calc_file_path, null=True, blank=True)
    logout_image         = models.FileField(verbose_name=_("Logout Page Image"), upload_to=_calc_file_path, null=True, blank=True)
    password_reset_image = models.FileField(verbose_name=_("Password Reset Page Image"), upload_to=_calc_file_path, null=True, blank=True)

    class Meta:
        verbose_name        = _("Authentication Settings")
        verbose_name_plural = _("Authentication Settings")

    def __str__(self):
        return self.site.__str__() if self.site else "---"

    @classmethod
    def get_for_default_site(cls) -> "AuthConfig":
        """
        Return authorization configuration for the default site defined in the ``SITE_ID`` setting.

        Raise ``AuthConfig.DoesNotExist`` if no configuration is found.
        """
        return cls.objects.get(site=settings.SITE_ID)

class AuthConfigText(UUIDMixin, TranslatableMixin):
    parent           = models.ForeignKey(AuthConfig, on_delete=models.CASCADE, related_name="translations")
    logout_next_text = models.CharField(verbose_name=_("Link Text after Logout"), max_length=255, null=False, blank=False)

    class Meta(TranslatableMixin.Meta):
        verbose_name        = _("Authentication Settings: Translation")
        verbose_name_plural = _("Authentication Settings: Translations")

        constraints = (
            models.UniqueConstraint(fields=("parent", "language"), name="unique_auth_config_translation"),
        )
