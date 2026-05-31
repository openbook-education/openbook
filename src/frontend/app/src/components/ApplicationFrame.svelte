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
    import NavigationBar    from "./app-frame/NavigationBar.svelte";
    import LoadingAnimation from "./app-frame/LoadingAnimation.svelte";

    import Router           from "svelte-spa-router";
    import routes           from "./routes.js";
    import {errorPage}      from "../stores/error.js";

    /**
     * Hidden previously shown error message, when navigating to a new page.
     */
    function onRouteLoaded() {
        errorPage.hide();
    }
</script>

<NavigationBar/>

<main class="flex flex-1 flex-col -z-10">
    <svelte:boundary>
        <Router {routes} {onRouteLoaded}/>

        {#snippet pending()}
            <LoadingAnimation/>
        {/snippet}

        {#snippet failed(error, reset)}
            An error occurred: {error}

            <button onclick={reset}>Try again!</button>
        {/snippet}
    </svelte:boundary>
</main>
