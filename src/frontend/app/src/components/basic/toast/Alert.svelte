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
A singe alert message, typically rendered as a toast.
-->

<script lang="ts">
    import type { Toast } from "../../../stores/toasts.js";
    import { fade }       from "svelte/transition";

    interface Props {
        class?:  string;
        type?:   Toast["type"];
        message: string;
    }

    let {
        class: className = "",
        type = "info",
        message,
    }: Props = $props();

    function getAlertClass(): string {
        switch (type) {
            case "warning": return "alert-warning";
            case "error":   return "alert-error";
            case "success": return "alert-success";
            default:        return "alert-info";
        }
    }

    function getAlertIcon(): string {
        switch (type) {
            case "warning": return "bi-slash-circle-fill";
            case "error":   return "bi-exclamation-circle-fill";
            case "success": return "bi-check-circle-fill";
            default:        return "bi-info-circle-fill";
        }
    }

    const mergedClass = $derived(["alert", getAlertClass(), className].filter(Boolean).join(" "));
    const icon = $derived.by(getAlertIcon);
</script>

<div role="alert" class={mergedClass} transition:fade>
    <i class="bi {icon}"></i>
    <span>{message}</span>
</div>
