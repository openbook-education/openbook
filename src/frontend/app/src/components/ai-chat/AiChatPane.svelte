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
AI chat pane.
-->

<script lang="ts">

    import type { ChatMessagePayload } from "../../stores/ai-chat.js";
    import type { ChatMessageType }    from "../../stores/ai-chat.js";

    import ChatBubble                  from "./ChatBubble.svelte";
    import ChatComposer                from "./ChatComposer.svelte";
    import ChatMarkdown                from "./ChatMarkdown.svelte";
    import ChatPanel                   from "./ChatPanel.svelte";
    import Card                        from "../basic/card/Card.svelte";
    import CardBody                    from "../basic/card/CardBody.svelte";

    import { onMount, tick }           from "svelte";

    import { AiChatStore }             from "../../stores/ai-chat.js";
    import { i18n }                    from "../../stores/i18n.js";

    const aiChat = new AiChatStore();

    const timeFormatter = new Intl.DateTimeFormat(undefined, {
        hour:   "2-digit",
        minute: "2-digit",
    });

    let composerValue        = $state("");
    let isSending            = $state(false);
    let transcriptElement    = $state<HTMLDivElement | undefined>(undefined);
    let keepTranscriptPinned = $state(true);

    const renderedMessages = $derived.by(() => {
        const messagesById = new Map<string, ChatMessagePayload>();
        const order: string[] = [];

        for (const message of $aiChat.messages) {
            if (!messagesById.has(message.id)) {
                order.push(message.id);
            }

            messagesById.set(message.id, message);
        }

        return order
            .map(id => messagesById.get(id))
            .filter((message): message is ChatMessagePayload => Boolean(message));
    });

    const hasMessages = $derived(renderedMessages.length > 0);

    const latestMessage = $derived(renderedMessages[renderedMessages.length - 1]);

    const assistantBusy = $derived(
        Boolean(latestMessage && latestMessage.sender === "assistant" && !latestMessage.finished)
    );

    const canSend = $derived(
        $aiChat.connection === "connected"
        && !isSending
        && !assistantBusy
        && composerValue.trim().length > 0
    );
    const connectionLabel = $derived(getConnectionLabel($aiChat.connection));

    const connectionBadgeClass = $derived.by(() => {
        function getConnectionBadgeVariant(): string {
            switch ($aiChat.connection) {
                case "connected":
                    return "badge-success";
                case "connecting":
                    return "badge-info";
                case "wait_before_retry":
                    return "badge-warning";
                default:
                    return "badge-ghost";
            }
        }

        return [
            "badge",
            "badge-sm",
            getConnectionBadgeVariant(),
        ].join(" ");
    });

    onMount(() => {
        void aiChat.connect();

        return () => {
            void aiChat.disconnect();
        };
    });

    $effect(() => {
        $aiChat.messages.length;

        if (!transcriptElement || !keepTranscriptPinned) {
            return;
        }

        void tick().then(() => {
            if (!transcriptElement || !keepTranscriptPinned) return;

            transcriptElement.scrollTo({
                top: transcriptElement.scrollHeight,
                behavior: "smooth",
            });
        });
    });

    function isNearTranscriptBottom(element: HTMLDivElement): boolean {
        return element.scrollHeight - element.scrollTop - element.clientHeight < 96;
    }

    function handleTranscriptScroll() {
        if (!transcriptElement) return;
        keepTranscriptPinned = isNearTranscriptBottom(transcriptElement);
    }

    function handleComposerKeydown(event: KeyboardEvent) {
        if (event.key !== "Enter" || event.shiftKey) return;

        event.preventDefault();
        void submitMessage();
    }

    async function submitMessage() {
        if (!canSend) return;

        const content = composerValue.trim();
        if (!content) return;

        isSending = true;
        keepTranscriptPinned = true;

        try {
            await aiChat.sendChatInput("markdown", content);
            composerValue = "";
        } finally {
            isSending = false;
        }
    }

    function handleSubmit(event: SubmitEvent) {
        event.preventDefault();
        void submitMessage();
    }

    function formatTimestamp(datetime: ChatMessagePayload["datetime"]): string {
        const dateValue = normalizeDate(datetime);
        if (!dateValue) return "";

        return timeFormatter.format(dateValue);
    }

    function normalizeDate(value: Date | ChatMessagePayload["datetime"] | number | null | undefined): Date | null {
        if (!value) return null;
        if (value instanceof Date && !Number.isNaN(value.getTime())) return value;

        const normalized = new Date(value);
        return Number.isNaN(normalized.getTime()) ? null : normalized;
    }

    function getConnectionLabel(connection: typeof $aiChat.connection): string {
        switch (connection) {
            case "connected":
                return $i18n.AiChat.Connection.Live;
            case "connecting":
                return $i18n.AiChat.Connection.Connecting;
            case "wait_before_retry":
                return $i18n.AiChat.Connection.Reconnecting;
            default:
                return $i18n.AiChat.Connection.Offline;
        }
    }

    function getMessageTitle(message: ChatMessagePayload): string {
        if (message.type === "status") {
            return message.sender === "assistant"
                ? $i18n.AiChat.MessageTitle.AssistantStatus
                : $i18n.AiChat.MessageTitle.Status;
        }

        if (message.type === "thought") return $i18n.AiChat.MessageTitle.ReasoningNote;
        if (message.type === "action")  return $i18n.AiChat.MessageTitle.Action;
        if (message.type === "system")  return getSystemLabel(message.severity);

        return message.sender === "user"
            ? $i18n.AiChat.MessageTitle.You
            : $i18n.AiChat.MessageTitle.OpenBookAI;
    }

    function getSystemLabel(severity: ChatMessagePayload["severity"]): string {
        switch (severity) {
            case "critical":
                return $i18n.AiChat.SystemLabel.CriticalNotice;
            case "error":
                return $i18n.AiChat.SystemLabel.Error;
            case "warning":
                return $i18n.AiChat.SystemLabel.Warning;
            default:
                return $i18n.AiChat.SystemLabel.Notice;
        }
    }

    function getMessageVariant(message: ChatMessagePayload): "assistant" | "user" | "system" {
        if (message.type === "system") return "system";
        return message.sender === "user" ? "user" : "assistant";
    }

    function getMessageTone(message: ChatMessagePayload): "neutral" | "muted" | "info" | "warning" | "error" {
        if (message.type === "status") return "muted";

        if (message.type === "system") {
            if (message.severity === "critical" || message.severity === "error") return "error";
            if (message.severity === "warning") return "warning";
            return "info";
        }

        return "neutral";
    }

    function getMessageMeta(message: ChatMessagePayload): string {
        const parts = [formatTimestamp(message.datetime)];

        if (message.type !== "normal") {
            parts.push(getMessageTypeLabel(message.type));
        }

        if (message.format !== "markdown") {
            parts.push(getMessageFormatLabel(message.format));
        }

        return parts.filter(Boolean).join(" • ");
    }

    function getMessageTypeLabel(type: ChatMessageType): string {
        switch (type) {
            case "status":
                return $i18n.AiChat.MessageType.Status;
            case "thought":
                return $i18n.AiChat.MessageType.Thought;
            case "action":
                return $i18n.AiChat.MessageType.Action;
            case "system":
                return $i18n.AiChat.MessageType.System;
            default:
                return "";
        }
    }

    function getMessageFormatLabel(format: ChatMessagePayload["format"]): string {
        switch (format) {
            case "json":
                return $i18n.AiChat.MessageFormat.Json;
            case "image":
                return $i18n.AiChat.MessageFormat.Image;
            default:
                return "";
        }
    }

    function messageHasExpandableThought(message: ChatMessagePayload): boolean {
        return message.type === "thought";
    }

    function isRenderableImage(content: string): boolean {
        return content.startsWith("data:image/");
    }

    function formatJsonContent(content: string): string {
        try {
            return JSON.stringify(JSON.parse(content), null, 2);
        } catch {
            return content;
        }
    }

    function getMarkdownTone(message: ChatMessagePayload): "assistant" | "user" | "muted" {
        if (message.sender === "user") return "user";
        if (message.type === "status" || message.type === "thought") return "muted";
        return "assistant";
    }

    function isTransientMessage(type: ChatMessageType): boolean {
        return type === "status" || type === "thought";
    }
