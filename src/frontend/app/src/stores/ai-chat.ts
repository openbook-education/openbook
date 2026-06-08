/*
 * OpenBook: Interactive Online Textbooks
 * © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import type { WebSocketClient }    from "../api/websocket.js";
import type { WSConnectionStatus } from "../api/websocket.js";

import { ReadableStore }           from "../utils/store.js";
import api                         from "../api/index.js";
import { toasts }                  from "./toasts.js";
import { i18n }                    from "./i18n.js";

////////////////////////////////////////////////////////////////////////////////
// NOTE: The typings at the bottom of this file must match the typings on     //
// the Python side. Currently we have no tool to automatically create them    //
// from the server-provided AsyncAPI specification. Thus, for now the typings //
// must be manually converted from Python to TypeScript.                      //
////////////////////////////////////////////////////////////////////////////////

/**
 * UI state for the AI chat.
 */
export type ChatState = {
    /**
     * Server connection status.
     */
    connection: WSConnectionStatus;

    /**
     * Chat history.
     */
    messages: ChatMessagePayload[];
};

/**
 * Messages sent from client to server.
 */
export type SentMessages = GetChatHistory | ChatInput;

/**
 * Messages sent from server to client.
 */
export type ReceivedMessages = ChatHistory | ChatMessage;

/**
 * A readable store that manages a connection to the backend server and synchronizes
 * AI chat messages between the client and server. Use this inside the UI code to send
 * and receive AI chat messages.
 */
export class AiChatStore extends ReadableStore<ChatState> {
    #ws?: WebSocketClient<SentMessages, ReceivedMessages>;

    /**
     * Object initialization.
     */
    constructor() {
        super({ connection: "disconnected", messages: [] });
    }

    /**
     * Connect to the server, if not already connected. No communication is possible
     * before this method is called.
     */
    async connect() {
        if (!this.#ws) this.#ws = await api.ws("/ai/chat");

        /**
         * Receive new connection status
         */
        this.#ws.setConnectionStatusListener(async status => {
            this.update(state => {
                state.connection = status;
                return state;
            });

            // Request full chat history from the server, once the connection is established
            // or brought back after a connection failure. Just to make sure we catch up with
            // the server-side.
            if (status === "connected") {
                await this.getChatHistory();
            }
        });

        /**
         * Show toast for generic WebSocket errors
         */
        this.#ws.setErrorHandler(error => {
            const errorText = (error instanceof Error && error.message) ? error.message : i18n.value.Error.WebSocket.UnknownError;
            toasts.show("error", errorText);
        });

        /**
         * Receive full chat history from server
         */
        this.#ws.setMessageHandler("chat_history", (message: ChatHistory) => {
            this.update(state => {
                state.messages = message.payload.messages;
                return state;
            });
        });

        /**
         * Receive streaming chat message from server. If a message with the same
         * ID already exists, it will be replaced. Otherwise the new message will
         * be appended at the end of the list.
         */
        this.#ws.setMessageHandler("chat_message", (message: ChatMessage) => {
            this.update(state => {
                const messagePayload = message.payload;
                const index = state.messages.findIndex((m) => m.id === messagePayload.id);

                if (index === -1) {
                    state.messages.push(messagePayload);
                } else {
                    state.messages[index] = messagePayload;
                }

                return state;
            });
        });

        await this.#ws.connect();
    }

    /**
     * Disconnect from the server, if already connected or trying to connect.
     */
    async disconnect() {
        if (!this.#ws) return;
        await this.#ws.disconnect();
    }

    /**
     * Request full chat history from the server. Will be automatically called
     * once the connection is established.
     */
    async getChatHistory() {
        const message: GetChatHistory = { action: "get_chat_history", payload: null };
        return this.#ws?.send(message);
    }

    /**
     * Send user chat message to the AI assistant.
     *
     * @param format Message format
     * @param content Message content
     */
    async sendChatInput(format: ChatMessageFormat, content: string) {
        // Note: No state update here to add the user message to the chat history,
        // because the server will send the full message back to us!
        const message: ChatInput = {
            action: "chat_input",
            payload: { format: format, content: content },
        };
        return this.#ws?.send(message);
    }
}

/**
 * Who sent the message, the user or the AI assistant
 */
export type ChatMessageSender = "user" | "assistant";

/**
 * How to interpret and handle a chat message. The user can only send normal messages.
 * The other values are reserved for the AI assistant.
 *
 * - `normal`:  Regular chat message
 * - `status`:  Temporary status message, e.g. "Thinking"
 * - `thought`: Temporary chain of thought message
 * - `action`:  A UI action triggered by the assistant
 * - `system`:  An information, warning or error message
 */
export type ChatMessageType = "normal" | "status" | "thought" | "action" | "system"

/**
 * Severity of system messages
 */
export type ChatMessageSeverity = "info" | "warning" | "error" | "critical";

/**
 * Format of the message content. Binary content is always Base64 encoded
 */
export type ChatMessageFormat = "markdown" | "json" | "image";

/**
 * Guard rails check incoming chat messages for disallowed or dangerous content.
 * This type defines the data structure for the check results.
 */
export type GuardRailCheckResult = {
    findings:    "none" | "offensive_language" | "dangerous_content" | "others";
    explanation: string;
}

/**
 * Payload for incoming user chat messages.
 */
export type ChatInputPayload = {
    format:  ChatMessageFormat
    content: string;
};

/**
 * Payload for a single chat message.
 */
export type ChatMessagePayload = {
    id:         string;
    datetime:   string;
    sender:     ChatMessageSender;
    type:       ChatMessageType;
    severity:   ChatMessageSeverity;
    guardRails: GuardRailCheckResult;
    format:     ChatMessageFormat;
    content:    string;
    finished:   boolean;
};

/**
 * Payload containing the full chat history.
 */
export type ChatHistoryPayload = {
    messages: ChatMessagePayload[];
};

/**
 * Chat input sent by the user to the assistant.
 */
export type ChatInput = {
    action:  "chat_input";
    payload: ChatInputPayload;
};

/**
 * A single chat message within a larger chat conversation.
 */
export type ChatMessage = {
    action:  "chat_message";
    payload: ChatMessagePayload;
};

/**
 * Message sent by the client to retrieve the full chat history from the server.
 */
export type GetChatHistory = {
    action:  "get_chat_history";
    payload: null;
};

/**
 * Full chat history.
 */
export type ChatHistory = {
    action:  "chat_history";
    payload: ChatHistoryPayload;
};
