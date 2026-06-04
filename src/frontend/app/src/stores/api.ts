/*
 * OpenBook: Interactive Online Textbooks
 * © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import type { paths      as authPaths }          from "../api/openapi/auth";
import type { components as authComponents }     from "../api/openapi/auth";
import type { paths      as openbookPaths }      from "../api/openapi/openbook";
import type { components as openbookComponents } from "../api/openapi/openbook";
import type { Client }                           from "openapi-fetch";

import clients                                   from "../api/index.js";
import { rethrowAppError }                       from "../utils/error.js";
import { toasts }                                from "./toasts.js";

/**
 * Typed schema components for the authentication API.
 */
export type authSchemas = authComponents["schemas"];

/**
 * Typed schema components for the OpenBook API.
 */
export type openbookSchemas = openbookComponents["schemas"];

/**
 * Factory for pre-configured wrapped API clients. The raw API clients are wrapped here
 * to simplify typical usage scenarios in a Svelte component.
 *
 * First of all, it is assumed that each component only ever accesses very few paths
 * (usually one) but needs to call different HTTP methods on that path. Therefore, the
 * path is only given once during creation of the wrapped API client.
 *
 * Next, errors are automatically handled in one of two possible ways:
 *
 * - "error-page" (default): Remote errors are thrown as exceptions, so that the
 *   `ApplicationFrame` can render a full-size error page.
 *
 * - "error-toast": Remote errors don't throw but trigger a toast notification.
 *   The wrapped client methods return the error object, for the caller to recognize
 *   and handle the error.
 */
export default {
    /**
     * @returns Wrapped API client for the authentication API
     */
    auth: async <Path extends AllPaths<authPaths>>(path: Path, errors: ErrorHandling = "error-page") => {
        let client = await clients.auth();
        return new ClientWrapper(client, path, errors);

    },

    /**
     * @returns Wrapped API client for the OpenBook API
     */
    openbook: async <Path extends AllPaths<openbookPaths>>(path: Path, errors: ErrorHandling = "error-page") => {
        let client = await clients.openbook();
        return new ClientWrapper(client, path, errors);
    },
};

/**
 * Wrapper for calling a specific OpenAPI path with error handling.
 *
 * @template Paths The OpenAPI paths type.
 * @template Path The specific path key.
 */
class ClientWrapper<Paths extends {}, Path extends AllPaths<Paths>> {
    client: Client<Paths>;
    path:   Path;
    errors: ErrorHandling;

    /**
     * Create a new client wrapper for a specific path and error handling mode.
     *
     * @param client The OpenAPI client instance.
     * @param path The OpenAPI path to call.
     * @param errors The error handling mode.
     */
    constructor(client: Client<Paths>, path: Path, errors: ErrorHandling) {
        this.client = client;
        this.path   = path;
        this.errors = errors;
    }

    /**
     * Handle errors from API calls according to the configured error handling mode.
     * Let's the application frame either render a toast or a full-blown error message.
     *
     * @param error The error object received from the API call.
     */
    private handleError(error: unknown) {
        if (!error) return;

        let status = 0;
        let message = "";

        if (typeof error === "object" && error !== null && "status" in error) {
            const maybeError  = error as {status?: unknown, detail?: unknown, message?: unknown};
            const maybeStatus = maybeError.status;

            if (typeof maybeStatus === "number") {
                status = maybeStatus;
            }

            if (typeof maybeError.detail === "string") {
                message = maybeError.detail;
            } else if (typeof maybeError.message === "string") {
                message = maybeError.message;
            } else {
                message = String(error);
            }
        } else {
            message = error?.toString?.() ?? String(error);
        }

        if (this.errors === "error-toast") {
            toasts.show("error", message);
            return;
        }

        switch (status) {
            case 401:
            case 403:
                rethrowAppError("PermissionDenied", error, message);
            case 404:
                rethrowAppError("NotFound", error, message);
            default:
                rethrowAppError("OperationFailed", error, message);
        }
    }

    /**
     * Send a `GET` request to retrieve a list or single object.
     *
     * @param options Request parameters.
     * @returns The result of the GET request.
     */
    async GET(options?: RequestOptionsParams): Promise<GetResult<Paths, Path>> {
        type PathKey = Extract<Path, GetPaths<Paths>>;
        const result = await this.client.GET(this.path as PathKey, (options ?? {}) as any);
        this.handleError((result as any).error);
        return result as GetResult<Paths, Path>;
    }

    /**
     * Send a `POST` request to create a new object.
     *
     * @param options Request parameters and body.
     * @returns The result of the POST request.
     */
    async POST(options?: RequestOptionsBody): Promise<PostResult<Paths, Path>> {
        type PathKey = Extract<Path, PostPaths<Paths>>;
        const result = await this.client.POST(this.path as PathKey, (options ?? {}) as any);
        this.handleError((result as any).error);
        return result as PostResult<Paths, Path>;
    }

