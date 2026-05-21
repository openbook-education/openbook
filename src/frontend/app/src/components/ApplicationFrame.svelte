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
Root component of the application which defines the global application UI.
-->

<script lang="ts">
    import Router  from "svelte-spa-router";
    import routes  from "./routes.js";
    import {error} from "../stores/error.js";

    /**
     * Hidden previously shown error message, when navigating to a new page.
     */
    function onRouteLoaded() {
        error.hide();
    }
</script>

<main class="flex flex-1 flex-col">
    <Router {routes} {onRouteLoaded}/>
</main>
