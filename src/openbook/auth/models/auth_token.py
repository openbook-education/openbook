# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import random, string

from django.contrib.auth.models           import AbstractUser
from django.db                            import models
from django.utils.translation             import gettext_lazy as _

from openbook.core.models.mixins.active   import ActiveInactiveMixin
from openbook.core.models.mixins.datetime import ValidityTimeSpanMixin
from openbook.core.models.mixins.uuid     import UUIDMixin
from openbook.core.models.mixins.text     import NameDescriptionMixin
from .mixins.audit                        import CreatedModifiedByMixin
from .user                                import User

ALLOWED_CHARACTERS = string.digits + string.ascii_letters + string.punctuation

def generate_token(length: int = 64):
    """
    Generate a new random token string.
    """
    return ''.join(random.choices(ALLOWED_CHARACTERS, k=length))

class AuthToken(UUIDMixin, NameDescriptionMixin, ActiveInactiveMixin, ValidityTimeSpanMixin, CreatedModifiedByMixin):
    """
    Store authentication tokens that remote clients can use for API authentication.

    This allows clients to impersonate the user account associated with the token,
    which can be used in two ways:

    1. As the sole authentication method for app users (technical users).
    2. To authenticate as a human user, instead of a full OAuth resource sharing flow.

    Token life-time can be manually managed by the users.
    """
    user  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auth_tokens")
    token = models.CharField(_("Token"), max_length=64, unique=True, default=generate_token)

    class Meta:
        verbose_name        = _("Authentication Token")
        verbose_name_plural = _("Authentication Tokens")
        permissions         = (("manage_own_authtoken", "Can mange own authentication tokens"),)

        indexes = [
            models.Index(fields=("user",)),
            models.Index(fields=("token",)),
        ]

    def __str__(self):
        if self.name:
            return f"{self.user}: {self.name}"
        else:
            return str(self.user)

    def has_obj_perm(self, user_obj: AbstractUser, perm: str) -> bool:
        """
        Allow users to manage only their own access key when they have ``openbook_auth.manage_own_authtoken``.

        The permission can be assigned directly to the user or via user groups,
        since we do not have an RBAC scope here.

        Note: Users must have the special permission ``openbook_auth.manage_own_authtoken`` in order to manage
        their own tokens. Because assigning the Django default permissions (add, change, delete, view)
        would allow them to manage all tokens of all users (due to the fallback logic in our auth backend).
        """
        if not self.user:
            return False

        return self.user.username == user_obj.username and user_obj.has_perm("openbook_auth.manage_own_authtoken")
