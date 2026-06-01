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
Semantic navigation bar wrapper based on DaisyUI classes.
-->

<script lang="ts">
    import type {Snippet} from "svelte";

    interface Props {
        class?: string;
        children?: Snippet;
    }

    let {
        class: className = "",
        children,
        ...props
    }: Props = $props();

    const navbarClass = $derived(
        [
            "navbar",
            "border-0",
            "bg-base-100/85",
            "backdrop-blur-md",
            className,
        ].filter(Boolean).join(" ")
    );
</script>

<div class={navbarClass} {...props}>
    {@render children?.()}
</div>
