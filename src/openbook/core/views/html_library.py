# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import io, sys, traceback

from django                   import forms
from django.shortcuts         import get_object_or_404
from django.utils.text        import format_lazy as _f
from django.utils.translation import gettext_lazy as _
from django.views.generic     import FormView
from unfold.views             import UnfoldModelAdminViewMixin
from unfold.widgets           import UnfoldBooleanSwitchWidget
from unfold.widgets           import UnfoldAdminCheckboxSelectMultipleWidget
from unfold.widgets           import UnfoldAdminSelectWidget

from ..models.html_library    import HTMLLibrary
from ..models.html_library    import HTMLLibraryVersion

class UnpackHTMLLibraryArchivesForm(forms.Form):
    """
    Custom form to render the input fields with proper styling.
    """
    library_versions = forms.MultipleChoiceField(
        label    = _("Library Versions"),
        choices  = [],
        required = True,
        widget   = UnfoldAdminCheckboxSelectMultipleWidget,
    )

    extract_archive = forms.BooleanField(
        label    = _("Extract archive file on filesystem"),
        initial  = True,
        required = False,
        widget   = UnfoldBooleanSwitchWidget,
    )
    
    update_library = forms.BooleanField(
        label    = _("Update library header data"),
        initial  = True,
        required = False,
        widget   = UnfoldBooleanSwitchWidget,
    )
    
    update_version = forms.BooleanField(
        label    = _("Update library version data"),
        initial  = True,
        required = False,
        widget   = UnfoldBooleanSwitchWidget,
    )
    
    update_components = forms.BooleanField(
        label    = _("Update component definitions"),
        initial  = True,
        required = False,
        widget   = UnfoldBooleanSwitchWidget,
    )
    
    verbosity = forms.ChoiceField(
        label    = _("Log Output"),
        choices  = [(1, _("Normal")), (2, _("Verbose"))],
        initial  = 1,
        required = True,
        widget   = UnfoldAdminSelectWidget,
    )

    def set_library(self, library):
        library_version_choices = [(lv.id, lv.fqn()) for lv in library.versions.all()]
        self.fields["library_versions"].choices = library_version_choices


class UnpackHTMLLibraryArchivesView(UnfoldModelAdminViewMixin, FormView):
    """
    Custom view that allows to unpack uploaded library archives in the Django Admin.
    The view is called for a single library of which the versions can be selected
    whose archives shall be unpacked and further installed.
    """
    title               = _("Unpack Archives")
    permission_required = ["openbook_core.change_htmllibraryversion"]
    template_name       = "openbook_core/admin/html_library/unpack.html"
    form_class          = UnpackHTMLLibraryArchivesForm

    def setup(self, request, *args, library_id, **kwargs):
        """
        Setup view instance. Read library from database.
        """
        super().setup(request, *args, **kwargs)
        self.library = get_object_or_404(HTMLLibrary, pk = library_id)
        self.log_output = ""

    def get_context_data(self, **kwargs):
        """
        Populate template context for rendering the output page.
        """
        return {
            **super().get_context_data(**kwargs),
            "library":    self.library,
            "log_output": self.log_output,
        }
    
    def get_form(self, form_class=None):
        """
        Initialize form and pass the library so that the library version choices can be set.
        """
        form = super().get_form(form_class)
        form.set_library(self.library)
        return form

    def form_valid(self, form):
        """
        Process valid form data by calling the installation method with the arguments received
        from the form. Unlike normal form handling, don't redirect but simply render the form
        again, so that the transient log output can be shown.
        """
        log_output = io.StringIO()

        try:
            verbosity = int(form.cleaned_data["verbosity"])
        except ValueError:
            verbosity = 1

        for library_version_id in form.cleaned_data["library_versions"]:
            library_version = get_object_or_404(HTMLLibraryVersion, pk = library_version_id)

            try:
                library_version.unpack_archive(
                    extract_archive   = form.cleaned_data["extract_archive"],
                    update_library    = form.cleaned_data["update_library"],
                    update_version    = form.cleaned_data["update_version"],
                    update_components = form.cleaned_data["update_components"],
                    verbosity         = verbosity,
                    stdout            = log_output,
                )
            except Exception as e:
                msg = _f("An exception occurred while processing library {fqn}:", fqn=library_version.fqn())
                log_output.write(f"{msg}\n{e}\n")
                traceback.print_exc(limit=None, file=sys.stderr)

            log_output.write("\n")
            
        # Rerender form so that the log output can be displayed, even though it is not saved.
        self.log_output = log_output.getvalue()
        return super().form_invalid(form)
