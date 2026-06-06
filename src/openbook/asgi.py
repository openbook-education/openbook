# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

import os

from channels.auth               import AuthMiddlewareStack
from channels.routing            import ChannelNameRouter, ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi            import get_asgi_application
from django.urls                 import path

from openbook.ai.consumers.chat  import ChatConsumer

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
# See: https://channels.readthedocs.io/en/latest/topics/troubleshooting.html
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openbook.settings")
asgi_application = get_asgi_application();

## from ob_xyz.consumers import ExampleWebsocketClient, ExampleWorkerProcess

application = ProtocolTypeRouter({
    "http":      asgi_application,
    "websocket": AuthMiddlewareStack(
        AllowedHostsOriginValidator(
            # AuthMiddlewareStack includes Cookies, Sessions and Auth
            AuthMiddlewareStack(
                # From: https://channels.readthedocs.io/en/latest/topics/routing.html#urlrouter
                # "Please note that URLRouter nesting will not work properly with path() routes
                # if inner routers are wrapped by additional middleware. See Issue #1428."
                # Therefore, we define all routes of all Django apps here (and not in the apps).
                URLRouter([
                    path("ws/ai/chat", ChatConsumer.as_asgi())
                ]),
            ),
        ),
    ),
    "channel": ChannelNameRouter({
        ## "example-worker-process": ExampleWorkerProcess.as_asgi()
    })
})
