/*
 * OpenBook: Interactive Online Textbooks
 * © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import concurrently from "concurrently";
import url          from "node:url";

const __dirname = url.fileURLToPath(new url.URL(".", import.meta.url));

concurrently([{
    name: "build",
    //command: `node ${path.join(__dirname, "build.js")} --watch`
    command: "npm run build",
}, {
    name:    "tsc",
    command: "tsc -w --preserveWatchOutput",
}], {
    prefix: "name",
    prefixColors: ["auto"],
    // raw: true,
});
