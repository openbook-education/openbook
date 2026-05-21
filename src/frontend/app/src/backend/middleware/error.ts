/*
 * OpenBook: Interactive Online Textbooks
 * © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import type {Middleware} from "openapi-fetch";

/**
 * Log communication errors.
 */
export default {
    /**
     * Note that this method only gets called for `TypeError`s (usually a network failure)
     * and `DOMException`s (request aborted). 4xx and 5xx status codes are treated as normal
     * responses by openapi-fetch.
     */
    async onError({error}) {
        console.error(error);
        return;
    },
} as Middleware;
