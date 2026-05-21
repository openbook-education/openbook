<!--
OpenBook: Interactive Online Textbooks
© 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
-->

<!--
@component
A simple hello world custom element to test building and using the library.
Will be replaced with proper web components later.
-->

<svelte:options customElement="ob-hello" />

<script lang="ts">
    let {
        name = "Web Component built with Svelte",
        onmouseover,
        onmouseleave,
        onfocus,
    } = $props();
</script>

<p {onmouseover} {onmouseleave} {onfocus}>
    Hello {name}!
</p>

<style>
    p {
        color: gold;
    }
</style>