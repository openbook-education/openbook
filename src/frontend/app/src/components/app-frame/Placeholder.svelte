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
Placeholder for the start page until we have proper content to show.
 -->
<script lang="ts">
    import {i18n}    from "../../stores/i18n.js";    
    import backend   from "../../backend.js";

    // Check backend status every three seconds
    let backendStatusText  = $state(i18n.value.Placeholder.BackendStatus.Checking);
    let backendStatusColor = $state("grey");

    async function checkBackendStatus() {
        try {
            let health = await backend.core.websites.coreSitesHealthRetrieve();
            console.log("Received backend health status", health.status);
    
            backendStatusText  = i18n.value.Placeholder.BackendStatus.Online;
            backendStatusColor = "green";
        } catch (error) {
            console.error(error);

            backendStatusText  = i18n.value.Placeholder.BackendStatus.Offline;
            backendStatusColor = "red";
        }
    }

    setInterval(checkBackendStatus, 3000);
</script>

<div>
    <h1>{$i18n.Placeholder.Title}</h1>

    <p class="underConstruction">
        {@html $i18n.Placeholder.Text}
    </p>

    <p>
        Backend Status: <span style:color={backendStatusColor}>{backendStatusText}</span>
    </p>

    <img src="placeholder.svg" alt="">
</div>

<style>
    div {
        flex: 1;
        align-self: center;
        text-align: center;
    }

    img {
        display: block;
        width: 30em;
        max-width: 100%;
        margin-top: 3em;
    }

    .underConstruction {
        color: darkred; 
    }
</style>