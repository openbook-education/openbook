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
        PaneVisibility: {
            AriaLabel: "Sichtbare Bereiche",
            Chat:      "Elisa",
            Content:   "Inhalt",
            Both:      "Beide",
        },

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
            Language: {
                Title: "Sprache"
            },
            Account: {
                Title:   "Benutzerkonto",
                Profile: "Benutzerprofil",
                Logout:  "Logout",
                Login:   "Login",
                SignUp:  "Registrieren",
            }
        },
    },

    Home: {
        Title: "Startseite",
    },

    AiChat: {
        PanelAriaLabel: "Elisa KI-Chat",
        StreamingResponseAriaLabel: "Antwort wird übertragen",
        MessageImageAlt: "Antwort von Elisa",
        StreamingUpdate: "Laufende Aktualisierung",

        Header: {
            Title:           "Elisa KI-Assistent",
            Description:     "Stelle Fragen, sammle Ideen oder entwirf Inhalte.",
            MessageSingular: "Nachricht",
            MessagePlural:   "Nachrichten",
        },

        Connection: {
            Live:         "Online",
            Connecting:   "Verbinde",
            Reconnecting: "Verbinde erneut",
            Offline:      "Offline",
        },

        EmptyState: {
            Eyebrow:                "Los geht's",
            Title:                  "Stell eine Frage",
            Description:            "Bitte um eine Zusammenfassung, Umarbeitung, einen Vergleich oder den nächsten Schritt.",
            GoodPromptsTitle:       "Zum Beispiel",
            GoodPromptsDescription: "Fasse dieses Kapitel zusammen, verwandle Notizen in Aufgaben, erkläre ein Konzept oder vergleiche Optionen.",
            BestFlowTitle:          "Hinweis",
            BestFlowDescription:    "Verwende Umschalt+Enter für mehrere Zeilen. Du kannst die nächste Nachricht senden, sobald die aktuelle Antwort fertig ist.",
        },

        MessageTitle: {
            AssistantStatus: "Status von Elisa",
            Status:          "Status",
            ReasoningNote:   "Denknotiz",
            Action:          "Aktion",
            You:             "Du",
            OpenBookAI:      "Elisa",
        },

        MessageType: {
            Status:  "Status",
            Thought: "Denknotiz",
            Action:  "Aktion",
            System:  "System",
        },

        MessageFormat: {
            Json:  "JSON",
            Image: "Bild",
        },

        SystemLabel: {
            CriticalNotice: "Kritischer Hinweis",
            Error:          "Fehler",
            Warning:        "Warnung",
            Notice:         "Systemhinweis",
        },

        Reasoning: {
            ShowNote:       "Denknotiz anzeigen",
            StillStreaming: "Denknotiz wird noch übertragen",
        },

        GuardRails: {
            Label: "Leitplanken:",
        },

        Composer: {
            Label:              "Nachricht an den Elisa KI-Assistenten",
            PlaceholderOnline:  "Bitte Elisa, etwas zu erklären, zusammenzufassen oder zu entwerfen...",
            PlaceholderOffline: "Der Chat ist offline. Stelle die Verbindung wieder her, um weiterzumachen.",
            HintWaiting:        "Warte, bis die aktuelle Antwort fertig ist.",
            HintReady:          "Drücke Enter zum Senden, Umschalt+Enter für eine neue Zeile.",
            HintOffline:        "Zum Senden von Nachrichten ist eine Verbindung erforderlich.",
            Clear:              "Leeren",
            Send:               "Senden",
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

        WebSocket: {
            Retry:            "Versuche, Verbindung zum WebSocket-Server $s$ wiederherzustellen; Versuch $n$ von $m$",
            Failed:           "WebSocket-Verbindung fehlgeschlagen!",
            ActionMissing:    "Die empfangene WebSocket-Nachricht enthält kein Attribut 'action' zur Unterscheidung der Nachrichtenart.",
            NoMessageHandler: "Keine Handler-Methode gefunden für WebSocket-Nachrichtenart '$action$'.",
            UnknownError:     "Während der WebSocket-Kommunikation mit dem Backend ist ein unbekannter Fehler aufgetreten.",
        },

        Backend: {
            NotFound:         "Objekt nicht gefunden",
            PermissionDenied: "Zugriff verweigert",
            OperationFailed:  "Operation fehlgeschlagen",
        }
    },
};

export default i18n;
