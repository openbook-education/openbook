/*
* OpenBook: Interactive Online Textbooks
* © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU Affero General Public License as
* published by the Free Software Foundation, either version 3 of the
* License, or (at your option) any later version.
*/

/**
 * Handler class that fetches the required information on the currently selected
 * scope and updates all dependent UI fields accordingly. Also watches the UI
 * fields for a changed scope type to repeat the process.
 */
class ScopeDependantFieldsHandler {
    // Input fields
    scopeTypeField       = document.querySelector("#id_scope_type");
    scopeUuidField       = document.querySelector("#id_scope_uuid");
    permissionsFromField = document.querySelector("#id_permissions_from");
    permissionsToField   = document.querySelector("#id_permissions_to");

    // Auxiliary variables
    scopeUuidChangeEventListenerRegistered = false;
    permissionsFromMutationObserver;
    retryCount = 0;

    // Scope type data from backend
    scopeTypeDetails = {
        scopeType: "",
        inFlight:  false,
        data:      {},
    }

    /**
     * Kickstart handling. This calls all other methods as required.
     */
    async updateAll(permissionsOnly) {
        if (++this.retryCount > 20) return;

        try {
            this.queryDomElements();
    
            if (this.scopeTypeField && !permissionsOnly) {
                await this.fetchScopeTypeDetails(this.scopeTypeField.value || "");
                this.updateScopeUuidField();
            }

            if (this.permissionsFromField && this.permissionsToField) {
                this.updatePermissionsFilter();
            } else {
                window.setTimeout(() => this.updateAll(true), 250);
            }
        } catch (err) {
            console.error("Failed to update scope dependant fields:", err);
        }
    }

    /**
     * This method must be called at least once to get the field references from the DOM.
     * For the permissions filter the call must be repeated a second or so, until the filter
     * becomes available. If it is still not available after a few seconds it should be safe
     * to assume there is no permissions filter on the page.
     * 
     * If the scope UUID fields is found, a change event listener is registered.
     * If the permissions filter is found, a mutation handler is registered.
     */
    queryDomElements() {
        this.scopeTypeField       = document.querySelector("#id_scope_type");
        this.scopeUuidField       = document.querySelector("#id_scope_uuid");
        this.permissionsFromField = document.querySelector("#id_permissions_from");
        this.permissionsToField   = document.querySelector("#id_permissions_to");

        // Register change event handler for the scope type
        if (this.scopeTypeField && !this.scopeUuidChangeEventListenerRegistered) {
            this.scopeUuidChangeEventListenerRegistered = true;
            this.scopeTypeField.addEventListener("change", () => this.updateAll());
        }

        // Register mutation handler for permissions from filter. Django Unfold (or Django Admin)
        // rebuilds the M2M from list each time, an entry is moved between the from and to list.
        // So we need to hide the disallowed options again.
        if (this.permissionsFromField && !this.permissionsFromMutationObserver) {
            this.permissionsFromMutationObserver = new MutationObserver(() => {
                if (this.permissionsFromMutationObserver._mutex) {
                    this.permissionsFromMutationObserver._mutex = false;
                    return;
                }
        
                this.updateAll(true);
            });
        
            this.permissionsFromMutationObserver.observe(this.permissionsFromField, {childList: true});
        }
    }

    /**
     * Fetch new data from backend if the scope type has been changed and no other
     * request is currently in flight.
     * 
     * @param {String} scopeType Selected scope type value
     */
    async fetchScopeTypeDetails(scopeType) {
        if (!scopeType || this.scopeTypeDetails.inFlight) return;
        if (this.scopeTypeDetails.scopeType === scopeType) return;

        this.scopeTypeDetails.scopeType = scopeType;
        this.scopeTypeDetails.inFlight  = true;

        let url = `/api/auth/scope_types/${scopeType}/`;
        let response = await fetch(url);

        if (!response.ok) {
            this.scopeTypeDetails.inFlight = false;
            throw new Error(await response.text());
        }

        this.scopeTypeDetails.data = (await response.json()) || {};

        if (!this.scopeTypeDetails.data.allowed_permissions) {
            this.scopeTypeDetails.data.allowed_permissions = [];
        }

        this.scopeTypeDetails.inFlight = false;
    }

    /**
     * Clear and repopulate scope UUID field, if it exists on the page.
     */
    updateScopeUuidField() {
        if (!this.scopeUuidField) return;
        if (this.scopeTypeDetails.inFlight) return;

        let selectedValue = this.scopeUuidField.querySelector("[selected]")?.value || "";
        this.scopeUuidField.innerHTML = "";

        for (let scope_object of this.scopeTypeDetails.data.objects || []) {
            let option = new Option(scope_object.name, scope_object.uuid);
            if (scope_object.uuid === selectedValue) option.selected = true;
            this.scopeUuidField.appendChild(option);
        }

        if (!selectedValue) {
            let option = new Option("", "");
            option.setAttribute("selected", "");
            this.scopeUuidField.appendChild(option);
        }
    }

    /**
     * Hide disallowed permissions from the permission filter, if input fields for
     * a horizontal permissions filter exist on the page.
     */
    updatePermissionsFilter() {
        if (!this.permissionsFromField || !this.permissionsToField) return;
        if (this.scopeTypeDetails.inFlight) return;

        this.permissionsFromMutationObserver._mutex = true;
        let allPermissionOptions = [];
        
        for (let option of this.permissionsFromField.querySelectorAll("option")) {                
            option.classList.remove("_visible");
            allPermissionOptions.push(option);
            option.remove();
        }

        for (let allowedPermission of this.scopeTypeDetails.data.allowed_permissions) {
            let toPermission = this.permissionsToField.querySelector(`option[value="${allowedPermission.id}"]`);

            allPermissionOptions.filter(option => {
                if (option.value == allowedPermission.id && !toPermission) {
                    option.classList.add("_visible");
                    this.permissionsFromField.appendChild(option);
                    return false;
                }

                return true;
            });
        }
    }
}

/**
 * Get the stone rolling once the DOM has finished loading.
 */
document.addEventListener("DOMContentLoaded", async () => {
    let handler = new ScopeDependantFieldsHandler();
    handler.updateAll();
});
