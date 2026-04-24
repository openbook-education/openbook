<!--
OpenBook: Interactive Online Textbooks - Server
© 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
-->

<!--
@component
Simple 404 not found page
 -->
<script lang="ts">
    import {i18n, _}  from "../../../stores/i18n.js";
    import {router} from "svelte-spa-router";
</script>

<div>
    <h1>{$i18n.Error404.Title}</h1>
    <p>
        {@html _($i18n.Error404.Message1, {url: router.location})}
    </p>
    <p>
        {@html $i18n.Error404.Message2}
    </p>
    <img src="page-not-found.png" alt="">
</div>

<style>
    div {
        flex: 1;
        align-self: center;
    }

    img {
        display: block;
        width: 30em;
        max-width: 100%;
        margin-top: 3em;
    }
</style>
