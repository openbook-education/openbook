<!--
OpenBook: Interactive Online Textbooks
© 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
-->

<!--
@component
Semantic dropdown menu wrapper based on DaisyUI classes.

TODO: Implement keyboard navigation with arrow keys
-->

<script lang="ts">
    import type {Snippet} from "svelte";

    type Align    = "start" | "end";
    type Side     = "top" | "bottom" | "left" | "right";
    type MenuSize = "" | "sm" | "md" | "lg";

    interface Props {
        class?:          string;
        align?:          Align;
        side?:           Side;
        open?:           boolean;
        hover?:          boolean;
        menuHorizontal?: boolean;
        menuSize?:       MenuSize;
        contentClass?:   string;
        contentRole?:    string;
        summaryClass?:   string;
        trigger?:        Snippet;
        children?:       Snippet;
    }

    let {
        align,
        side,
        open,
        hover            = false,
        menuHorizontal   = false,
        menuSize         = "",
        contentClass     = "",
        contentRole      = "menu",
        summaryClass     = "",
        class: className = "",
        trigger,
        children,
    }: Props = $props();

    const detailsClass = $derived(
        [
            "dropdown",
            align ? `dropdown-${align}` : "",
            side  ? `dropdown-${side}`  : "",
            hover ? "dropdown-hover"    : "",
            className,
        ].filter(Boolean).join(" ")
    );

    const menuClass = $derived(
        [
            "dropdown-content",
            "menu",
            menuSize       ? `menu-${menuSize}` : "",
            menuHorizontal ? "menu-horizontal"  : "",
            contentClass,
        ].filter(Boolean).join(" ")
    );
</script>

<details class={detailsClass} {open}>
    <summary class={summaryClass}>
        {@render trigger?.()}
    </summary>

    <ul class={menuClass} role={contentRole}>
        {@render children?.()}
    </ul>
</details>
