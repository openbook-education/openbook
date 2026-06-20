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
Semantic surface for chat input controls with dedicated hint and action slots.
-->

<script lang="ts">
    import type {Snippet} from "svelte";

    interface Props {
        class?:    string;
        hint?:     Snippet;
        actions?:  Snippet;
        children?: Snippet;
    }

    let {
        class: className = "",
        hint,
        actions,
        children,
    }: Props = $props();

    const composerClass = $derived([
        "rounded-[1.75rem]",
        "border",
        "border-base-300",
        "bg-base-100",
        "p-2",
        "shadow-sm",
        "flex-1",
        "lg:max-w-4xl",
        className,
    ].filter(Boolean).join(" "));
</script>

<div class={composerClass}>
    <div>
        {@render children?.()}
    </div>

    {#if hint || actions}
        <div class="flex items-center justify-between gap-3 px-2 pb-1 pt-2">
            <div class="min-w-0 flex-1 text-xs text-base-content/60">
                {@render hint?.()}
            </div>

            {#if actions}
                <div class="flex shrink-0 items-center gap-2">
                    {@render actions()}
                </div>
            {/if}
        </div>
    {/if}
</div>
