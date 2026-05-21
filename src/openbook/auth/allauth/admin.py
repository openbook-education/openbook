# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from allauth.account                 import admin as account_admin
from allauth.socialaccount           import admin as socialaccount_admin
from django                          import forms
from unfold.widgets                  import UnfoldAdminSelectWidget
from unfold.widgets                  import UnfoldAdminTextareaWidget

from openbook.admin                  import CustomModelAdmin
from openbook.core.models.utils.json import PrettyPrintJSONEncoder

# Very dirty, but how else could be make Django Unfold play nice with
# the admin views provided by django-allauth!?

class EmailAddressAdmin(CustomModelAdmin, account_admin.EmailAddressAdmin):
    pass

class EmailConfirmationAdmin(CustomModelAdmin, account_admin.EmailConfirmationAdmin):
    pass

class SocialAppForm(socialaccount_admin.SocialAppForm):
    class Meta(socialaccount_admin.SocialAppForm.Meta):
        # Undo custom form widgets because the lack the Django Unfold styling
        widgets = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Use Unfold styled widget
        self.fields["provider"] = forms.ChoiceField(
            choices = self.fields["provider"].choices,
            widget  = UnfoldAdminSelectWidget(),
        )

        self.fields["settings"] = forms.JSONField(
            widget  = UnfoldAdminTextareaWidget(),
            encoder = PrettyPrintJSONEncoder
        )

class SocialAppAdmin(CustomModelAdmin, socialaccount_admin.SocialAppAdmin):
    form = SocialAppForm

class SocialAccountAdmin(CustomModelAdmin, socialaccount_admin.SocialAccountAdmin):
    pass

class SocialTokenAdmin(CustomModelAdmin, socialaccount_admin.SocialTokenAdmin):
    pass