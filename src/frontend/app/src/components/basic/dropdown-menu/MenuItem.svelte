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
Semantic menu item element.
-->

<script lang="ts">
    import type {Snippet} from "svelte";

    type ButtonType = "button" | "submit" | "reset";

    interface Props {
        class?:     string;
        itemClass?: string;
        href?:      string;
        type?:      ButtonType;
        children?:  Snippet;
    }

    let {
        class: className = "",
        itemClass        = "",
        type             = "button",
        href,
        children,
        ...restProps
    }: Props & Record<string, unknown> = $props();

    const isInteractive = $derived(
        Boolean(href || itemClass || Object.keys(restProps).length)
    );
</script>

<li class={className}>
    {#if href}
        <a
            {href}
            class = {itemClass}
            {...restProps}
        >
            {@render children?.()}
        </a>
    {:else if isInteractive}
        <button
            {type}
            class = {itemClass}
            {...restProps}
        >
            {@render children?.()}
        </button>
    {:else}
        {@render children?.()}
    {/if}
</li>
