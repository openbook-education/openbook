/*
 * OpenBook: Interactive Online Textbooks
 * © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import {i18n} from "../stores/i18n";
import {_}    from "../stores/i18n";

/**
 * Maximum number of attempts for each request.
 */
const MAX_ATTEMPTS = 5;

/**
 * Initial delay after the first failed attempt.
 * Will be doubled for each successive retry.
 */
const BASE_DELAY_MS = 250;

/**
 * A simple wrapper around the browser's native `WebSocket` class that adds automatic
 * reconnect (with exponential backup) on connection loss and message handler routing.
 * Received messages must be JSON objects with a property called `action` (as per the
 * [chanx](https://chanx.readthedocs.io/) convention) to identify the message type.
 */
export class WebSocketClient<SentMessages extends WebSocketMessage, ReceivedMessages extends WebSocketMessage> {
    #url:             string;
    #socket?:         WebSocket;
    #status:          WSConnectionStatus = "disconnected";
    #statusListener?: WSConnectionStatusListener;
    #errorHandler?:   WSErrorHandler;
    #messageHandlers: Map<WebSocketMessageAction, WebSocketMessageHandler> = new Map();
    #messageQueue:    SentMessages[] = [];

    /**
     * Object initialization.
     * @param url Full URL of the WebSocket server
     */
    constructor(url: string) {
        this.#url = url;
    }

    /**
     * Set connection status listener that will be called for each change in
     * the connection status. Note that this replaces the previous listener.
     *
     * @param listener
     */
    setConnectionStatusListener(listener: WSConnectionStatusListener) {
        this.#statusListener = listener;
    }

    /**
     * Set error handler that will be called for generic WebSocket errors.
     * Note that this replaces the previous handler.
     *
     * @param handler Error handler
     */
    setErrorHandler(handler: WSErrorHandler) {
        this.#errorHandler = handler;
    }

    /**
     * Set message handler for a given message type. Note that this replaces the
     * previous handler for the same message type.
     *
     * @param action Message type
     * @param handler Message handler
     */
    setMessageHandler<Action extends ReceivedMessages["action"]>(
        action:  Action,
        handler: WebSocketMessageHandler<ExtractMessageByAction<ReceivedMessages, Action>>
    ) {
        this.#messageHandlers.set(action, handler);
    }

    /**
     * Utility method to set the current connection status and call the status listener.
     *
     * @param status New connection status
     * @param reconnectInSec Timeout before reconnect
     */
    async #setConnectionStatus(status: WSConnectionStatus, reconnectInSec: number = 0) {
        this.#status  = status;

