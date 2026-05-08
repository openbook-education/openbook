# OpenBook: Interactive Online Textbooks - Server
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from allauth.account.decorators import secure_admin_login
from django.apps                import apps
from django.conf                import settings
from django.utils.translation   import gettext_lazy as _
from djangoql.admin             import DjangoQLSearchMixin
from import_export.resources    import ModelResource
from import_export.admin        import ImportExportModelAdmin
from import_export.fields       import Field
from unfold.sites               import UnfoldAdminSite
from unfold.admin               import ModelAdmin as UnfoldModelAdmin

class ImportExportModelResource(ModelResource):
    """
    Allow deleting entries while importing model data in the admin.

    The files may include a row called delete with a boolean value to indicate the
    rows to be deleted.
    """
    delete = Field(column_name="delete")

    def dehydrate_delete(self, obj):
        return "false"

    def for_delete(self, row, instance):
        return "delete" in row and row["delete"].upper() in ["1", "X", "YES", "TRUE"]

class CustomModelAdmin(DjangoQLSearchMixin, UnfoldModelAdmin, ImportExportModelAdmin):
    """
    Combine Django Unfold, Django QL, and Django Import/Export mixins in one base class.
    """
    save_as = True
    warn_unsaved_form = True
    compressed_fields = True

class CustomAdminSite(UnfoldAdminSite):
    """
    Override dashboard ordering of apps and models.

    Apps are sorted in the order listed in settings.INSTALLED_APPS. Models are
    sorted in the order in which they are registered with the admin site.
    """
    # Not used by Unfold Admin, but set in settings.py
    # site_title  = _("OpenBook: Admin")
    # site_header = _("OpenBook: Admin")
    # index_title = _("Administration")

    def __init__(self):
        """
        Initialize the site and track model registration order.
        """
        super().__init__()
        self._models_ = []

    def register(self, model_or_iterable, admin_class, **options):
        """
        Remember the order in which models are registered.
        """
        super().register(model_or_iterable, admin_class, **options)

        try:
            for model in iter(model_or_iterable):
                if model in self._models_:
                    self._models_.remove(model)

                self._models_.append(model)
        except TypeError:
            self._models_.append(model_or_iterable)

    def unregister(self, model_or_iterable):
        """
        Remove unregistered models from the internal order list.
        """
        super().unregister(model_or_iterable)

        try:
            for model in iter(model_or_iterable):
                if model in self._models_:
                    self._models_.remove(model)
        except TypeError:
            if model_or_iterable in self._models_:
                self._models_.remove(model_or_iterable)

    def get_app_list(self, request, *args):
        """
        Return the app list with custom app and model ordering.
        """
        # Sort apps in the order they appear in the settings
        app_list = super().get_app_list(request, *args)

        for admin_app in app_list:
            app_config = apps.get_app_config(admin_app["app_label"])
            admin_app["_index_"] = settings.INSTALLED_APPS.index(app_config.name)

        app_list.sort(key = lambda admin_app: admin_app["_index_"])

        for admin_app in app_list:
            del admin_app["_index_"]

        # Sort models in the order they were registered
        for admin_app in app_list:
            for model in admin_app["models"]:
                model["_index_"] = self._models_.index(model["model"])

            admin_app["models"].sort(key = lambda model: model["_index_"])

            for model in admin_app["models"]:
                del model["_index_"]

        # Clean up menu structure by hiding  models that are shown as changelist tabs
        # in other models. Also hide apps without remaining models.
        changelist_tabs    = []
        hidden_model_names = []
        group_labels       = {}

        try:
            changelist_tabs = settings.UNFOLD["TABS"]
        except KeyError:
            pass

        for changelist_tab in changelist_tabs:
            hidden_model_names = [*hidden_model_names, *changelist_tab["models"][1:]]

            if "ob_group_name" in changelist_tab:
                group_labels[changelist_tab["models"][0]] = changelist_tab["ob_group_name"]

        for i in reversed(range(len(app_list))):
            admin_app = app_list[i]

            for j in reversed(range(len(admin_app["models"]))):
                model_class  = admin_app["models"][j]["model"]
                app_label    = model_class._meta.app_label
                model_name   = model_class._meta.model_name
                model_string = f"{app_label}.{model_name}"

                if model_string in hidden_model_names:
                    del admin_app["models"][j]
                elif model_string in group_labels:
                    admin_app["models"][j]["name"] = group_labels[model_string]

            if not len(admin_app["models"]):
                del app_list[i]

        return app_list

admin_site = CustomAdminSite()
admin_site.login = secure_admin_login(admin_site.login)
