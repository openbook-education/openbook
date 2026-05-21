/*
 * OpenBook: Interactive Online Textbooks
 * © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import * as i18n from "./stores/i18n.js";

declare global {
    interface Window {
        /**
         * Public exports for usage in the study books
         */
        OpenBook: {
            /**
             * Get translated texts or customize the translations
             */
            i18n: typeof i18n;
        }
    }
}

window.OpenBook = {i18n};