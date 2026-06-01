/*
 * OpenBook: Interactive Online Textbooks
 * © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import type {Client}     from "openapi-fetch";

import client              from "../backend";
import { rethrowAppError } from "../utils/error";
import { toast }           from "./toast";

/**
 * Factory for creating typed API client wrappers for a given OpenAPI client.
 *
 * @template Paths The OpenAPI paths type.
 */
class ClientWrapperFactory<Paths extends {}> {
    /**
     * The OpenAPI client instance.
     */
    client: Client<Paths>

    /**
     * Create a new factory for a specific OpenAPI client.
     *
     * @param client The OpenAPI client instance.
     */
    constructor(client: Client<Paths>) {
        this.client = client;
    }

    /**
     * Create a new client wrapper for a specific API path and error handling mode.
     *
     * @param path The OpenAPI path to call.
     * @param errors The error handling mode.
     * @returns A client wrapper for the given path.
     */
    call<Path extends AllPaths<Paths>>(path: Path, errors: ErrorHandling): ClientWrapper<Paths, Path> {
        return new ClientWrapper(this.client, path, errors);
    }
}

/**
 * Error handling modes for API calls.
 */
export type ErrorHandling = "error-toast" | "error-page";

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
            toast.show("error", message);
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
 * Client stubs to call the backend REST API from inside other Svelte stores
 * or Svelte UI components.
 */
export default {
    auth:     new ClientWrapperFactory(client.auth),
    openbook: new ClientWrapperFactory(client.openbook),
}


/* The following types extract the paths from the OpenAPI-generated
 * types that support each respective HTTP method. They work like this:
 *
 * Iterate over all keys (Key) in the Path object.
 * For each key, check if the value has a property for the wished HTTP method.
 * If yes, keep the key; if not, set it to never.
 *
 * The final [keyof Path] at the end creates a union of all the keys that are not never.
 */
export type AllPaths<Path>    = {[Key in keyof Path]: Key}[keyof Path];
export type GetPaths<Path>    = {[Key in keyof Path]: Path[Key] extends {get:    any} ? Key : never}[keyof Path];
export type PostPaths<Path>   = {[Key in keyof Path]: Path[Key] extends {post:   any} ? Key : never}[keyof Path];
export type PutPaths<Path>    = {[Key in keyof Path]: Path[Key] extends {put:    any} ? Key : never}[keyof Path];
export type PatchPaths<Path>  = {[Key in keyof Path]: Path[Key] extends {patch:  any} ? Key : never}[keyof Path];
export type DeletePaths<Path> = {[Key in keyof Path]: Path[Key] extends {delete: any} ? Key : never}[keyof Path];

/**
 * The following types extract the result types for each HTTP method and path.
 *
 * For a given path key, check if the value at that key has a get/put/... property with
 * a response for the expected HTTP status (e.g., 200 for GET, 201 for PUT, 204 for DELETE)
 * and content type application/json.
 *
 * If so, use TypeScript’s infer keyword to extract the type of the response body as `data`.
 * The result type always includes `data`, `error`, and `response` fields.
 * If the expected response is not defined, `data` is undefined and `error`/`response` are unknown.
 *
 * Note: Error and non-JSON responses are typed as unknown because they are not explicitly defined
 * in the OpenAPI schema.
 */
type GetResult<Path, Key extends keyof Path> =
    Path[Key] extends {get: {responses: infer Responses}}
        ? {
                data:     Responses extends {200: {content: {"application/json": infer ResponseBody}}} ? ResponseBody : undefined;
                error:    unknown;
                response: unknown;
            }
        : ErrorResult;

type PostResult<Path, Key extends keyof Path> =
    Path[Key] extends {post: {responses: infer Responses}}
        ? {
                data:     Responses extends {201: {content: {"application/json": infer ResponseBody}}} ? ResponseBody : undefined;
                error:    unknown;
                response: unknown;
            }
        : ErrorResult;

type PutResult<Path, Key extends keyof Path> =
    Path[Key] extends {put: {responses: infer Responses}}
        ? {
                data:     Responses extends {200: {content: {"application/json": infer ResponseBody}}} ? ResponseBody : undefined;
                error:    unknown;
                response: unknown;
            }
        : ErrorResult;

type PatchResult<Path, Key extends keyof Path> =
    Path[Key] extends {patch: {responses: infer Responses}}
        ? {
                data:     Responses extends {200: {content: {"application/json": infer ResponseBody}}} ? ResponseBody : undefined;
                error:    unknown;
                response: unknown;
            }
        : ErrorResult;

type DeleteResult<Path, Key extends keyof Path> =
    Path[Key] extends {delete: {responses: infer Responses}}
        ? {
                data:     Responses extends {204: {content: {"application/json": infer ResponseBody}}} ? ResponseBody : undefined;
                error:    unknown;
                response: unknown;
            }
        : ErrorResult;

export type ErrorResult          = {data: undefined, error: unknown, response: unknown};
export type RequestOptionsParams = {params: any};
export type RequestOptionsBody   = {params: any, body: any};
