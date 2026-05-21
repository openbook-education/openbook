# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django_filters.filters import CharFilter

class ScopedRolesFilterMixin:
    """Provide owner filtering for models that implement ScopedRolesMixin."""
    owner = CharFilter(method="owner_filter")

    class Meta:
        fields = {"owner": ("exact",)}

    def owner_filter(self, queryset, name, value):
        return queryset.filter(owner__username=value)

class ScopeTypeFilterMixin:
    """Provide scope-type filtering for models with a scope_type field."""
    scope_type = CharFilter(method="scope_type_filter")

    class Meta:
        fields = {
            "scope_type": ("exact",),
        }

    def scope_type_filter(self, queryset, name, value):
        try:
            return queryset.filter(scope_type__pk=int(value))
        except ValueError:
            app_label, model = value.split(".", 1)

            return queryset.filter(
                scope_type__app_label = app_label,
                scope_type__model     = model,
            )

class ScopeFilterMixin(ScopeTypeFilterMixin):
    """Provide scope filtering for models that implement ScopedMixin."""
    class Meta:
        fields = {
            **ScopeTypeFilterMixin.Meta.fields,
            "scope_uuid": ("exact",),
        }
