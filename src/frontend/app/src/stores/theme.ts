/*
 * OpenBook: Interactive Online Textbooks
 * © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

// import {i18n}          from "./i18n.js";
import {WritableStore} from "../utils/store.js";

export type ThemeName  = string;
export type ThemeLabel = string;
export type ThemeType  = "light" | "dark" | "other";
export type Theme      = {name: ThemeName, label: ThemeLabel, type: ThemeType};

/**
 * Static list of all available themes
 */
export const availableThemes: Theme[] = [
    {
        name:  "OpenBook-Light",
        label: "Light", //i18n.value.ApplicationFrame.Menu.Theme.Light,
        type:  "light",
    },
    {
        name:  "dim",
        label: "Dark", //i18n.value.ApplicationFrame.Menu.Theme.Dark,
        type:  "dark",
    },
    {
        name:  "nord",
        label: "Nord", //i18n.value.ApplicationFrame.Menu.Theme.Nord,
        type:  "other",
    },
    {
        name:  "aqua",
        label: "Aqua", //i18n.value.ApplicationFrame.Menu.Theme.Aqua,
        type:  "other",
    },
];

/**
 * Writable store to change the current theme. Saves the selected theme in the
 * browser's local storage and automatically chooses the default light or dark
 * theme based on browser preferences.
 */
class ThemeStore extends WritableStore<ThemeName> {
    htmlElement = document.querySelector("html") as HTMLHtmlElement;

    /**
     * Initialize with the current theme from local storage or the browser preferences.
     */
    constructor() {
        let value = localStorage.getItem("theme") || getDefaultTheme();
        super(value);
        this.htmlElement.dataset.theme = value;
    }

    /**
     * Set new value.
     */
    set(value: ThemeName) {
        localStorage.setItem("theme", value);
        this.htmlElement.dataset.theme = value;
        super.set(value);
    }
}

/**
 * Currently active theme.
 */
export const theme = new ThemeStore();

/**
 * Determine the default theme, light or dark, depending in the browser's preferences.
 */
function getDefaultTheme(): ThemeName {
    const dark  = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    const type  = dark ? "dark" : "light";
    const theme = availableThemes.find(t => t.type === type) || availableThemes[0] as Theme;

    return theme.name;
}
