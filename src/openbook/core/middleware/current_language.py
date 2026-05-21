# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import threading

thread_local = threading.local()

def CurrentLanguageMiddleware(get_response):
    """
    Save the current language in a thread-local variable so that it can be accessed
    within the other layers. This is done to get the language in DRF serializers that
    needs to handle translation themselves.
    """
    def middleware(request):
        thread_local.current_language = request.LANGUAGE_CODE
        return get_response(request)

    return middleware

def get_current_language():
    """
    Get the current request language, if any. Returns `None` otherwise.
    """
    return getattr(thread_local, "current_language", None)
