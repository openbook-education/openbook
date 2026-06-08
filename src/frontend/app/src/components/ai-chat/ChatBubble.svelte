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
Reusable chat message bubble with variants for user, assistant and system messages.
-->

<script lang="ts">
    import type {Snippet} from "svelte";
    import { i18n }       from "../../stores/i18n.js";

    type ChatBubbleVariant = "assistant" | "user" | "system";
    type ChatBubbleTone    = "neutral" | "muted" | "info" | "warning" | "error" | "success";

    interface Props {
        class?:    string;
        variant?:  ChatBubbleVariant;
        tone?:     ChatBubbleTone;
        title?:    string;
        meta?:     string;
        pending?:  boolean;
        children?: Snippet;
    }

    let {
        class: className = "",
        variant = "assistant",
        tone    = "neutral",
        title   = "",
        meta    = "",
        pending = false,
        children,
    }: Props = $props();

    const wrapperClass = $derived([
        "flex",
        variant === "user" ? "justify-end" : "justify-start",
        variant === "system" && "justify-center",
    ].filter(Boolean).join(" "));

    const bubbleClass = $derived([
        "w-full",
        variant === "system" ? "max-w-full" : "max-w-[min(92%,42rem)]",
        "rounded-[1.5rem]",
        "px-4",
        "py-3",
        "shadow-sm",
        variant === "assistant" && "border border-base-300 bg-base-100 text-base-content",
        variant === "user"      && "bg-primary text-primary-content shadow-md",
        variant === "system"    && "border border-dashed border-base-300 bg-base-100/90 text-base-content",
        tone    === "muted"     && "bg-base-200 text-base-content/80",
        tone    === "info"      && "border-info/40 bg-info/10 text-info-content",
        tone    === "warning"   && "border-warning/40 bg-warning/10 text-warning-content",
        tone    === "error"     && "border-error/40 bg-error/10 text-error-content",
        tone    === "success"   && "border-success/40 bg-success/10 text-success-content",
        className,
    ].filter(Boolean).join(" "));

    const metaClass = $derived([
        "flex",
        "flex-wrap",
        "items-center",
        "gap-x-2",
        "gap-y-1",
        "text-[0.7rem]",
        "font-semibold",
        "uppercase",
        "tracking-[0.18em]",
        variant === "user" ? "text-primary-content/75" : "text-base-content/55",
    ].filter(Boolean).join(" "));
</script>

<div class={wrapperClass}>
    <article class={bubbleClass}>
        {#if title || meta || pending}
            <header class={metaClass}>
                {#if title}<span>{title}</span>{/if}
                {#if meta}<span>{meta}</span>{/if}
                {#if pending}<span class="loading loading-dots loading-xs" aria-label={$i18n.AiChat.StreamingResponseAriaLabel}></span>{/if}
            </header>
        {/if}

        <div class="mt-2 space-y-3 text-sm leading-6 sm:text-[0.95rem]">
            {@render children?.()}
        </div>
    </article>
</div>
