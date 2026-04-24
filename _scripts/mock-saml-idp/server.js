/*
 * OpenBook: Interactive Online Textbooks
 * © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import {parseArgs}   from "node:util";
import {startServer} from "mock-saml-idp";

/**
 * Configure and start mock SAML IDP server to local testing and unit tests.
 */
const args = parseArgs({
    options: {
        h: {type: "string"},
        p: {type: "string"},
    }
});

const config = {
    host: args.values.h || "localhost",
    port: parseInt(args.values.p || "7000"),    // mock-saml-idp default port is 7000
}

if (Number.isNaN(config.port)) {
    throw new Error(`Invalid port number: ${config.port}`);
}

const {url} = await startServer({
    host: config.host,
    port: config.port,

    // Default user shown in the login form. Actually the server accepts all
    // credentials and simply passes them on to the service provider. For testing
    // we use different e-mail domains to assign initial permission groups:
    // @student.com, @teacher.com, @admin.com
    defaultUser: {
        nameId:    "alice@student.com",
        firstName: "Alice",
        lastName:  "Student",
    },
});

console.log(`Mock SAML IdP running at ${url}`);