    /**
     * Send a `PUT` request to replace an object. The request body must contain
     * the full object structure.
     *
     * @param options Request parameters and body.
     * @returns The result of the PUT request.
     */
    async PUT(options?: RequestOptionsBody): Promise<PutResult<Paths, Path>> {
        type PathKey = Extract<Path, PutPaths<Paths>>;
        const result = await this.client.PUT(this.path as PathKey, (options ?? {}) as any);
        this.handleError((result as any).error);
        return result as PutResult<Paths, Path>;
    }

    /**
     * Send a `PATCH` request to update an object. Unlike `POST`, the request body only
     * needs to contain the properties to be changed.
     *
     * @param options Request parameters and body.
     * @returns The result of the PATCH request.
     */
    async PATCH(options?: RequestOptionsBody): Promise<PatchResult<Paths, Path>> {
        type PathKey = Extract<Path, PatchPaths<Paths>>;
        const result = await this.client.PATCH(this.path as PathKey, (options ?? {}) as any);
        this.handleError((result as any).error);
        return result as PatchResult<Paths, Path>;
    }

    /**
     * Send a `DELETE` request to delete an object.
     *
     * @param options Request parameters and body.
     * @returns The result of the DELETE request.
     */
    async DELETE(options?: RequestOptionsParams): Promise<DeleteResult<Paths, Path>> {
        type PathKey = Extract<Path, DeletePaths<Paths>>;
        const result = await this.client.DELETE(this.path as PathKey, (options ?? {}) as any);
        this.handleError((result as any).error);
        return result as DeleteResult<Paths, Path>;
    }
}

/**
 * Error handling modes for API calls.
 */
export type ErrorHandling = "error-toast" | "error-page";

/* The following types extract the paths from the OpenAPI-generated
 * types that support each respective HTTP method. They work like this:
 *
 * Iterate over each path in the paths object.
 * For each path, check if has a property for the given HTTP method.
 * If yes, keep the path; if not, set it to never.
 *
 * The final [keyof Paths] at the end creates a union of all the keys that are not never.
 */
export type AllPaths<Paths>    = {[Path in keyof Paths]: Path}[keyof Paths];
export type GetPaths<Paths>    = {[Path in keyof Paths]: Paths[Path] extends {get:    any} ? Path : never}[keyof Paths];
export type PostPaths<Paths>   = {[Path in keyof Paths]: Paths[Path] extends {post:   any} ? Path : never}[keyof Paths];
export type PutPaths<Paths>    = {[Path in keyof Paths]: Paths[Path] extends {put:    any} ? Path : never}[keyof Paths];
export type PatchPaths<Paths>  = {[Path in keyof Paths]: Paths[Path] extends {patch:  any} ? Path : never}[keyof Paths];
export type DeletePaths<Paths> = {[Path in keyof Paths]: Paths[Path] extends {delete: any} ? Path : never}[keyof Paths];

/**
 * The following types extract the result types for each HTTP method and path.
 *
 * For a given path, check it has a get/put/... property with a response for the expected
 * HTTP status (e.g., 200 for GET, 201 for PUT, 204 for DELETE) and content type application/json.
 *
 * If so, use TypeScript’s infer keyword to extract the type of the response body as `data`.
 * The result type always includes `data`, `error`, and `response` fields.
 * If the expected response is not defined, `data` is undefined and `error`/`response` are unknown.
 *
 * Note: Error and non-JSON responses are typed as unknown because they are not explicitly defined
 * in the OpenAPI schema.
 */
type GetResult<Paths, Path extends keyof Paths> =
    Paths[Path] extends {get: {responses: infer Responses}}
        ? {
                data:     Responses extends {200: {content: {"application/json": infer ResponseBody}}} ? ResponseBody : undefined;
                error:    unknown;
                response: unknown;
            }
        : ErrorResult;

type PostResult<Paths, Path extends keyof Paths> =
    Paths[Path] extends {post: {responses: infer Responses}}
        ? {
                data:     Responses extends {201: {content: {"application/json": infer ResponseBody}}} ? ResponseBody : undefined;
                error:    unknown;
                response: unknown;
            }
        : ErrorResult;

type PutResult<Paths, Path extends keyof Paths> =
    Paths[Path] extends {put: {responses: infer Responses}}
        ? {
                data:     Responses extends {200: {content: {"application/json": infer ResponseBody}}} ? ResponseBody : undefined;
                error:    unknown;
                response: unknown;
            }
        : ErrorResult;

type PatchResult<Paths, Path extends keyof Paths> =
    Paths[Path] extends {patch: {responses: infer Responses}}
        ? {
                data:     Responses extends {200: {content: {"application/json": infer ResponseBody}}} ? ResponseBody : undefined;
                error:    unknown;
                response: unknown;
            }
        : ErrorResult;

type DeleteResult<Paths, Path extends keyof Paths> =
    Paths[Path] extends {delete: {responses: infer Responses}}
        ? {
                data:     Responses extends {204: {content: {"application/json": infer ResponseBody}}} ? ResponseBody : undefined;
                error:    unknown;
                response: unknown;
            }
        : ErrorResult;

export type ErrorResult          = {data: undefined, error: unknown, response: unknown};
export type RequestOptionsParams = {params: any};
export type RequestOptionsBody   = {params: any, body: any};
