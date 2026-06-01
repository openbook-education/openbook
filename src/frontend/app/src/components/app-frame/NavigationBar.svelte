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
    import DropdownMenu      from "../basic/dropdown-menu/DropdownMenu.svelte";
    import MenuItem          from "../basic/dropdown-menu/MenuItem.svelte";
    import MenuTitle         from "../basic/dropdown-menu/MenuTitle.svelte";
    import SubMenu           from "../basic/dropdown-menu/SubMenu.svelte";
    import Navbar            from "../basic/navbar/Navbar.svelte";

    import {i18n}            from "../../stores/i18n.js";
    import {availableThemes} from "../../stores/theme.js";
    import {theme}           from "../../stores/theme.js";

    import AvatarDefault     from "./img/AvatarDefault.jpg";

    let avatar = $state(AvatarDefault);

    function switchTheme(event: MouseEvent) {
        const target = event.currentTarget as HTMLElement | null;
        const themeName = target?.dataset.themeName;

        if (themeName) {
            $theme = themeName;
        }
    }
</script>

<!-- Navbar -->
<Navbar class="top-0 sticky">
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
        <DropdownMenu
            align        = "end"
            summaryClass = "btn btn-ghost btn-circle avatar"
            contentClass = "menu-sm xl:menu-horizontal bg-base-100/85 backdrop-blur shadow rounded-box lg:min-w-max z-10"
        >
            {#snippet trigger()}
                <div class="w-10 rounded-full">
                    <img src="{avatar}" alt="{$i18n.ApplicationFrame.Menu.Title}"/>
                </div>
            {/snippet}

            <!-- Theme -->
            <MenuItem>
                <MenuTitle>
                    {$i18n.ApplicationFrame.Menu.Theme.Title}
                </MenuTitle>

                <SubMenu>
                    {#each availableThemes as availableTheme}
                        <MenuItem
                            itemClass       = "justify-start"
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
                        </MenuItem>
                    {/each}
                </SubMenu>
            </MenuItem>

            <!-- Account -->
            <MenuItem>
                <MenuTitle>
                    {$i18n.ApplicationFrame.Menu.Account.Title}
                </MenuTitle>

                <SubMenu>
                    <MenuItem href="#/accounts/profile">
                        <i class="bi bi-box-arrow-right"></i>
                        {$i18n.ApplicationFrame.Menu.Account.Profile}
                    </MenuItem>

                    <MenuItem href="#/accounts/logout">
                        <i class="bi bi-person-circle"></i>
                        {$i18n.ApplicationFrame.Menu.Account.Logout}
                    </MenuItem>
                </SubMenu>
            </MenuItem>
        </DropdownMenu>
    </div>
</Navbar>
