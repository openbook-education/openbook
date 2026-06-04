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
    import type { openbookSchemas } from "../../stores/api.js";

    import Breadcrumbs              from "../basic/breadcrumbs/Breadcrumbs.svelte";
    import BreadcrumbsItem          from "../basic/breadcrumbs/BreadcrumbsItem.svelte";
    import DropdownMenu             from "../basic/dropdown-menu/DropdownMenu.svelte";
    import MenuItem                 from "../basic/dropdown-menu/MenuItem.svelte";
    import MenuTitle                from "../basic/dropdown-menu/MenuTitle.svelte";
    import SubMenu                  from "../basic/dropdown-menu/SubMenu.svelte";
    import Navbar                   from "../basic/navbar/Navbar.svelte";

    import { breadcrumbs }          from "../../stores/breadcrumbs.js";
    import { i18n }                 from "../../stores/i18n.js";
    import { language }             from "../../stores/i18n.js";
    import { availableThemes }      from "../../stores/theme.js";
    import { theme }                from "../../stores/theme.js";
    import api                      from "../../stores/api.js";

    import AvatarDefault            from "./img/AvatarDefault.jpg";

    let avatar = $state(AvatarDefault);
    let availableLanguages: openbookSchemas["Language"][] = $state([]);

    async function loadLanguages() {
        let backend  = await api.openbook("/api/core/languages/", "error-toast");
        let response = await backend.GET();
        availableLanguages = response.data.results;
    }
</script>

{#await loadLanguages()}{/await}

<!-- Navbar -->
<Navbar class="top-0 sticky z-10 bg-base-100/95">
    <!-- Logo and breadcrumb -->
    <div class="flex-1 flex flex-row items-center gap-8">
        <!-- Logo -->
        <div class="flex flex-row items-center gap-1">
            <img src="favicon.svg" alt="" class="block size-6"/>
            <div class="text-primary text-xl font-bold">OpenBook</div>
        </div>

        <!-- Breadcrumbs -->
        <Breadcrumbs class="hidden md:block text-sm">
            {#each $breadcrumbs($i18n) as item (`${item.href}/${item.label}`)}
                <BreadcrumbsItem href={item.href || undefined}>
                    {item.label}
                </BreadcrumbsItem>
            {/each}
        </Breadcrumbs>
    </div>

    <!-- Search and menu -->
    <div class="flex gap-2">
        <!-- Search input -->
        <input type="text" placeholder="{$i18n.ApplicationFrame.Search.Placeholder}" class="input input-bordered w-24 md:w-auth"/>

        <!-- Menu -->
        <DropdownMenu
            align        = "end"
            triggerClass = "btn btn-ghost btn-circle avatar"
            contentClass = "menu-sm bg-base-100/95 backdrop-blur shadow rounded-box lg:min-w-max"
        >
            {#snippet trigger()}
                <div class="w-10 rounded-full">
                    <img src="{avatar}" alt="{$i18n.ApplicationFrame.Menu.Title}"/>
                </div>
            {/snippet}

            <!-- Language -->
            {#if availableLanguages.length > 1}
                <MenuItem>
                    <MenuTitle>
                        {$i18n.ApplicationFrame.Menu.Language.Title}
                    </MenuTitle>

                    <SubMenu>
                        {#each availableLanguages as availableLanguage (availableLanguage.language)}
                            <MenuItem
                                itemClass          = "justify-start"
                                onclick            = {() => $language = availableLanguage.language}
                                role               = "menuitemradio"
                                aria-checked       = {$language === availableLanguage.language}
                                tabindex           = {$language === availableLanguage.language ? 0 : -1}
                            >
                                {#if $language === availableLanguage.language}
                                    <i class="bi bi-check-circle"></i>
                                {:else}
                                    <i class="bi bi-circle"></i>
                                {/if}

                                {availableLanguage.name}
                            </MenuItem>
                        {/each}
                    </SubMenu>
                </MenuItem>
            {/if}

            <!-- Theme -->
            <MenuItem>
                <MenuTitle>
                    {$i18n.ApplicationFrame.Menu.Theme.Title}
                </MenuTitle>

                <SubMenu>
                    {#each availableThemes($i18n) as availableTheme (availableTheme.name)}
                        <MenuItem
                            itemClass       = "justify-start"
                            data-theme-name = {availableTheme.name}
                            onclick         = {() => $theme = availableTheme.name}
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
                        <i class="bi bi-person-circle"></i>
                        {$i18n.ApplicationFrame.Menu.Account.Profile}
                    </MenuItem>

                    <MenuItem href="#/accounts/logout">
                        <i class="bi bi-box-arrow-right"></i>
                        {$i18n.ApplicationFrame.Menu.Account.Logout}
                    </MenuItem>
                </SubMenu>
            </MenuItem>
        </DropdownMenu>
    </div>
</Navbar>
