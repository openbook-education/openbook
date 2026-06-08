# OpenBook: Interactive Online Textbooks
# © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from chanx.messages.base import BaseMessage
from datetime            import datetime
from pydantic            import BaseModel, Field
from typing              import Literal
from uuid                import uuid4

ChatMessageSender = Literal["user", "assistant"]
"""Who sent the message, the user or the AI assistant"""

ChatMessageType = Literal["normal", "status", "thought", "action", "system"]
"""
How to interpret and handle a chat message. The user can only send normal messages.
The other values are reserved for the AI assistant.

- ``normal``:  Regular chat message
- ``status``:  Temporary status message, e.g. "Thinking"
- ``thought``: Temporary chain of thought message
- ``action``:  A UI action triggered by the assistant
- ``system``:  An information, warning or error message
"""

ChatMessageSeverity = Literal["info", "warning", "error", "critical"]
"""Severity of system messages"""

ChatMessageFormat = Literal["markdown", "json", "image"]
"""Format of the message content. Binary content is always Base64 encoded."""

class GuardRailCheckResult(BaseModel):
    """
    Guard rails check incoming chat messages for disallowed or dangerous content.
    This type defines the data structure for the check results.
    """
    findings:    Literal["none", "offensive_language", "dangerous_content", "others"]
    explanation: str

class ChatInputPayload(BaseModel):
    """
    Payload for incoming user chat messages.
    """
    format:  ChatMessageFormat
    content: str

class ChatMessagePayload(BaseModel):
    """
    Payload for a single chat message.
    """
    id:         str = Field(default_factory = lambda: str(uuid4()))
    datetime:   datetime
    sender:     ChatMessageSender
    type:       ChatMessageType
    severity:   ChatMessageSeverity
    guardRails: GuardRailCheckResult
    format:     ChatMessageFormat
    content:    str
    finished:   bool

class ChatHistoryPayload(BaseModel):
    """
    Payload containing the full chat history.
    """
    messages: list[ChatMessagePayload]

class ChatInput(BaseMessage):
    """
    Chat input sent by the user to the assistant.
    """
    action:  Literal["chat_input"] = "chat_input"
    payload: ChatInputPayload

class ChatMessage(BaseMessage):
    """
    A single chat message within a larger chat conversation. This is the data that
    the server uses internally to drive the AI chat functionality and persist the
    chat history.
    """
    action:  Literal["chat_message"] = "chat_message"
    payload: ChatMessagePayload

class GetChatHistory(BaseMessage):
    """
    Message sent by the client to retrieve the full chat history from the server.
    """
    action:  Literal["get_chat_history"] = "get_chat_history"
    payload: None = None

class ChatHistory(BaseMessage):
    """
    Full chat history.
    """
    action:  Literal["chat_history"] = "chat_history"
    payload: ChatHistoryPayload
