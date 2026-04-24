# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from collections                import defaultdict
from drf_spectacular.utils      import extend_schema
from drf_spectacular.types      import OpenApiTypes
from drf_spectacular.utils      import OpenApiParameter
from rest_framework             import status
from rest_framework.permissions import AllowAny
from rest_framework.response    import Response
from rest_framework.settings    import api_settings

class ModelViewSetMixin:
    """
    Ensure that object permissions are also checked when creating new model instances.
    DRF checks object permissions on database-loaded objects, but during creation,
    the object doesn't exist yet. Here we validate the input and construct the instance
    before saving to allow permission checks.

    NOTE: This is a mixin that must be used together with `ModelViewSet` to avoid a mysterious
    circular import in DRF. To overwrite the implementation of `post()` the mixin must come first.

    ```python
    class MyViewSet(ModelViewSetMixin, ModelViewSet):
        pass
    ```
    """

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if hasattr(serializer, "get_prefilled_instance"):
            # Use custom method to construct the instance
            instance = serializer.get_prefilled_instance()
        else:
            # Default behavior: construct the instance manually
            instance = serializer.Meta.model(**serializer.validated_data)

        self.check_object_permissions(request, instance)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class AllowAnonymousListRetrieveViewSetMixin:
    """
    Small view set mixin class that allows unrestricted access to the `list` and `retrieve`
    actions while deferring permission checks for all other actions to the permission classes
    of the view set (usually defined in `settings.py`).
    """
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return (AllowAny(),)
        else:
            return super().get_permissions()

def with_flex_fields_parameters():
    """
    Decorator for view set classes to add the `drf-flex-fields?` query parameters, with which
    clients can choose the fields they want to receive, to the OpenAPI description.
    """
    return extend_schema(
        parameters=[
            OpenApiParameter("_fields", OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Fields to be included in the response"),
            OpenApiParameter("_omit",   OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Fields to be removed from the response"),
            OpenApiParameter("_expand", OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Relationships to be expanded in the response"),
        ]
    )

OPERATION_ID_SUMMARY = {
    "list":           "List",
    "retrieve":       "Retrieve",
    "create":         "Create",
    "update":         "Update",
    "partial_update": "Partial Update",
    "destroy":        "Delete",
}

def add_tag_groups(result, **kwargs):
    """
    Builds x-tagGroups for drf-spectacular based on OpenAPI extensions:

    - `x-app-name`:   used for tag group
    - `x-model-name`: used as the tag for the endpoint
    """
    tag_groups = defaultdict(set)

    for path_item in result.get("paths", {}).values():
        for method, operation in path_item.items():
            if not isinstance(operation, dict):
                continue

            # Get tag info
            extensions = operation.get("extensions", operation)
            app_name   = extensions.get("x-app-name")
            model_name = extensions.get("x-model-name")

            if app_name and model_name:
                tag_groups[app_name].add(model_name)
                operation["tags"] = [model_name]

            # Parse operationId to assign friendly label
            operation_id = operation.get("operationId")

            if operation_id and not "summary" in operation:
                for action, summary in OPERATION_ID_SUMMARY.items():
                    if operation_id.endswith(f"_{action}"):
                        operation["summary"] = summary

    result["x-tagGroups"] = [
        {"name": app_name, "tags": sorted(tags)}
        for app_name, tags in sorted(tag_groups.items())
    ]

    return result
