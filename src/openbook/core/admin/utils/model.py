# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.contrib.auth    import get_permission_codename
from django.core.exceptions import PermissionDenied
from django.db.models       import Model
from django.http            import HttpRequest

from unfold.admin           import ModelAdmin as UnfoldModelAdmin

# Currently not used but kept in case we want to introduce object-level permissions in the Admin
class ModelAdmin(UnfoldModelAdmin):
    """
    Improved version of the stock ``ModelAdmin`` that checks object-permissions instead of
    the regular model-permissions. The only difference is, that ``obj`` will be set to the
    object to be viewed/changed/deleted, when the permission is checked.

    This relies on our custom authentication backend to fallback to regular permissions
    checks when the object doesn't support object-permissions or the object-based permission
    check fails.
    """
    def save_form(self, request, form, change):
        """
        The parent class calls ``has_add_permission()`` in ``_changeform_view()`` just before the form
        data is validated and saved, but doesn't have the new object, yet. Therefor ``has_add_permission()``
        lacks the ``obj`` parameter. This method is called after the validation to actually save the object.
        As a hacky workaround we catch up on the permission check here.
        """
        if not change:
            opts = self.opts
            codename = get_permission_codename("add", opts)
            obj = form.save(commit=False)

            if not request.user.has_perm("%s.%s" % (opts.app_label, codename), obj):
                raise PermissionDenied

        super().save_form(request, form, change)

    def has_view_permission(self, request: HttpRequest, obj: Model = None) -> bool:
        """
        The base class also checks "change" permission, when "view" fails. This logic was moved
        to our custom authentication backend.
        """
        opts = self.opts
        codename = get_permission_codename("view", opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename), obj)

    def has_change_permission(self, request: HttpRequest, obj: Model = None) -> bool:
        opts = self.opts
        codename = get_permission_codename("change", opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename), obj)

    def has_delete_permission(self, request: HttpRequest, obj: Model = None) -> bool:
        opts = self.opts
        codename = get_permission_codename("delete", opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename), obj)
