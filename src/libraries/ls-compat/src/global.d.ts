/*
 * OpenBook: Interactive Online Textbooks
 * © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

/**
 * Fix TypeScript error for image imports. These are already handled by
 * esbuild, but we need to tell TypeScript, too.
 */

// Side-effect imports
declare module "*.css";
declare module "*.svelte";

// Value imports
declare module "*.css" {
    const value: string;
    export default value;
}

declare module "*.png" {
    const value: string;
    export default value;
}

declare module "*.jpg" {
    const value: string;
    export default value;
}

declare module "*.svg" {
    const value: string;
    export default value;
}
