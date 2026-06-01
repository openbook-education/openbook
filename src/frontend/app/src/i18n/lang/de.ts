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
    ApplicationFrame: {
        Search: {
            Placeholder: "Suche",
        },
        Menu: {
            Title: "Menü",
            Theme: {
                Title: "Farbschema",
                Light: "Hell",
                Dark:  "Dunkel",
                Nord:  "Nord",
                Aqua:  "Aqua",
            },
            Account: {
                Title:   "Benutzerkonto",
                Profile: "Profil bearbeiten",
                Logout:  "Logout",
            }
        },
    },

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
        Page: {
            NetworkError: {
                Title:    "Netzwerkfehler",
                Message1: "Das Internet hat sich wohl eine Kaffeepause gegönnt.",
                Message2: "Überprüfe deine Verbindung und versuche es erneut — oder gib der KI die Schuld.",
            },

            NotFound: {
                Title:    "Seite nicht gefunden",
                Message1: "Es sieht so aus, als hätte diese Seite eine Lernpause gemacht und sich verflüchtigt.",
                Message2: "Lass uns dich zurück zu deiner Lernreise bringen.",
            },

            OperationFailed: {
                Title:    "Operation fehlgeschlagen",
                Message1: "Selbst unsere KI versteht nicht, was hier schiefgelaufen ist.",
                Message2: "Bitte versuche es erneut, oder kontaktiere den Support, wenn das Problem weiterhin besteht.",
            },

            PermissionDenied: {
                Title:    "Zugriff verweigert",
                Message1: "Es sieht so aus, als hättest du noch keinen VIP-Zugang zu diesem Bereich.",
                Message2: "Kontaktiere deinen Dozenten, wenn du glaubst, dass du Zugriff haben solltest.",
            },

            Actions: {
                Retry:        "Erneut versuchen",
                GoToHomepage: "Zur Startseite",
                GoToLibrary:  "Zur Bibliothek",
            },

            Support: {
                Title:  "Brauchst du Hilfe beim Finden von Inhalten?",
                Text:   "Unser KI-Assistent zeigt dir den richtigen Weg.",
                Action: "KI-Assistent fragen",
            },
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
