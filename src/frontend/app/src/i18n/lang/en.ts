/*
 * OpenBook: Interactive Online Textbooks
 * © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

// This is the master language. Therefore no type import here.
export default {
    ApplicationFrame: {
        PaneVisibility: {
            AriaLabel: "Visible panes",
            Chat:      "Elisa",
            Content:   "Content",
            Both:      "Both",
        },

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
            Language: {
                Title: "Language"
            },
            Account: {
                Title: "User Account",
                Profile: "User Profile",
                Logout:  "Logout",
                Login:   "Login",
                SignUp:  "Sign Up",
            }
        }
    },

    Home: {
        Title: "Home",
    },

    AiChat: {
        PanelAriaLabel: "Elisa AI chat",
        StreamingResponseAriaLabel: "Streaming response",
        MessageImageAlt: "Elisa's response",
        StreamingUpdate: "Streaming update",

        Header: {
            Title:           "Elisa AI Assistant",
            Description:     "Ask questions, explore ideas, or draft content.",
            MessageSingular: "message",
            MessagePlural:   "messages",
        },

        Connection: {
            Live:         "Online",
            Connecting:   "Connecting",
            Reconnecting: "Reconnecting",
            Offline:      "Offline",
        },

        EmptyState: {
            Eyebrow:                "Start here",
            Title:                  "Ask a question",
            Description:            "Ask for a summary, rewrite, comparison, or next step.",
            GoodPromptsTitle:       "Try asking",
            GoodPromptsDescription: "Summarize this chapter, turn notes into tasks, explain a concept, or compare options.",
            BestFlowTitle:          "Tip",
            BestFlowDescription:    "Use Shift+Enter for multiple lines. You can send the next message when the current reply is done.",
        },

        MessageTitle: {
            AssistantStatus: "Elisa status",
            Status:          "Status",
            ReasoningNote:   "Reasoning note",
            Action:          "Action",
            You:             "You",
            OpenBookAI:      "Elisa",
        },

        MessageType: {
            Status:  "Status",
            Thought: "Reasoning note",
            Action:  "Action",
            System:  "System",
        },

        MessageFormat: {
            Json:  "JSON",
            Image: "Image",
        },

        SystemLabel: {
            CriticalNotice: "Critical notice",
            Error:          "Error",
            Warning:        "Warning",
            Notice:         "System notice",
        },

        Reasoning: {
            ShowNote:       "Show reasoning note",
            StillStreaming: "Reasoning note is still streaming",
        },

        GuardRails: {
            Label: "Guard rails:",
        },

        Composer: {
            Label:              "Message the Elisa AI assistant",
            PlaceholderOnline:  "Ask Elisa to explain, summarize, or draft something...",
            PlaceholderOffline: "Chat is offline. Reconnect to continue.",
            HintWaiting:        "Wait for the current reply to finish.",
            HintReady:          "Press Enter to send, Shift+Enter for a new line.",
            HintOffline:        "Connection required before messages can be sent.",
            Clear:              "Clear",
            Send:               "Send",
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

        WebSocket: {
            Retry:            "Retrying to connect to WebSocket server $s$; attempt $n$ from $m$",
            Failed:           "WebSocket connection failed!",
            ActionMissing:    "Received WebSocket message is missing the 'action' property which defines the message type.",
            NoMessageHandler: "No handler method found for WebSocket message of type '$action$'.",
            UnknownError:     "An unknown error occurred during the WebSocket communication with the backend.",
        },

        Backend: {
            NotFound:         "Object Not Found",
            PermissionDenied: "Permission Denied",
            OperationFailed:  "Operation Failed",
        }
    }
};
