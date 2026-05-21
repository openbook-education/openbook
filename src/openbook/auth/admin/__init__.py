# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from openbook.admin           import admin_site
from .access_request          import AccessRequestAdmin
from .allowed_role_permission import AllowedRolePermissionAdmin
from .anonymous_permission    import AnonymousPermissionAdmin
from .auth_config             import AuthConfigAdmin
from .auth_token              import AuthTokenAdmin
from .enrollment_method       import EnrollmentMethodAdmin
from .group                   import GroupAdmin
from .permission_text         import PermissionTextAdmin
from .role                    import RoleAdmin
from .role_assignment         import RoleAssignmentAdmin
from .signup_group_assignment import SignupGroupAssignmentAdmin
from .user                    import UserAdmin
from ..                       import models

admin_site.register(models.AuthConfig,            AuthConfigAdmin)
admin_site.register(models.SignupGroupAssignment, SignupGroupAssignmentAdmin)
admin_site.register(models.User,                  UserAdmin)
admin_site.register(models.Group,                 GroupAdmin)
admin_site.register(models.AuthToken,             AuthTokenAdmin)
admin_site.register(models.PermissionText,        PermissionTextAdmin)
admin_site.register(models.AnonymousPermission,   AnonymousPermissionAdmin)
admin_site.register(models.AllowedRolePermission, AllowedRolePermissionAdmin)
admin_site.register(models.Role,                  RoleAdmin)
admin_site.register(models.RoleAssignment,        RoleAssignmentAdmin)
admin_site.register(models.EnrollmentMethod,      EnrollmentMethodAdmin)
admin_site.register(models.AccessRequest,         AccessRequestAdmin)

# Hacking django-allauth to use the Django Unfold styling
# Template: https://codeberg.org/allauth/django-allauth/src/branch/main/allauth/account/admin.py
# Template: https://codeberg.org/allauth/django-allauth/src/branch/main/allauth/idp/oidc/admin.py
from allauth.account       import app_settings as allauth_app_settings
from allauth.account       import models       as allauth_account_models
from allauth.socialaccount import models       as allauth_socialaccount_models
from ..allauth             import admin        as allauth

admin_site.register(allauth_account_models.EmailAddress, allauth.EmailAddressAdmin)

if not allauth_app_settings.EMAIL_CONFIRMATION_HMAC:
    admin_site.register(allauth_account_models.EmailConfirmation, allauth.EmailConfirmationAdmin)

admin_site.register(allauth_socialaccount_models.SocialApp,     allauth.SocialAppAdmin)
admin_site.register(allauth_socialaccount_models.SocialAccount, allauth.SocialAccountAdmin)
admin_site.register(allauth_socialaccount_models.SocialToken,   allauth.SocialTokenAdmin)