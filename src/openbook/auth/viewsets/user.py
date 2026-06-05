# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from drf_spectacular.utils         import extend_schema
from drf_spectacular.utils         import extend_schema_field
from drf_spectacular.utils         import extend_schema_view
from django_filters.filterset      import FilterSet
from rest_framework.permissions    import AllowAny
from rest_framework.serializers    import BooleanField
from rest_framework.serializers    import SerializerMethodField
from rest_framework.response       import Response
from rest_framework.viewsets       import ModelViewSet

from openbook.drf.flex_serializers import FlexFieldsModelSerializer
from openbook.drf.viewsets         import ModelViewSetMixin
from openbook.drf.viewsets         import with_flex_fields_parameters
from ..models.user                 import User

class UserSerializer(FlexFieldsModelSerializer):
    __doc__ = "User"

    full_name = SerializerMethodField()

    class Meta:
        model = User

        fields = [
            "id", "username",
            "full_name", "first_name", "last_name",
            "description", "picture",
            "is_staff", "last_login", "date_joined",
        ]

        read_only_fields  = ["username", "is_staff"]
        filterset_fields  = ["first_name", "last_name", "is_staff"]
        expandable_fields = {}

    @extend_schema_field(str)
    def get_full_name(self, obj):
        return obj.get_full_name() if hasattr(obj, "get_full_name") else ""

class CurrentUserSerializer(UserSerializer):
    __doc__ = "Current User"

    is_authenticated = BooleanField(read_only=True)

    class Meta:
        model             = User
        fields            = [*UserSerializer.Meta.fields, "email", "is_authenticated"]
        filterset_fields  = [*UserSerializer.Meta.filterset_fields]

class UserFilter(FilterSet):
    class Meta:
        model  = User
        fields = {
            "username":    ("icontains",),
            "first_name":  ("icontains",),
            "last_name":   ("icontains",),
            "email":       ("icontains",),
            "description": ("icontains",),
            "is_staff":    ("exact",),
        }

@extend_schema(
    extensions={
        "x-app-name":   "User Management",
        "x-model-name": "User Profiles",
    }
)
@with_flex_fields_parameters()
class UserViewSet(ModelViewSetMixin, ModelViewSet):
    """Provide read/write operations for active user profiles."""
    __doc__ = "Users"

    lookup_field       = "username"
    queryset           = User.objects.filter(is_active=True)
    http_method_names  = ["get", "put", "patch", "delete"]  # Post (create) not allowed!
    filterset_class    = UserFilter
    serializer_class   = UserSerializer
    ordering           = ["username"]
    search_fields      = ["username", "first_name", "last_name", "description"]

@extend_schema(
    extensions={
        "x-app-name":   "User Management",
        "x-model-name": "Current User",
    }
)
@extend_schema_view(retrieve=extend_schema(exclude=True))
@with_flex_fields_parameters()
class CurrentUserViewSet(ModelViewSet):
    """Return the profile of the currently logged-in user.

    If no user is logged in, return a simple response with
    ``is_authenticated = false``.
    """
    __doc__ = "Current User"

    permission_classes = [AllowAny]
    serializer_class   = CurrentUserSerializer
    queryset           = User.objects.none()

    def get_view_name(self):
        return "Current User"

    @extend_schema(
        operation_id= "auth_current_user",
        description = "Returns the currently authenticated user or a fallback response.",
        responses   = CurrentUserSerializer,
        summary     = "Retrieve",
    )
    def list(self, request):
        if request.user.is_authenticated:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        else:
            return Response({"is_authenticated": False})

    def retrieve(self, request, pk=None):
        # Disable detail route
        raise NotImplementedError()
