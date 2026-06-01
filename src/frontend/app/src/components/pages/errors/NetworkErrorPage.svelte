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
Dedicated full-screen page for backend/network connectivity errors.
 -->

<script lang="ts">
    import {i18n}    from "../../../stores/i18n.js";
    import {router}  from "svelte-spa-router";
    import ErrorPage from "./ErrorPage.svelte";

    interface Props {
        onRetry?: () => void;
    }

    let {
        onRetry,
    }: Props = $props();

    const retryHref = $derived(router.location ? `#${router.location}` : "#/");
</script>

<ErrorPage
    title                = {$i18n.Error.Page.NetworkError.Title}
    messageHtml          = {$i18n.Error.Page.NetworkError.Message1}
    statusCode           = "503"
    imageSrc             = "error/network-error.png"
    detailsHtml          = {$i18n.Error.Page.NetworkError.Message2}
    imageAlt             = {$i18n.Error.Page.NetworkError.Title}
    primaryActionLabel   = {$i18n.Error.Page.Actions.Retry}
    primaryActionIcon    = "bi bi-arrow-clockwise"
    primaryActionHref    = {retryHref}
    primaryActionOnClick = {onRetry}
    secondaryActionLabel = {$i18n.Error.Page.Actions.GoToHomepage}
    secondaryActionHref  = "#/"
/>
