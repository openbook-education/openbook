/*
 * OpenBook: Interactive Online Textbooks
 * © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import {ReadableStore} from "../utils/store.js";

/**
 * Full-screen error message
 */
export type ErrorMessage = {
    type:     "NoError" | "NotFound" | "NetworkError" | "PermissionDenied" | "OperationFailed";
    heading:  string;
    message?: string;
};

/**
 * Readable store for a full-screen error message.
 */
class ErrorStore extends ReadableStore<ErrorMessage> {
    constructor() {
        super({type: "NoError", heading: "", message: ""});
    }

    /**
     * Replace current content with a full-screen error message.
     */
    show(type: ErrorMessage["type"], heading: string, message?: string) {
        this.set({type, heading, message: message || ""});
    }

    /**
     * Hide currently visible error, if any.
     */
    hide() {
        this.set({type: "NoError", heading: "", message: ""});
    }
}

/**
 * Full-screen error messsage.
 */
export const error = new ErrorStore();
