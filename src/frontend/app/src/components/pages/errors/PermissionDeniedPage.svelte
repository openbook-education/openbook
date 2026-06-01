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
Dedicated full-screen page for authorization errors.
 -->

<script lang="ts">
    import {i18n}    from "../../../stores/i18n.js";
    import ErrorPage from "./ErrorPage.svelte";
</script>

<ErrorPage
    title                = {$i18n.Error.Page.PermissionDenied.Title}
    messageHtml          = {$i18n.Error.Page.PermissionDenied.Message1}
    statusCode           = "403"
    imageSrc             = "error/permission-denied.png"
    detailsHtml          = {$i18n.Error.Page.PermissionDenied.Message2}
    imageAlt             = {$i18n.Error.Page.PermissionDenied.Title}
    primaryActionLabel   = {$i18n.Error.Page.Actions.GoToHomepage}
    primaryActionHref    = "#/"
    secondaryActionLabel = {$i18n.Error.Page.Actions.GoToLibrary}
    secondaryActionHref  = "#/library"
/>
