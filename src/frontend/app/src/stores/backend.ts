/*
 * OpenBook: Interactive Online Textbooks
 * © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

// Wrapper for all REST API calls
//  - Centralize error handling (by updating nearby stores like Toast/Error Store)
//  - Caching and SWR pattern:
//      - Cache all responses with bounded LRU strategy and key strings
//      - Eagerly return cached responses
//      - Refetch data in background
//  - Rerender affected views after data fetch/mutations
