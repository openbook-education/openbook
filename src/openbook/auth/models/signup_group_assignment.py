# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import re

from allauth.socialaccount.models       import SocialApp
from django.db                          import models
from django.utils.translation           import gettext_lazy as _

from openbook.core.models.mixins.active import ActiveInactiveMixin
from openbook.core.models.mixins.uuid   import UUIDMixin
from openbook.core.models.mixins.text   import NameDescriptionMixin
from openbook.core.models.site          import Site

class SignupGroupAssignment(UUIDMixin, ActiveInactiveMixin, NameDescriptionMixin):
    """
    Automatic user group assignment after sign-up. For local accounts and most social providers,
    all new users are added to the same user groups. For SAML it is possible to assign different
    groups based on the assertions returned by the IdP.
    """
    site = models.ForeignKey(
        to           =  Site,
        on_delete    = models.CASCADE,
        related_name = "+",
        null         = True,
        blank        = True,
        help_text    = _("Leave blank for all sites."),
    )

    social_app = models.ForeignKey(
        to           = SocialApp,
        on_delete    = models.CASCADE,
        related_name = "+",
        null         = True,
        blank        = True,
        help_text    = _("Leave blank for local accounts."),
    )

    groups = models.ManyToManyField(
        to           = "openbook_auth.group",
        related_name = "+",
        blank        = True,
    )

    is_staff = models.BooleanField(
        verbose_name = _("staff status"),   # Django name is lower-case
        default      = False,
        help_text    = _("BE CAREFUL: Allows the user to login to the admin site!"),
    )

    is_superuser = models.BooleanField(
        verbose_name = _("superuser status"),   # Django name is lower-case
        default      = False,
        help_text    = _("BE CAREFUL: Makes the user have all permissions without explicitly assigning them!"),
    )

    class Meta:
        verbose_name        = _("Group Assignment on Signup")
        verbose_name_plural = _("Group Assignments on Signup")

    def __str__(self):
        return self.name if self.name else "---"

    def match(self, extra_data: dict|list[dict]) -> bool:
        """
        Check if the given extra data from the social account entry matches all scopes/assertions.
        """
        for assertion in self.assertions.all():
            if not assertion.match(extra_data):
                return False
        
        return True
    
class SecurityAssertion(UUIDMixin):
    """
    OAuth Scope or SAML Assertion to be checked after sign-up for automatic user
    group assignment.
    """
    class MatchStrategy(models.TextChoices):
        EXACT       = "exact",       _("Exact Match"),
        CONTAINS    = "contains",    _("Contains"),
        STARTS_WITH = "starts-with", _("Starts With"),
        ENDS_WITH   = "ends-with",   _("Ends With")
        REGEX       = "regex",       _("Regular Expression"),
        ANY         = "any",         _("Any Value"),

    parent = models.ForeignKey(
        to           =  SignupGroupAssignment,
        on_delete    = models.CASCADE,
        related_name = "assertions",
        null         = False,
        blank        = False,
    )

    name = models.CharField(
        max_length   = 255,
        verbose_name = _("Name"),
        help_text    = _("Name of the scope or assertion"),
        blank        = False,
        null         = False,
    )

    value = models.CharField(
        max_length   = 255,
        verbose_name = _("Value"),
        help_text    = _("Value of the assertion"),
        blank        = True,
        null         = True,
    )

    match_strategy = models.CharField(
        verbose_name = _("Match Strategy"),
        choices      = MatchStrategy,
        default      = MatchStrategy.EXACT,
    )

    class Meta:
        verbose_name        = _("Identity Assertion")
        verbose_name_plural = _("Identity Assertions")

    def __str__(self):
        return f"{self.name or ""} {self.match_strategy or ""} {self.value or ""}".strip()

    def match(self, extra_data: dict|list[dict]) -> bool:
        """
        Check if the given extra data from the social account entry matches the scope or assertion.
        """
        def _match_value(value) -> bool:
            value = str(value)

            if self.match_strategy == self.MatchStrategy.EXACT:
                return value == self.value
            elif self.match_strategy == self.MatchStrategy.CONTAINS:
                return self.value in value
            elif self.match_strategy == self.MatchStrategy.STARTS_WITH:
                return value.startswith(self.value)
            elif self.match_strategy == self.MatchStrategy.ENDS_WITH:
                return value.endswith(self.value)
            elif self.match_strategy == self.MatchStrategy.REGEX:
                pattern = re.compile(self.value)
                return bool(pattern.match(value))
            elif self.match_strategy == self.MatchStrategy.ANY:
                return True
            else:
                return False

        def _match_dict(data: dict) -> bool:
            if self.name not in data:
                return False
            
            value = data[self.name]

            if isinstance(value, list):
                for child_value in value:
                    if _match_value(child_value):
                        return True    
                    
                return False
            else:
                return _match_value(value)
            
        if isinstance(extra_data, list):
            for child_data in extra_data:
                if _match_dict(child_data):
                    return True
                
            return False
        else:
            return _match_dict(extra_data)