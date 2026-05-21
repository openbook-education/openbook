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
 * HTTP status codes eligible for automatic retries.
 */
const RETRY_STATUS_CODES = new Set([408, 420, 429]);

/**
 * Initial delay after the first failed attempt.
 * Will be doubled for each successive retry.
 */
const BASE_DELAY_MS = 250;

/**
 * Wrapper around the regular `fetch()` function that implements exponential backoff
 * in case of connection errors responses indicating too many requests.
 */
export async function fetchWithRetry(request: Request): Promise<Response> {
    let lastError: unknown = null;
    let response: Response|undefined;
    let delayMs = BASE_DELAY_MS;

    for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
        lastError = null;

        try {
            const response = await fetch(request.clone());
            if (!RETRY_STATUS_CODES.has(response.status)) break;
        } catch (error) {
            lastError = error;
        }

        await new Promise(resolve => setTimeout(resolve, delayMs));
        delayMs *= 2;

        console.warn(_(i18n.value.Error.RequestFailed.Retry, {
            n: attempt,
            m: MAX_ATTEMPTS
        }));
    }

    if (response) return response;
    if (lastError instanceof Error) throw lastError;
    throw new Error(i18n.value.Error.RequestFailed.Failed);
}
