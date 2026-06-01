/*
 * OpenBook: Interactive Online Textbooks
 * © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import ApplicationFrame from "../../components/ApplicationFrame.svelte";

// This is the master language. Therefore no type import here.
export default {
    ApplicationFrame: {
        Search: {
            Placeholder: "Search",
        },
        Menu: {
            Title: "Menu",
            Theme: {
                Title: "Theme",
                Light: "Light",
                Dark:  "Dark",
                Nord:  "Nord",
                Aqua:  "Aqua",
            },
            Account: {
                Title: "User Account",
                Profile: "Profile",
                Logout:  "Logout",
            }
        }
    },

    Placeholder: {
        Title: "OpenBook",
        Text:  "Under Construction!",

        BackendStatus: {
            Checking: "Checking Now …",
            Online:   "Online",
            Offline:  "Offline",
        },
    },

    Error: {
        Page: {
            NetworkError: {
                Title:    "Network error",
                Message1: "Looks like the internet decided to take a coffee break.",
                Message2: "Check your connection and try again — or blame the AI.",
            },

            NotFound: {
                Title:    "Page not found",
                Message1: "It looks like this page took a study break and wandered off.",
                Message2: "Let's get you back to your learning journey.",
            },

            OperationFailed: {
                Title:    "Operation failed",
                Message1: "Even our AI doesn't understand what went wrong here.",
                Message2: "Please try again, or contact support if the problem persists.",
            },

            PermissionDenied: {
                Title:    "Permission denied",
                Message1: "Looks like you don't have a VIP pass to this section—yet.",
                Message2: "Contact your instructor if you think you should have access.",
            },

            Actions: {
                Retry:        "Retry",
                GoToHomepage: "Go to Homepage",
                GoToLibrary:  "Go to Library",
            },

            Support: {
                Title:  "Need help finding something?",
                Text:   "Our AI assistant can point you in the right direction.",
                Action: "Ask AI Assistant",
            },
        },

        RequestFailed: {
            Retry:  "Retrying request: $n$ from $m$",
            Failed: "Request failed!",
        },

        Backend: {
            NotFound:         "Object Not Found",
            PermissionDenied: "Permission Denied",
            OperationFailed:  "Operation Failed",
        }
    }
};
