# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from allauth.account.adapter          import DefaultAccountAdapter
from allauth.socialaccount.adapter    import DefaultSocialAccountAdapter
from allauth.socialaccount.models     import SocialApp
from allauth.socialaccount.models     import SocialLogin
from django.contrib.auth.models       import AbstractUser
from django.core.exceptions           import ValidationError
from django.db.models                 import Q
from django.http                      import HttpRequest
from django.utils.text                import format_lazy as _f

from openbook.core.models.site        import Site
from ..models.auth_config             import AuthConfig
from ..models.signup_group_assignment import SignupGroupAssignment

class AccountAdapter(DefaultAccountAdapter):
    """
    Adapted behavior for local account registration.
    """
    def is_open_for_signup(self, request: HttpRequest):
        """
        Check whether local account registration is allowed.
        """
        try:
            auth_config = AuthConfig.get_for_default_site()
            return auth_config.local_signup_allowed
        except AuthConfig.DoesNotExist:
            pass
        
        return True

    def clean_email(self, email: str) -> str:
        """
        Restrict local account e-mail to e-mails with a certain suffix.
        """
        try:
            auth_config  = AuthConfig.get_for_default_site()
            email_suffix = auth_config.signup_email_suffix.strip()

            if not email.endswith(email_suffix):
                raise ValidationError(_f("This e-mail is not allowed to sign-up. The e-mail must end with {suffix}", suffix=email_suffix))
        except AuthConfig.DoesNotExist:
            pass
        
        return email
    
    def save_user(self, request: HttpRequest, user: AbstractUser, form, commit=True) -> AbstractUser:
        """
        Add user to groups after sign-up.
        """
        saved_user = super().save_user(request, user, form, commit)
        groups = []

        try:
            current_site = Site.objects.get(site_ptr=request.site)
        except Site.DoesNotExist:
            current_site = None

        group_assignments = SignupGroupAssignment.objects.filter(
            Q(is_active = True),
            Q(social_app = None),
            Q(site = None) | Q(site = current_site),
        )

        for group_assignment in group_assignments.all():
            for group in group_assignment.groups.all():
                groups.append(group)
        
        saved_user.groups.set(groups)
        return saved_user

    def authenticate(self, request, **credentials):
        """
        Only allow human users to authenticate. App users need to authenticate with an
        authentication token, instead. This is an extra security measure, since normally
        app users should not have a passwort set and thus should not be able to login
        with username/password, anyway.
        """
        user = super().authenticate(request, **credentials)

        if not user:
            return user
        
        if hasattr(user, "user_type") and not user.user_type == user.UserType.HUMAN:
            # Cannot raise exception here
            return None

        return user

class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Adapted behavior for social account registration.
    """
    def save_user(self, request: HttpRequest, sociallogin: SocialLogin, form=None) -> AbstractUser:
        """
        Add user to groups after sign-up.
        """
        saved_user = super().save_user(request, sociallogin, form)
        social_app = None
        groups = []

        try:
            social_app = SocialApp.objects.get(provider_id = sociallogin.account.provider)
        except SocialApp.DoesNotExist:
            pass
    
        if not social_app:
            try:
                social_app = SocialApp.objects.get(provider = sociallogin.account.provider)
            except SocialApp.DoesNotExist:
                pass

        if social_app:
            try:
                current_site = Site.objects.get(site_ptr=request.site)
            except Site.DoesNotExist:
                current_site = None

            group_assignments = SignupGroupAssignment.objects.filter(
                Q(is_active = True),
                Q(social_app = social_app),
                Q(site = None) | Q(site = current_site),
            )

            for group_assignment in group_assignments.all():
                if group_assignment.match(sociallogin.account.extra_data):
                    for group in group_assignment.groups.all():
                        groups.append(group)
                    
                    if group_assignment.is_staff:
                        saved_user.is_staff = True
                    
                    if group_assignment.is_superuser:
                        saved_user.is_superuser = True
            
            saved_user.save()
            saved_user.groups.set(groups)

        return saved_user