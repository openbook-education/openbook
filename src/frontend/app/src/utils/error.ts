/*
 * OpenBook: Interactive Online Textbooks
 * © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

export class NotFoundError extends Error {
    public readonly cause?: unknown;

    /**
     * Error indicating that a requested resource does not exist.
     *
     * @param message Optional custom error message.
     * @param cause Optional original error that caused this error.
     */
    public constructor(message = "Resource not found", cause?: unknown) {
        super(message);

        this.name  = "NotFound";
        this.cause = cause;

        Object.setPrototypeOf(this, new.target.prototype);
    }
}

export class NetworkError extends Error {
    public readonly cause?: unknown;

    /**
     * Error indicating a transport-level problem (offline, timeout, DNS, etc.).
     *
     * @param message Optional custom error message.
     * @param cause Optional original error that caused this error.
     */
    public constructor(message = "Network request failed", cause?: unknown) {
        super(message);

        this.name  = "NetworkError";
        this.cause = cause;

        Object.setPrototypeOf(this, new.target.prototype);
    }
}

export class PermissionDeniedError extends Error {
    public readonly cause?: unknown;

    /**
     * Error indicating that the current user is not allowed to perform the action.
     *
     * @param message Optional custom error message.
     * @param cause Optional original error that caused this error.
     */
    public constructor(message = "Permission denied", cause?: unknown) {
        super(message);

        this.name  = "PermissionDenied";
        this.cause = cause;

        Object.setPrototypeOf(this, new.target.prototype);
    }
}

export class OperationFailedError extends Error {
    public readonly cause?: unknown;

    /**
     * Error indicating a domain or business operation failed for a non-network reason.
     *
     * @param message Optional custom error message.
     * @param cause Optional original error that caused this error.
     */
    public constructor(message = "Operation failed", cause?: unknown) {
        super(message);

        this.name = "OperationFailed";
        this.cause = cause;

        Object.setPrototypeOf(this, new.target.prototype);
    }
}

export type AppError = NotFoundError | NetworkError | PermissionDeniedError | OperationFailedError;
export type AppErrorKind = "NotFound" | "NetworkError" | "PermissionDenied" | "OperationFailed";

/**
 * Options used when creating or throwing application-specific errors.
 */
export interface AppErrorOptions {
    /**
     * Optional custom message for the thrown error.
     */
    message?: string;

    /**
     * Optional original error that caused the current failure.
     */
    cause?: unknown;
}

/**
 * Throws one of the application-specific error classes based on the given kind.
 *
 * @param kind The error kind to throw.
 * @param messageOrOptions Optional message or options for the thrown error.
 * @throws NotFoundError
 * @throws NetworkError
 * @throws PermissionDeniedError
 * @throws OperationFailedError
 */
export function throwAppError(kind: AppErrorKind, messageOrOptions?: string | AppErrorOptions): never {
    function _normalizeOptions(messageOrOptions?: string | AppErrorOptions): AppErrorOptions {
        if (typeof messageOrOptions === "string") {
            return { message: messageOrOptions };
        }

        return messageOrOptions ?? {};
    }

    const { message, cause } = _normalizeOptions(messageOrOptions);

    switch (kind) {
        case "NotFound":
            throw new NotFoundError(message, cause);
        case "NetworkError":
            throw new NetworkError(message, cause);
        case "PermissionDenied":
            throw new PermissionDeniedError(message, cause);
        case "OperationFailed":
            throw new OperationFailedError(message, cause);
    }
}

/**
 * Rethrows an existing error as one of the application-specific error classes.
 *
 * The original error is preserved as the `cause`.
 *
 * @param kind The app error kind to throw.
 * @param cause The original error to attach as the cause.
 * @param message Optional custom message for the wrapped error.
 */
export function rethrowAppError(kind: AppErrorKind, cause: unknown, message?: string): never {
    throwAppError(kind, {
        message,
        cause,
    });
}
