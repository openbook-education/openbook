# OpenBook: Interactive Online Textbooks
# © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from chanx.channels.websocket import AsyncJsonWebsocketConsumer
from chanx.core.decorators    import channel, ws_handler
from chanx.messages.incoming  import PingMessage
from chanx.messages.outgoing  import PongMessage
from datetime                 import datetime, UTC

from ..messages.chat          import ChatHistory, ChatInput, ChatMessage, GetChatHistory

@channel(
    name        = "chat",
    description = "Chat with AI Assistant",
    tags        = ["ai", "chat"],
)
class ChatConsumer(AsyncJsonWebsocketConsumer):
    """
    Websocket consumer for chatting with the AI assistant.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize object with a simply in-memory chat history. Note: In future
        versions this should be replaced with a persisted chat memory.
        """
        super().__init__(*args, **kwargs)
        self.chat_history: list[ChatMessage] = []

    @ws_handler(
        summary     = "Handle Ping Requests",
        description = "Simple ping-pong for connectivity testing",
    )
    async def handle_ping(self, message: PingMessage) -> PongMessage:
        return PongMessage()

    @ws_handler(
        summary     = "Get Chat History",
        description = "Retrieve the full chat history from the server",
    )
    async def handle_get_chat_history(self, message: GetChatHistory) -> ChatHistory:
        """
        Return the whole chat history to the client.
        """
        return ChatHistory(messages=self.chat_history)

    @ws_handler(
        summary     = "Handle Chat Input",
        description = "Send a new chat message from the user to the assistant",
    )
    async def handle_chat_input(self, message: ChatInput) -> ChatMessage:
        """
        Handle incoming chat message sent by the user.
        """
        user_message = ChatMessage(
            datetime   = datetime.now(UTC),
            sender     = "user",
            type       = "normal",
            severity   = "info",
            guardRails = {"findings": "none", "explanation": ""},
            format     = message.format,
            content    = message.content,
            finished   = True,
        )
        self.chat_history.append(user_message)

        response_message = ChatMessage(
            datetime   = datetime.now(UTC),
            sender     = "assistant",
            type       = "normal",
            severity   = "info",
            guardRails = {"findings": "none", "explanation": ""},
            format     = "markdown",
            content    = f"Fake response: {message.content}",
            finished   = True,
        )

        self.chat_history.append(response_message)
        return response_message

