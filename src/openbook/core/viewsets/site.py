# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django_filters.filters        import CharFilter
from django_filters.filterset      import FilterSet
from drf_spectacular.utils         import extend_schema
from drf_spectacular.utils         import inline_serializer
from rest_framework.viewsets       import ReadOnlyModelViewSet
from rest_framework.decorators     import action
from rest_framework.response       import Response
from rest_framework.serializers    import CharField
from rest_framework.permissions    import AllowAny

from openbook.drf.flex_serializers import FlexFieldsModelSerializer
from openbook.drf.viewsets         import AllowAnonymousListRetrieveViewSetMixin
from openbook.drf.viewsets         import with_flex_fields_parameters
from ..models.site                 import Site

class SiteSerializer(FlexFieldsModelSerializer):
    __doc__ = "Site"

    class Meta:
        model  = Site
        fields = ("id", "domain", "name", "short_name", "about_url", "brand_color", "auth_config")
        expandable_fields = {
            "auth_config": "openbook.auth.viewsets.auth_config.AuthConfigSerializer"
        }

class SiteFilter(FilterSet):
    domain     = CharFilter(lookup_expr="icontains")
    name       = CharFilter(lookup_expr="icontains")
    short_name = CharFilter(lookup_expr="icontains")

    class Meta:
        model = Site
        fields = ("domain", "name", "short_name")

@extend_schema(
    extensions={
        "x-app-name":   "OpenBook Server",
        "x-model-name": "Websites",
    }
)
@with_flex_fields_parameters()
class SiteViewSet(AllowAnonymousListRetrieveViewSetMixin, ReadOnlyModelViewSet):
    __doc__ = "General Website Settings"

    queryset           = Site.objects.all()
    serializer_class   = SiteSerializer
    filterset_class    = SiteFilter
    ordering           = ("domain", "short_name", "name")
    search_fields      = ("domain", "name", "short_name")

    @extend_schema(
        responses = inline_serializer(name="health-response", fields={
            "status": CharField(help_text="Status of the API server")
        }),
        summary="Health Status",
    )
    @action(detail=False, permission_classes=[AllowAny])
    def health(self, request):
        """
        Return a simple health status that the API is up and running.
        """
        return Response({"status": "GOOD"})
