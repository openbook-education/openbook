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
Generic error page layout centered horizontally and vertically.
-->

<script lang="ts">
    import {i18n} from "../../../stores/i18n.js";

    interface Props {
        title:                 string;
        messageHtml:           string;
        statusCode:            string;
        imageSrc:              string;
        detailsHtml?:          string;
        imageAlt?:             string;
        primaryActionLabel?:   string;
        primaryActionHref?:    string;
        primaryActionOnClick?: () => void;
        primaryActionIcon?:    string;
        secondaryActionLabel?: string;
        secondaryActionHref?:  string;
    }

    let {
        title,
        messageHtml,
        statusCode,
        imageSrc,
        detailsHtml          = "",
        imageAlt             = "",
        primaryActionLabel   = $i18n.Error.Page.Actions.GoToHomepage,
        primaryActionHref    = "#/",
        primaryActionOnClick,
        primaryActionIcon    = "bi bi-book",
        secondaryActionLabel = "",
        secondaryActionHref  = "",
    }: Props = $props();

    const pageClass          = "flex h-full w-full flex-1 flex-col gap-6 px-4 py-6 sm:px-6 sm:py-8 xl:px-10 xl:py-10";
    const statusCodeClass    = "bg-linear-to-r from-primary to-info bg-clip-text text-6xl font-black tracking-tight text-transparent sm:text-7xl xl:text-8xl";
    const imageClass         = "h-auto max-h-full w-full max-w-xl object-contain drop-shadow-2xl";
    const primaryActionClass = "btn btn-primary btn-lg shadow-lg shadow-primary/20";
    const supportCardClass   = "mt-2 rounded-2xl border border-base-300 bg-base-100/85 p-4 shadow-sm sm:mt-4 sm:p-5";
</script>

<section class={pageClass}>
    <div class="grid flex-1 gap-8 xl:grid-cols-[1.05fr_1fr]">
        <article class="flex h-full flex-col justify-center gap-6 text-left">
            <div class="space-y-3">
                <p class={statusCodeClass}>
                    {statusCode}
                </p>

                <h1 class="text-4xl font-bold leading-tight text-base-content sm:text-5xl">
                    {title}
                </h1>
            </div>

            <div class="max-w-2xl space-y-4">
                <p class="text-base text-base-content/80 sm:text-xl">
                    {@html messageHtml}
                </p>

                {#if detailsHtml}
                    <p class="text-sm text-base-content/65 sm:text-lg">
                        {@html detailsHtml}
                    </p>
                {/if}
            </div>

            <div class="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
                {#if primaryActionOnClick}
                    <button type="button" onclick={primaryActionOnClick} class={primaryActionClass}>
                        <i class={primaryActionIcon}></i>
                        {primaryActionLabel}
                    </button>
                {:else if primaryActionHref}
                    <a href={primaryActionHref} class={primaryActionClass}>
                        <i class={primaryActionIcon}></i>
                        {primaryActionLabel}
                    </a>
                {/if}

                {#if secondaryActionLabel && secondaryActionHref}
                    <a href={secondaryActionHref} class="btn btn-outline btn-lg">
                        <i class="bi bi-house"></i>
                        {secondaryActionLabel}
                    </a>
                {/if}
            </div>
        </article>

        <div class="relative flex h-full min-h-64 items-end justify-center rounded-3xl p-6 sm:p-8">
            <img
                class={imageClass}
                src={imageSrc}
                alt={imageAlt || title}
            >
        </div>
    </div>

    <div class={supportCardClass}>
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div class="flex items-start gap-3">
                <span class="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <i class="bi bi-magic"></i>
                </span>

                <div class="space-y-3">
                    <p class="text-base font-semibold text-base-content">
                        {$i18n.Error.Page.Support.Title}
                    </p>

                    <p class="text-sm text-base-content/70 sm:text-base">
                        {$i18n.Error.Page.Support.Text}
                    </p>
                </div>
            </div>

            <!-- TODO: Open AI assistant -->
            <a href="#/" class="btn btn-outline btn-sm whitespace-nowrap sm:btn-md">
                <i class="bi bi-stars"></i>
                {$i18n.Error.Page.Support.Action}
            </a>
        </div>
    </div>
</section>
