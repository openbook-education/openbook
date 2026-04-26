/*
 * OpenBook: Interactive Online Textbooks
 * © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import {getOptions} from "./_options.js";
import path         from "node:path";
import shelljs      from "shelljs";

const options = getOptions();

for (let outfile of options.outfiles) {
    shelljs.rm("-R", path.join(path.dirname(outfile), "bundle.*"));
}
