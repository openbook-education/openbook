/*
 * OpenBook: Interactive Online Textbooks
 * © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

// @ts-expect-error: Could not find a declaration file
import TinyMDE from "tiny-markdown-editor/dist/tiny-mde.js";
import "tiny-markdown-editor/dist/tiny-mde.css";

import * as ckeditor from 'ckeditor5';
import "ckeditor5/ckeditor5.css";

import "./style.css";

(window as any).TinyMDE  = TinyMDE;
(window as any).ckeditor = ckeditor;
