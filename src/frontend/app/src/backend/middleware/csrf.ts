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
 * Include CSRF token in each request. The token is set in a cookie by Django and must
 * be included in each request for the server to accept the request.
 */
export default {
    async onRequest({request}) {
        const csrfToken = document.cookie.match(/csrftoken=([\w]+)/)?.[1] || "";
        request.headers.set("X-CSRFToken", csrfToken);
    },
} as Middleware;
