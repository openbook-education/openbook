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
 * Handler class that fetches the available roles within the selected scope
 * from the backend and updates the role selection list accordingly.
 */
class ScopeRolesHandler {
    // Input fields
    scopeTypeField = document.querySelector("#id_scope_type");
    scopeUuidField = document.querySelector("#id_scope_uuid");
    roleField      = document.querySelector("#id_role");

    // Auxiliary variables
    eventListenerRegistered = false;

    // Available roles from backend
    availableRoles = {
        scopeType: "",
        scopeUuid: "",
        inFlight:  false,
        data:      {},
    }

    /**
     * Kickstart handling. This calls all other methods as required.
     */
    async updateAll() {
        try {
            this.queryDomElements();
            await this.fetchAvailableRoles();
            this.updateRoleField();
        } catch (err) {
            console.error("Failed to update scope roles:", err);
        }
        
    }
    /**
     * This method must be called at least once to get the field references from the DOM.
     * If the scope type and  UUID fields is found, a change event listener is registered.
     */
    queryDomElements() {
        this.scopeTypeField = document.querySelector("#id_scope_type");
        this.scopeUuidField = document.querySelector("#id_scope_uuid");

        // Register change event handlers
        if (this.eventListenerRegistered) return;
        this.eventListenerRegistered = true;
        
        this.scopeTypeField.addEventListener("change", () => this.updateAll());
        this.scopeUuidField.addEventListener("change", () => this.updateAll());
    }

    /**
     * Fetch new data from backend if the scope has been changed and no other
     * request is currently in flight.
     */
    async fetchAvailableRoles() {
        if (this.availableRoles.inFlight) return;

        let scopeType = this.scopeTypeField.value;
        let scopeUuid = this.scopeUuidField.value;
        if (this.availableRoles.scopeType === scopeType && this.availableRoles.scopeUuid === scopeUuid) return;

        this.availableRoles.scopeType = scopeType;
        this.availableRoles.scopeType = scopeUuid;
        this.availableRoles.inFlight  = true;

        let queryParameters = new URLSearchParams();
        queryParameters.append("scope_type", scopeType);
        queryParameters.append("scope_uuid", scopeUuid);

        let url = `/api/auth/roles/?${queryParameters}`;
        let response = await fetch(url);

        if (!response.ok) {
            this.availableRoles.inFlight = false;
            throw new Error(await response.text());
        }

        this.availableRoles.data = (await response.json()) || {};
        this.availableRoles.inFlight = false;
    }

    /**
     * Clear and repopulate role field, if it exists on the page.
     */
    updateRoleField() {
        if (!this.roleField) return;
        if (this.availableRoles.inFlight) return;

        let selectedValue = this.roleField.querySelector("[selected]")?.value || "";
        this.roleField.innerHTML = "";

        for (let role of this.availableRoles.data.results || []) {
            let option = new Option(role.name, role.id);
            if (role.id === selectedValue) option.selected = true;
            this.roleField.appendChild(option);
        }

        if (!selectedValue) {
            let option = new Option("", "");
            option.setAttribute("selected", "");
            this.roleField.appendChild(option);
        }
    }
}

/**
 * Get the stone rolling once the DOM has finished loading.
 */
document.addEventListener("DOMContentLoaded", async () => {
    let handler = new ScopeRolesHandler();
    handler.updateAll();
});
