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
        PageNotFound: {
            Title:    "Page not found",
            Message1: "We are terribly sorry, but the requested page <b>$url$</b> cannot be found.",
            Message2: 'Maybe go back to the <a href="#/">home page</a> and grab some other cheese, instead?',
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
