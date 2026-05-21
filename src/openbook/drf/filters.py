# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from rest_framework.filters import BaseFilterBackend

class DjangoObjectPermissionsFilter(BaseFilterBackend):
    """
    Filter implementation inspired by `django-rest-framework-guardian2` `ObjectPermissionsFilter`.
    Filters out all objects from a queryset for which the user has no object-level view permission.
    """
    def filter_queryset(self, request, queryset, view):
        app_label   = queryset.model._meta.app_label
        model_name  = queryset.model._meta.model_name
        perm_string = f"{app_label}.view_{model_name}"
        allowed_pks = []

        for obj in queryset:
            if request.user.has_perm(perm_string, obj):
                allowed_pks.append(obj.pk)

        return queryset.model.objects.filter(pk__in=allowed_pks)