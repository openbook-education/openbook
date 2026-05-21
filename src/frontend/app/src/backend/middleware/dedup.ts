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
 * How long responses should be cached for request deduplication. Older responses
 * will be evicted with the next request for any endpoint.
 */
const DEDUP_TIMEOUT_MS = 5000;

/**
 * Which HTTP methods to deduplicate. Here we assume, that only GET requests shall
 * be deduplicated. Mutations (PUT, POST, PATCH, DELETE) should never be deduplicated
 * and for OPTIONS, TRACE etc. there is no benefit.
 */
const DEDUP_HTTP_METHODS = ["GET"];

type CacheKey  = string;
type CacheEntry = {ttl: number, response: Response};

const cache = new Map<CacheKey, CacheEntry>();

function getCacheKey(request: Request): CacheKey {
    return `${request.method}:${request.url}`;
}

function getTime(offset?: number): number {
    return new Date().getTime() + (offset || 0);
}

/**
 * Introduce a short-term cache to deduplicate identical requests triggered by different
 * UI components in short succession. This can happen when two components need to request
 * the same backend resource for showing their data on the same page.
 */
export default {
    async onRequest({request}) {
        // Evict outdated cache entries
        const now = getTime();

        for (let [key, entry] of cache.entries()) {
            // This works, because Map retains the insertion order
            if (entry.ttl >= now) break;
            cache.delete(key);
        }

        // Satisfy request from cache, if possible
        const cacheEntry = cache.get(getCacheKey(request));
        return cacheEntry?.response.clone();
    },

    async onResponse({request, response}) {
        if (!DEDUP_HTTP_METHODS.includes(request.method.toUpperCase())) return;

        cache.set(getCacheKey(request), {
            ttl:      getTime(DEDUP_TIMEOUT_MS),
            response: response.clone(),
        });
    },
} as Middleware;
