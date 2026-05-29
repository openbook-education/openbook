/*
 * OpenBook: Interactive Online Textbooks
 * © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import type { paths as authPaths }     from "./openapi/auth";
import type { paths as openbookPaths } from "./openapi/openbook";

import createClient                    from "openapi-fetch";
import middlewares                     from "./middleware";
import {fetchWithRetry}                from "./retry";

// Fetch backend URL
let response  = await fetch("server.url");
let baseUrl   = await response.text();

while (baseUrl.endsWith("/")) {
    baseUrl = baseUrl.slice(0, baseUrl.length - 1);
}

/**
 * Pre-instantiated client objects, generated from the OpenAPI specification.
 * The clients objects automatically use the correct base URL of the server and
 * use all required middlewares like authentication, request deduplication etc.
 */
const client = {
    auth:     createClient<authPaths>     ({baseUrl, fetch: fetchWithRetry}),
    openbook: createClient<openbookPaths> ({baseUrl, fetch: fetchWithRetry}),
};

export default client;

// Register middlewares
for (let middleware of middlewares) {
    client.auth.use(middleware);
    client.openbook.use(middleware);
}