        if (this.#statusListener) {
            await this.#statusListener(status, reconnectInSec);
        }
    }

    /**
     * Try to connect or reconnect to the WebSocket server. In case of an error, the
     * method tries to reconnect up to `MAX_ATTEMPTS` times with increasing delays
     * based on the `BASE_DELAY_WS` constant.
     *
     * When the method returns, the connection is either established or has failed
     * for good. In the latter case an exception is thrown.
     *
     * @throws `Error`, when the connection cannot be established
     */
    async connect() {
        if (!["disconnected", "connection_lost"].includes(this.#status)) return;

        let lastError: unknown = null;
        let delayMs = BASE_DELAY_MS;

        for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
            lastError = null;

            try {
                await this.#setConnectionStatus("connecting");

                await new Promise((resolve, reject) => {
                    this.#socket = new WebSocket(this.#url);

                    /**
                     * Connection established. Flush message queue, update status and
                     * resolve the promise to break the retry loop.
                     */
                    this.#socket.addEventListener("open", async () => {
                        await this.#setConnectionStatus("connected");

                        for (let message of this.#messageQueue) {
                            await this.#send(message);
                        }

                        this.#messageQueue = [];
                        resolve(undefined);
                    });

                    /**
                     * Connection closed or lost. Reaction depends on the circumstances
                     * why the connection was closed.
                     */
                    this.#socket.addEventListener("close", () => {
                        this.#socket = undefined;

                        // Case 1: The connection never got established. The outer method
                        // is therefore still waiting for the promise to resolve or reject.
                        if (this.#status === "connecting") {
                            reject(new Error(i18n.value.Error.WebSocket.Failed));
                        };

                        // Case 2: External caller deliberately wanted to disconnect.
                        if (this.#status === "disconnected") return;

                        // Case 3: The connection got lost. The other method is therefore
                        // not executing, anymore. Schedule a new JavaScript task (not a
                        // microtask, since we are already processing the microtasks of
                        // the current task here) to reconnect.
                        window.setTimeout(async () => {
                            await this.#setConnectionStatus("disconnected");

                            try {
                                await this.connect();
                            } catch (error) {
                                console.error(error);
                                if (this.#errorHandler) await this.#errorHandler(error as Error);
                            }
                        }, 0);

                    /**
                     * Generic WebSocket error. Will be logged and passed to the error handler.
                     */
                    this.#socket.addEventListener("error", async (error: Event) => {
                        console.error(error);
                        if (this.#errorHandler) await this.#errorHandler(error);
                    });

                    /**
                     * Message received. Will be passed to the appropriate message handler.
                     */
                    this.#socket.addEventListener("message", async (event: MessageEvent) => {
                        try {
                            const message = JSON.parse(event.data);
                            if (!message.action) throw new Error(i18n.value.Error.WebSocket.ActionMissing);

                            if (isWebSocketServerErrorMessage(message)) {
                                const error = new WebSocketServerError(
                                    formatWebSocketServerErrorMessage(message.payload),
                                    message.payload ?? [],
                                    message,
                                );

                                console.error(error);
                                if (this.#errorHandler) await this.#errorHandler(error);
                                return;
                            }

                            const handler = this.#messageHandlers.get(message.action);

                            if (!handler) {
                                const errorText = _(i18n.value.Error.WebSocket.NoMessageHandler, { action: message.action });
                                console.warn(errorText, message);
                                throw new Error(errorText);
                            }

                            await handler(message);
                        } catch (error) {
                            console.error(error);
                            if (this.#errorHandler) await this.#errorHandler(error as Error);
                        }
                    });
                });
            } catch (error) {
                lastError = error;
            }

            if (this.#status === "connected") return;

            await this.#setConnectionStatus("wait_before_retry", delayMs / 1000);
            await new Promise(resolve => setTimeout(resolve, delayMs));
            delayMs *= 2;

            console.warn(_(i18n.value.Error.WebSocket.Retry, {
                n: attempt,
                m: MAX_ATTEMPTS,
                s: this.#url,
            }));
        }

        await this.#setConnectionStatus("disconnected");
        if (lastError instanceof Error) throw lastError;
        throw new Error(i18n.value.Error.WebSocket.Failed);
    }

    /**
     * Disconnect from the server and don't try to reconnect until `connect()`
     * is called again.
     */
    async disconnect() {
        if (!this.#socket) return;

        await this.#setConnectionStatus("disconnected");
        this.#socket.close();
    }

    /**
     * Send message to the server, if the connection is established. Otherwise queue
     * the message to be sent once the connection comes back.
     *
     * @param message Message to be sent
     */
    async send(message: SentMessages) {
        if (this.#status === "connected" && this.#socket) {
            this.#send(message);
        } else {
            this.#messageQueue.push(message);
        }
    }

    /**
     * Internal utility method to actually serialize and send a message to the server.
     * Does nothing, when there is no connection.
     *
     * @param message Message to be sent
     */
    async #send(message: SentMessages) {
        if (!this.#socket) return;
        const json = JSON.stringify(message);
        this.#socket.send(json);
    }
}

/**
 * WebSocket connection status:
 *
 * - `disconnected`:      No connection to the server, not retrying
 * - `connecting`:        Trying to connect right now
 * - `connected`:         Connected to the server
 * - `wait_before_retry`: Waiting before retrying to connect
 */
export type WSConnectionStatus = "disconnected" | "connecting" | "connected" | "wait_before_retry";

/**
 * Event callback for WebSocket connection status changes.
 *
 * @param status Connection status
 * @param reconnectInSec Number of seconds until reconnect, when the connection is lost
 */
export type WSConnectionStatusListener = (status: WSConnectionStatus, reconnectInSec: number) => void|Promise<void>;

/**
 * Event callback for generic WebSocket errors.
 */
export type WSErrorHandler = (error: Event | Error) => void|Promise<void>;

/**
 * Unique string to distinguish different message types.
 */
export type WebSocketMessageAction = string;

/**
 * Base-type for a WebSocket message. The only requirement is, that each sent or
 * received WebSocket message is an object with an `action` property to distinguish
 * the message type. Messages will be serialized as JSON over the wire.
 */
export interface WebSocketMessage { action: WebSocketMessageAction };

/**
 * Handler function to handle received messages of a given type.
 */
export type WebSocketMessageHandler<MessageType extends WebSocketMessage = any> = (message: MessageType) => void | Promise<void>;

/**
 * TypeScript black magic!
 *
 * Helper to narrow down the message union to the specific message with the matching action.
 * If the union can't be resolved (e.g. it is a raw WebSocketMessage), it returns the base type
 * intersected with the action literal type.
 */
type ExtractMessageByAction<
    Messages extends WebSocketMessage,
    Action extends string
> = [Extract<Messages, { action: Action }>] extends [never]
    ? Messages & { action: Action }
    : Extract<Messages, { action: Action }>;

type WebSocketServerErrorDetail = {
    type?: string;
    msg?: string;
    loc?: unknown[];
};

type WebSocketServerErrorMessage = WebSocketMessage & {
    action: "error";
    payload?: WebSocketServerErrorDetail[];
};

class WebSocketServerError extends Error {
    payload: WebSocketServerErrorDetail[];

    constructor(message: string, payload: WebSocketServerErrorDetail[] = [], cause?: unknown) {
        super(message, { cause });
        this.name = "WebSocketServerError";
        this.payload = payload;
    }
}

function isWebSocketServerErrorMessage(message: unknown): message is WebSocketServerErrorMessage {
    return typeof message === "object"
        && message !== null
        && "action" in message
        && message.action === "error";
}

function formatWebSocketServerErrorMessage(payload?: WebSocketServerErrorDetail[]): string {
    if (!Array.isArray(payload) || !payload.length) {
        return i18n.value.Error.WebSocket.UnknownError;
    }

    return payload.map(({ type, msg, loc }) => {
        const reason = msg || i18n.value.Error.WebSocket.UnknownError;
        const suffix = Array.isArray(loc) && loc.length ? ` (${loc.map(String).join(".")})` : "";
        return type ? `${reason} [${type}]${suffix}` : `${reason}${suffix}`;
    }).join("\n");
}
