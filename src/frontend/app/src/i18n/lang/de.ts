/*
 * OpenBook: Interactive Online Textbooks
 * © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import type {I18N} from "../index.js";

const i18n: I18N = {
    Placeholder: {
        Title: "OpenBook",
        Text:  "Achtung, Baustelle!",

        BackendStatus: {
            Checking: "Wird geprüft …",
            Online:   "Online",
            Offline:  "Offline",
        },
    },

    Error: {
        PageNotFound: {
            Title:    "Seite nicht gefunden",
            Message1: "Es tut uns fürchterlich Leid, aber die angeforderte Seite <b>$url$</b> wurde nicht gefunden.",
            Message2: 'Wollen Sie stattdessen zur <a href="#/">Startseite</a> zurückgehen und sich einen anderen Käse schnappen?',
        },

        RequestFailed: {
            Retry:  "Wiederhole Anfrage: $n$ von $m$",
            Failed: "Anfrage fehlgeschlagen!",
        },

        Backend: {
            NotFound:         "Objekt nicht gefunden",
            PermissionDenied: "Zugriff verweigert",
            OperationFailed:  "Operation fehlgeschlagen",
        }
    },
};

export default i18n;
