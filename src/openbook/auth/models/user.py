# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.contrib.auth.models      import AbstractUser
from django.core.validators          import EmailValidator
from django.db                       import models
from django.utils.translation        import gettext_lazy as _
from unfold.decorators               import display
from openbook.core.models.utils.file import calc_file_path

class User(AbstractUser):
    """
    Extend Django's core user model to distinguish user types and add profile fields.
    """
    class UserType(models.TextChoices):
        HUMAN = "human",  _("Human User")
        APP   = "app",    _("App User")

    def _calc_file_path(self, filename):
        return calc_file_path(self._meta, self.username, filename)

    user_type   = models.CharField(verbose_name=_("User Type"), choices=UserType, default=UserType.HUMAN)
    email       = models.EmailField(_("E-Mail Address"), blank=False, null=False, validators=[EmailValidator])
    description = models.TextField(verbose_name=_("Description"), blank=True, null=False)
    picture     = models.FileField(verbose_name=_("Profile Picture"), upload_to=_calc_file_path, null=True, blank=True)

    groups = models.ManyToManyField(
        "openbook_auth.Group",
        verbose_name       = _("Groups"),
        blank              = True,
        help_text          = _("The groups this user belongs to. A user will get all permissions granted to each of their groups."),
        related_name       = "user_set",
        related_query_name = "user",
    )

    @display(header=True, description=_("Full Name"))
    def full_name(self, obj=None):
        """
        Return name, e-mail, and profile picture.

        Note that Django Unfold only supports this in the changelist, not on the detail page.
        """
        if self.first_name and self.last_name:
            initials = f"{self.first_name[0]}{self.last_name[0]}"
        elif self.first_name:
            initials = self.first_name.zfill(2)[:2].strip()
        elif self.last_name:
            initials = self.last_name.zfill(2)[:2].strip()
        else:
            initials = self.username.zfill(2)[:2].strip()

        return (
            self.get_full_name(),
            self.email,
            initials.upper(),
            {
                "path":       self.picture.url if self.picture else "",
                "borderless": True,
                "squared":    True,
            }
        )

    def has_obj_perm(self, user_obj: AbstractUser, perm: str) -> bool:
        """
        Allow users to update and delete their account.
        """
        return self.username == user_obj.username
