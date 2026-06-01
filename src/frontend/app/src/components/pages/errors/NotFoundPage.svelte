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
Dedicated full-screen page for not-found errors.
 -->

<script lang="ts">
    import {i18n}    from "../../../stores/i18n.js";
    import ErrorPage from "./ErrorPage.svelte";
</script>

<ErrorPage
    title                = {$i18n.Error.Page.NotFound.Title}
    messageHtml          = {$i18n.Error.Page.NotFound.Message1}
    statusCode           = "404"
    imageSrc             = "error/not-found.png"
    detailsHtml          = {$i18n.Error.Page.NotFound.Message2}
    imageAlt             = {$i18n.Error.Page.NotFound.Title}
    primaryActionLabel   = {$i18n.Error.Page.Actions.GoToLibrary}
    primaryActionHref    = "#/library"
    secondaryActionLabel = {$i18n.Error.Page.Actions.GoToHomepage}
    secondaryActionHref  = "#/"
/>
