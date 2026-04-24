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
Root component of the application which defines the global application UI.
-->

<script lang="ts">
    import Router from "svelte-spa-router";
    import routes from "./routes.js";
</script>

<main>
    <Router {routes} />
</main>

<style>
    main {
        flex: 1;

        display: flex;
        flex-direction: column;
    }
</style>