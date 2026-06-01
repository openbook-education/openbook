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
Semantic wrapper for DaisyUI's hover-3d utility.
-->

<script lang="ts">
    import type {Snippet} from "svelte";

    interface Props {
        class?:    string;
        href?:     string;
        children?: Snippet;
    }

    let {
        class: className = "",
        href = "",
        children,
    }: Props = $props();

    const rootClass = $derived(
        ["hover-3d", href ? "cursor-pointer" : "", className].filter(Boolean).join(" ")
    );
</script>

{#if href}
    <a class={rootClass} {href}>
        {@render children?.()}

        <div aria-hidden="true"></div>
        <div aria-hidden="true"></div>
        <div aria-hidden="true"></div>
        <div aria-hidden="true"></div>
        <div aria-hidden="true"></div>
        <div aria-hidden="true"></div>
        <div aria-hidden="true"></div>
        <div aria-hidden="true"></div>
    </a>
{:else}
    <div class={rootClass}>
        {@render children?.()}

        <div aria-hidden="true"></div>
        <div aria-hidden="true"></div>
        <div aria-hidden="true"></div>
        <div aria-hidden="true"></div>
        <div aria-hidden="true"></div>
        <div aria-hidden="true"></div>
        <div aria-hidden="true"></div>
        <div aria-hidden="true"></div>
    </div>
{/if}