</script>

<ChatPanel class="border-r border-base-300/80 bg-[linear-gradient(180deg,rgba(249,250,251,0.96),rgba(236,244,255,0.92))]">
    {#snippet header()}
        <div class="flex items-start justify-between gap-4">
            <div class="flex min-w-0 items-start gap-3">
                <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-primary text-primary-content shadow-md">
                    <i class="bi bi-stars text-lg"></i>
                </div>

                <div class="min-w-0 space-y-1">
                    <div class="flex items-center gap-2">
                        <h2 class="truncate text-lg font-semibold text-base-content">{$i18n.AiChat.Header.Title}</h2>
                        <span class={connectionBadgeClass}>{connectionLabel}</span>
                    </div>

                    <p class="max-w-md text-sm text-base-content/70">
                        {$i18n.AiChat.Header.Description}
                    </p>
                </div>
            </div>

            <div class="hidden rounded-full border border-base-300 bg-base-100 px-3 py-1 text-xs font-medium text-base-content/65 sm:block">
                {$aiChat.messages.length} {$aiChat.messages.length === 1
                    ? $i18n.AiChat.Header.MessageSingular
                    : $i18n.AiChat.Header.MessagePlural}
            </div>
        </div>
    {/snippet}

    <div
        bind:this={transcriptElement}
        class="min-h-0 flex-1 overflow-y-auto px-4 py-4 sm:px-5"
        onscroll={handleTranscriptScroll}
    >
        {#if !hasMessages}
            <div class="flex h-full items-center justify-center py-8">
                <Card class="w-full max-w-[min(100%,56rem)] border-white/70 bg-base-100/90 shadow-xl backdrop-blur" variant="elevated">
                    <CardBody class="gap-5">
                        <div class="space-y-2">
                            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-primary/75">{$i18n.AiChat.EmptyState.Eyebrow}</p>
                            <h3 class="text-2xl font-semibold text-base-content">{$i18n.AiChat.EmptyState.Title}</h3>
                            <p class="text-sm leading-6 text-base-content/70">
                                {$i18n.AiChat.EmptyState.Description}
                            </p>
                        </div>

                        <div class="grid gap-3 text-sm text-base-content/70 sm:grid-cols-2">
                            <div class="rounded-2xl border border-base-300 bg-base-200/60 p-4">
                                <p class="font-medium text-base-content">{$i18n.AiChat.EmptyState.GoodPromptsTitle}</p>
                                <p class="mt-1">{$i18n.AiChat.EmptyState.GoodPromptsDescription}</p>
                            </div>

                            <div class="rounded-2xl border border-base-300 bg-base-200/60 p-4">
                                <p class="font-medium text-base-content">{$i18n.AiChat.EmptyState.BestFlowTitle}</p>
                                <p class="mt-1">{$i18n.AiChat.EmptyState.BestFlowDescription}</p>
                            </div>
                        </div>
                    </CardBody>
                </Card>
            </div>
        {:else}
            <div class="flex flex-col gap-4 pb-4">
                {#each renderedMessages as message (message.id)}
                    <ChatBubble
                        variant = {getMessageVariant(message)}
                        tone    = {getMessageTone(message)}
                        title   = {getMessageTitle(message)}
                        meta    = {getMessageMeta(message)}
                        pending = {message.sender === "assistant" && !message.finished}
                    >
                        {#if message.format === "json"}
                            <pre class="overflow-x-auto whitespace-pre-wrap wrap-break-word rounded-2xl bg-base-300/35 p-3 text-xs leading-6">{formatJsonContent(message.content)}</pre>
                        {:else if message.format === "image" && isRenderableImage(message.content)}
                            <img class="max-h-72 rounded-2xl object-contain shadow-sm" alt={$i18n.AiChat.MessageImageAlt} src={message.content} />
                        {:else if messageHasExpandableThought(message)}
                            <details class="rounded-2xl border border-base-300/80 bg-base-200/45 p-3">
                                <summary class="cursor-pointer text-sm font-medium text-base-content/75">
                                    {message.finished
                                        ? $i18n.AiChat.Reasoning.ShowNote
                                        : $i18n.AiChat.Reasoning.StillStreaming}
                                </summary>
                                <ChatMarkdown class="mt-3" content={message.content} tone="muted" />
                            </details>
                        {:else}
                            <ChatMarkdown content={message.content} tone={getMarkdownTone(message)} />
                        {/if}

                        {#if message.guardRails.findings !== "none"}
                            <div class="rounded-2xl border border-warning/40 bg-warning/10 px-3 py-2 text-xs leading-5 text-base-content/80">
                                <span class="font-semibold text-base-content">{$i18n.AiChat.GuardRails.Label}</span>
                                {message.guardRails.explanation}
                            </div>
                        {/if}

                        {#if isTransientMessage(message.type) && !message.finished}
                            <div class="text-xs font-medium uppercase tracking-[0.18em] text-base-content/45">
                                {$i18n.AiChat.StreamingUpdate}
                            </div>
                        {/if}
                    </ChatBubble>
                {/each}
            </div>
        {/if}
    </div>

    {#snippet footer()}
        <form class="space-y-3" onsubmit={handleSubmit}>
            <ChatComposer>
                <label class="sr-only" for="ai-chat-composer">{$i18n.AiChat.Composer.Label}</label>
                <textarea
                    id          = "ai-chat-composer"
                    bind:value={composerValue}
                    rows        = "3"
                    class       = "min-h-24 w-full resize-none border-0 bg-transparent px-3 py-2 text-sm leading-6 text-base-content outline-none placeholder:text-base-content/40"
                    aria-busy   = {isSending || assistantBusy}
                    placeholder = {$aiChat.connection === "connected"
                        ? $i18n.AiChat.Composer.PlaceholderOnline
                        : $i18n.AiChat.Composer.PlaceholderOffline}
                    onkeydown = {handleComposerKeydown}
                ></textarea>

                {#snippet hint()}
                    <p>
                        {$aiChat.connection === "connected"
                            ? assistantBusy
                                ? $i18n.AiChat.Composer.HintWaiting
                                : $i18n.AiChat.Composer.HintReady
                            : $i18n.AiChat.Composer.HintOffline}
                    </p>
                {/snippet}

                {#snippet actions()}
                    <button
                        class    = "btn btn-ghost btn-sm rounded-full"
                        type     = "button"
                        disabled = {!composerValue.trim().length || isSending}
                        onclick  = {() => { composerValue = "" }}
                    >
                        {$i18n.AiChat.Composer.Clear}
                    </button>

                    <button class="btn btn-primary btn-sm rounded-full px-5" type="submit" disabled={!canSend}>
                        {#if isSending}
                            <span class="loading loading-spinner loading-xs"></span>
                        {/if}
                        {$i18n.AiChat.Composer.Send}
                    </button>
                {/snippet}
            </ChatComposer>
        </form>
    {/snippet}
</ChatPanel>
