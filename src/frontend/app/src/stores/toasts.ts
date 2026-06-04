/*
 * OpenBook: Interactive Online Textbooks
 * © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import { ReadableStore } from "../utils/store.js";

/**
 * A short information, warning or error message.
 */
export type Toast = {
    id:      string;
    type:    "info" | "warning" | "error" | "success";
    message: string;
}

/**
 * How long toast messages will be shown.
 */
const TOAST_DURATION_MS = 10_000;

/**
 * Readable store for toast messages, including a method for external clients to
 * add new toasts.
 */
class ToastStore extends ReadableStore<Toast[]> {
    constructor() {
        super([]);
    }

    /**
     * Show a new toast message
     *
     * @param type Message type
     * @param message Message text
     */
    show(type: Toast["type"], message: string): void {
        const toast: Toast = {
            id:      Math.random().toString(36).substring(2, 18),
            type:    type,
            message: message,
        }

        this.update(currentList => [...currentList, toast]);

        window.setTimeout(() => {
            this.update(currentList => currentList.filter(t => t.id !== toast.id));
        }, TOAST_DURATION_MS);
    }
}

/**
 * Information, warning and error messages that will be shown as a temporary toast.
 */
export const toasts = new ToastStore();
