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
Semantic title element for menu sections.
-->

<script lang="ts">
    import type {Snippet} from "svelte";

    interface Props {
        class?:    string;
        children?: Snippet;
    }

    let {
        class: className = "",
        children,
    }: Props = $props();

    const mergedClass = $derived(["menu-title", className].filter(Boolean).join(" "));
</script>

<div class={mergedClass}>
    {@render children?.()}
</div>
