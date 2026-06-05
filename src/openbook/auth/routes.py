# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

import typing

from .viewsets.access_request          import AccessRequestViewSet
from .viewsets.allowed_role_permission import AllowedRolePermissionViewSet
from .viewsets.auth_token              import AuthTokenViewSet
from .viewsets.enrollment_method       import EnrollmentMethodViewSet
from .viewsets.permission              import PermissionViewSet
from .viewsets.permission_text         import PermissionTextViewSet
from .viewsets.role_assignment         import RoleAssignmentViewSet
from .viewsets.role                    import RoleViewSet
from .viewsets.scope                   import ScopeTypeViewSet
from .viewsets.user                    import CurrentUserViewSet
from .viewsets.user                    import UserViewSet

if typing.TYPE_CHECKING:
    from rest_framework.routers        import DefaultRouter

def register_api_routes(router: DefaultRouter, prefix: str) -> None:
    router.register(f"{prefix}/access_requests",          AccessRequestViewSet,         basename="access_request")
    router.register(f"{prefix}/allowed_role_permissions", AllowedRolePermissionViewSet, basename="allowed_role_permission")
    router.register(f"{prefix}/auth_tokens",              AuthTokenViewSet,             basename="auth_token")
    router.register(f"{prefix}/current_user",             CurrentUserViewSet,           basename="current_user")
    router.register(f"{prefix}/enrollment_methods",       EnrollmentMethodViewSet,      basename="enrollment_method")
    router.register(f"{prefix}/users",                    UserViewSet,                  basename="user")
    router.register(f"{prefix}/permissions",              PermissionViewSet,            basename="permission")
    router.register(f"{prefix}/permission_texts",         PermissionTextViewSet,        basename="permission_text")
    router.register(f"{prefix}/roles",                    RoleViewSet,                  basename="role")
    router.register(f"{prefix}/role_assignments",         RoleAssignmentViewSet,        basename="role_assignment")
    router.register(f"{prefix}/scope_types",              ScopeTypeViewSet,             basename="scope_type")
