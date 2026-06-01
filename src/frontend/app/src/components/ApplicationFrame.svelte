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
    import NavigationBar        from "./app-frame/NavigationBar.svelte";
    import LoadingAnimation     from "./app-frame/LoadingAnimation.svelte";

    import {
        NetworkError,
        NotFoundError,
        OperationFailedError,
        PermissionDeniedError,
    } from "../utils/error.js";

    import Router           from "svelte-spa-router";
    import routes           from "./routes.js";

    type ErrorPageResolverResult = {
        component: any;
        retryable: boolean;
    };

    /**
     * Resolve error page at runtime to avoid static import. Because statically importing
     * the same files (directly or indirectly) here and in `routes.ts` silently breaks
     * page rendering, so that only a white page is rendered but not error is logged neither
     * during the build nor at runtime.
     */
    async function resolveErrorPage(error: unknown): Promise<ErrorPageResolverResult> {
        if (error instanceof NotFoundError) {
            return {
                component: (await import("./pages/errors/NotFoundPage.svelte")).default,
                retryable: false,
            };
        }

        if (error instanceof NetworkError) {
            return {
                component: (await import("./pages/errors/NetworkErrorPage.svelte")).default,
                retryable: true,
            };
        }

        if (error instanceof PermissionDeniedError) {
            return {
                component: (await import("./pages/errors/PermissionDeniedPage.svelte")).default,
                retryable: false,
            };
        }

        return {
            component: (await import("./pages/errors/OperationFailedPage.svelte")).default,
            retryable: error instanceof OperationFailedError,
        };
    }
</script>

<NavigationBar/>

<main class="flex flex-1 flex-col">
    <svelte:boundary>
        <Router {routes} />

        {#snippet pending()}
            <LoadingAnimation/>
        {/snippet}

        {#snippet failed(error, reset)}
            {#await resolveErrorPage(error) then resolved}
                {#if resolved.retryable}
                    <svelte:component this={resolved.component} onRetry={reset}/>
                {:else}
                    <svelte:component this={resolved.component}/>
                {/if}
            {:catch error}
                <div class="flex flex-1 items-center justify-center p-8 text-center text-base-content/70">
                    {error}
                </div>
            {/await}
        {/snippet}
    </svelte:boundary>
</main>
