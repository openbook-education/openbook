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
    import AiChatPane                from "./ai-chat/AiChatPane.svelte";
    import NavigationBar             from "./app-frame/NavigationBar.svelte";
    import LoadingAnimation          from "./app-frame/LoadingAnimation.svelte";
    import Toast                     from "./basic/toast/Toast.svelte";
    import Alert                     from "./basic/toast/Alert.svelte";

    import { toasts }                from "../stores/toasts";
    import { NetworkError }          from "../utils/error.js";
    import { NotFoundError }         from "../utils/error.js";
    import { OperationFailedError }  from "../utils/error.js";
    import { PermissionDeniedError } from "../utils/error.js";

    import Router                    from "svelte-spa-router";
    import routes                    from "./routes.js";

    type ErrorPageResolverResult = {
        component: any;
        retryable: boolean;
    };

    type MobilePaneMode  = "chat" | "main";
    type DesktopPaneMode = "chat" | "main" | "both";

    let mobilePaneMode  = $state<MobilePaneMode>("main");
    let desktopPaneMode = $state<DesktopPaneMode>("both");

    /**
     * Resolve error page at runtime to avoid static import. Because statically importing
     * the same files (directly or indirectly) here and in `routes.ts` silently breaks
     * page rendering, so that only a white page is rendered but not error is logged neither
     * during the build nor at runtime.
     */
    async function resolveErrorPage(error: unknown): Promise<ErrorPageResolverResult> {
        console.error(error);

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

    const chatPaneClass = $derived([
        "min-h-0",
        "overflow-y-auto",
        mobilePaneMode === "chat" ? "flex flex-1" : "hidden",
        desktopPaneMode === "main"
            ? "lg:hidden"
            : desktopPaneMode === "both"
                ? "lg:flex lg:flex-1"
                : "lg:flex lg:flex-1 lg:justify-center",
    ].join(" "));

    const mainPaneClass = $derived([
        "relative",
        "min-h-0",
        "overflow-y-auto",
        "shadow-lg",
        mobilePaneMode === "main" ? "flex flex-1" : "hidden",
        desktopPaneMode === "chat"
            ? "lg:hidden"
            : desktopPaneMode === "both"
                ? "lg:flex lg:flex-2"
                : "lg:flex lg:flex-1",
    ].join(" "));

    const chatPaneInnerClass = $derived([
        "flex",
        "min-h-0",
        "flex-1",
        "w-full",
        desktopPaneMode === "chat" ? "lg:max-w-[96rem]" : "",
    ].filter(Boolean).join(" "));
</script>

<div class="flex h-dvh min-h-0 flex-col overflow-hidden">
    <NavigationBar
        bind:mobilePaneMode
        bind:desktopPaneMode
    />

    <main class="flex min-h-0 flex-1 flex-col overflow-hidden">
        <svelte:boundary>
            <div class="flex flex-1 min-h-0 flex-col overflow-hidden lg:flex-row">
                <div class={chatPaneClass}>
                    <div class={chatPaneInnerClass}>
                        <AiChatPane/>
                    </div>
                </div>

                <div class={mainPaneClass}>
                    <Router {routes} />
                </div>
            </div>

            {#snippet pending()}
                <LoadingAnimation/>
            {/snippet}

            {#snippet failed(error, reset)}
                {#await resolveErrorPage(error) then resolved}
                    {@const ResolvedComponent = resolved.component}
                    {#if resolved.retryable}
                        <ResolvedComponent onRetry={reset}/>
                    {:else}
                        <ResolvedComponent/>
                    {/if}
                {:catch error}
                    <div class="flex flex-1 items-center justify-center p-8 text-center text-base-content/70">
                        {error}
                    </div>
                {/await}
            {/snippet}
        </svelte:boundary>

        <Toast>
            {#each $toasts as toast (toast.id) }
                <Alert type={toast.type} message={toast.message} />
            {/each}
        </Toast>
    </main>
</div>
