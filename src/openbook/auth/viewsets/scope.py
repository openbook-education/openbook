# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions             import FieldError
from drf_spectacular.utils              import extend_schema
from drf_spectacular.utils              import OpenApiParameter
from rest_framework                     import status
from rest_framework.permissions         import IsAuthenticated
from rest_framework.response            import Response
from rest_framework.serializers         import CharField
from rest_framework.serializers         import IntegerField
from rest_framework.serializers         import Serializer
from rest_framework.serializers         import UUIDField
from rest_framework.viewsets            import ViewSet

from openbook.core.utils.content_type   import content_type_for_model_string
from openbook.core.utils.content_type   import model_string_for_content_type
from ..models.allowed_role_permission   import AllowedRolePermission
from ..models.permission_text           import PermissionText
from ..models.mixins.scope              import ScopedRolesMixin
from ..utils                            import perm_string_for_permission

class AllowedPermissionSerializer(Serializer):
    id    = IntegerField()
    perm  = CharField()
    app   = CharField()
    model = CharField()
    name  = CharField()

class ScopeObjectSerializer(Serializer):
    uuid = UUIDField()
    name = CharField()

class ScopeTypeRetrieveSerializer(Serializer):
    pk                  = IntegerField()
    id                  = CharField()
    label               = CharField()
    objects             = ScopeObjectSerializer(many=True, required=False)
    allowed_permissions = AllowedPermissionSerializer(many=True, required=False)

class ScopeTypeListSerializer(Serializer):
    pk    = IntegerField()
    id    = CharField()
    label = CharField()

@extend_schema(
    extensions={
        "x-app-name":   "User Management",
        "x-model-name": "Scope Types",
    }
)
class ScopeTypeViewSet(ViewSet):
    """Return permission scope information.

    When a list is requested, return a flat list of scope types. If a single
    object is requested, return full details including all scopes and allowed
    permissions.
    """
    __doc__ = "Permission Scopes"

    permission_classes = [IsAuthenticated]
    pagination_class   = None
    filter_backends    = []
    queryset           = ContentType.objects.all()
    lookup_field       = "id"
    lookup_value_regex = '[^/]+'
    ordering           = ["id"]

    @extend_schema(responses=ScopeTypeListSerializer)
    def list(self, request, *args, **kwargs):
        """Return a flat list of scope types."""
        result = []

        for content_type in ScopedRolesMixin.get_scope_model_content_types():
            result.append({
                "pk":    content_type.pk,
                "id":    model_string_for_content_type(content_type),
                "label": content_type.name,
            })

        serializer = ScopeTypeListSerializer(data=result, many=True)
        serializer.is_valid()
        return Response(serializer.data)

    @extend_schema(
            parameters=[
                OpenApiParameter(
                    name        = "id",
                    type        = str,
                    location    = OpenApiParameter.PATH,
                    description = "Unique identifier for the scope (id or pk)",
                ),
            ],
            responses=ScopeTypeRetrieveSerializer,
        )
    def retrieve(self, request, *args, **kwargs):
        """Return a scope type with scopes and allowed permissions."""
        scope_type   = self.request.parser_context["kwargs"].get("id")
        content_type = None

        try:
            try:
                content_type = ContentType.objects.get(pk=int(scope_type))
            except ValueError:
                content_type = content_type_for_model_string(scope_type)
        except (ContentType.DoesNotExist, ValueError, LookupError):
            content_type = None

        if not content_type:
            return Response(status=status.HTTP_404_NOT_FOUND, data=[])

        try:
            query_set = content_type.get_all_objects_for_this_type().only("id", "name").order_by("name")
        except FieldError:
            # PK references content type without id or name field
            return Response(status=status.HTTP_404_NOT_FOUND, data=[])

        result = {
            "pk":                  content_type.pk,
            "id":                  model_string_for_content_type(content_type),
            "label":               content_type.name,
            "objects":             [],
            "allowed_permissions": [],
        }

        for scope in query_set.all():
            result["objects"].append({
                "uuid":  scope.id,
                "name":  scope.name if hasattr(scope, "name") else scope.id,
            })

        allowed_role_permissions = AllowedRolePermission.get_for_scope_type(content_type).all()
        allowed_permissions = []

        for allowed_role_permission in allowed_role_permissions:
            if allowed_role_permission.permission:
                allowed_permissions.append(allowed_role_permission.permission)

        translations = PermissionText.objects.filter(parent__in=allowed_permissions).all()

        for allowed_role_permission in allowed_role_permissions:
            permission = allowed_role_permission.permission

            if not permission:
                continue

            translation = next((t for t in translations if t.parent == permission), None)
            model = permission.content_type.model_class()

            result["allowed_permissions"].append({
                "id":    permission.pk,
                "perm":  perm_string_for_permission(permission),
                "app":   model._meta.app_config.verbose_name,
                "model": model._meta.verbose_name,
                "name":  translation.name if translation else permission.name,
            })

        serializer = ScopeTypeRetrieveSerializer(data=result)
        serializer.is_valid()
        return Response(serializer.data)
