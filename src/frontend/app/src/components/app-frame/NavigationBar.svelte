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
Top navigation page of the application frame.
-->

<script lang="ts">
    import {i18n}            from "../../stores/i18n.js";
    import {availableThemes} from "../../stores/theme.js";
    import {theme}           from "../../stores/theme.js";
    import AvatarDefault     from "./img/AvatarDefault.jpg";

    let avatar = $state(AvatarDefault);

    function switchTheme(event: MouseEvent) {
        const target = event.target as HTMLAnchorElement;
        $theme = target.dataset.themeName as string;
        event.preventDefault();
    }
</script>

<!-- Navbar -->
<div class="navbar border-0 bg-base-100/85 backdrop-blur-md top-0 sticky">
    <!-- Breadcrumb with current location -->
    <div class="flex-1">
        Breadcrumb
    </div>

    <!-- Page menu -->

    <!-- Search and user menu -->
    <div class="flex gap-2">
        <!-- Search input -->
        <input type="text" placeholder="{$i18n.ApplicationFrame.Search.Placeholder}" class="input input-bordered w-24 md:w-auth"/>

        <!-- Menu -->
        <!-- TODO: Custom element with better keyboard navigation -->
        <details class="dropdown dropdown-end">
            <summary class="btn btn-ghost btn-circle avatar">
                <div class="w-10 rounded-full">
                    <img src="{avatar}" alt="{$i18n.ApplicationFrame.Menu.Title}"/>
                </div>
            </summary>
            <ul
                class = "dropdown-content menu menu-sm xl:menu-horizontal bg-base-100/85 backdrop-blur shadow rounded-box lg:min-w-max z-10"
                role = "menu"
            >
                <!-- Theme -->
                <li class="w-40">
                    <div class="menu-title">
                        {$i18n.ApplicationFrame.Menu.Theme.Title}
                    </div>
                    <ul>
                        {#each availableThemes as availableTheme}
                            <li>
                                <a
                                    href            = "#dummy"
                                    data-theme-name = {availableTheme.name}
                                    onclick         = {switchTheme}
                                    role            = "menuitemradio"
                                    aria-checked    = {$theme === availableTheme.name}
                                    tabindex        = {$theme === availableTheme.name ? 0 : -1}
                                >
                                    {#if $theme === availableTheme.name}
                                        <i class="bi bi-check-circle"></i>
                                    {:else}
                                        <i class="bi bi-circle"></i>
                                    {/if}

                                    {availableTheme.label}
                                </a>
                            </li>
                        {/each}
                    </ul>
                </li>

                <!-- Account -->
                <li class="w-40">
                    <div class="menu-title">
                        {$i18n.ApplicationFrame.Menu.Account.Title}
                    </div>
                    <ul>
                        <li>
                            <a href="#/accounts/profile">
                                <i class="bi bi-box-arrow-right"></i>
                                {$i18n.ApplicationFrame.Menu.Account.Profile}
                            </a>
                        </li>
                        <li>
                            <a href="#/accounts/logout">
                                <i class="bi bi-person-circle"></i>
                                {$i18n.ApplicationFrame.Menu.Account.Logout}
                            </a>
                        </li>
                    </ul>
                </li>
            </ul>
        </details>
    </div>
</div>
