# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.core.exceptions        import ValidationError as DjangoValidationError
from rest_flex_fields2.serializers import FlexFieldsModelSerializer as RFFFlexFieldsModelSerializer
from rest_framework.exceptions     import ValidationError as DRFValidationError

class FlexFieldsModelSerializer(RFFFlexFieldsModelSerializer):
    """
    Reuse full cleaning and validation logic of the models in the REST API, including
    `full_clean()`, `clean()`, field validation and uniqueness checks. Also make sure,
    that the pre-filled model instance can be accessed in the DRF view.
    ```
    """
    def validate(self, attrs):
        # Create or update instance for validation and cache for access in view
        self._instance = self.instance or self.Meta.model()

        for attr, value in attrs.items():
            setattr(self._instance, attr, value)

        try:
            self._instance.full_clean()
        except DjangoValidationError as e:
            # Convert Django's ValidationError to DRF's ValidationError
            raise DRFValidationError(e.message_dict)

        return attrs

    def get_prefilled_instance(self):
        """
        Method to access the pre-filled model instance in `ModelViewSetMixin`.
        """
        return getattr(self, '_instance', None)
