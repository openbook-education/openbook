/*
 * OpenBook: Interactive Online Textbooks
 * © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import type {Readable}     from "svelte/store";
import type {Subscriber}   from "svelte/store";
import type {Unsubscriber} from "svelte/store";
import type {Updater}      from "svelte/store";
import type {Writable}     from "svelte/store";

import {get}      from "svelte/store";
import {readable} from "svelte/store";
import {writable} from "svelte/store";

/**
 * Object-oriented version of a readable store. This makes it easier to implement
 * custom stores with additional methods, than with Svelte's functional stores.
 *
 * For a custom store simply a new class with additional methods must be derived.
 * Inside the methods the protected `set()` and `update()` methods can be called
 * to replace or update the store's value.
 *
 * Additionally, the store contains a `value` property (getter method), that can
 * be used to read its value without subscription, e.g. in plain TypeScript code.
 */
export class ReadableStore<T> {
    private _store!:  Readable<T>;
    private _set!:    (value: T) => void;
    private _update!: (fn: Updater<T>) => void;

    /**
     * Initialize a new store object.
     * @param defaultValue Default store value
     */
    constructor(defaultValue: T) {
        this._store = readable(defaultValue, (set, update) => {
            this._set    = set;
            this._update = update;
        });
    }

    /**
     * Store contract: Subscribe
     */
    subscribe(run: Subscriber<T>, invalidate?: () => void): Unsubscriber {
        return this._store.subscribe(run, invalidate);
    }

    /**
     * Get current value without subscription.
     */
    get value(): T {
        return get(this._store);
    }

    /**
     * Set new value.
     */
    protected set(value: T) {
        this._set(value);
    }

    /**
     * Modify the current value. The callback function receives the current value
     * and must return a new value.
     */
    protected update(fn: Updater<T>) {
        this._update(fn);
    }

    /**
     * Internal method for other stores to set a new value.
     *
     * Note, even though this class is a readable store, this method is deliberately
     * publicly exposed. From the view's point of view that store is still read-only,
     * sine the `set()` method of the store contract is not exposed. But other stores,
     * using this one internally, get a public API to push new values to the views.
     */
    public changeValue(value: T) {
        this._set(value);
    }
}

/**
 * Object-oriented version of a writable store. This makes it easier to implement
 * custom stores with additional methods, than with Svelte's functional stores.
 *
 * For a custom store simply a new class with additional methods must be derived.
 * Inside the methods the protected `set()` and `update()` methods can be called
 * to replace or update the store's value.
 *
 * Additionally, the store contains a `value` property (getter method), that can
 * be used to read its value without subscription, e.g. in plain TypeScript code.
 */
export class WritableStore<T> {
    private _store!:  Writable<T>;
    private _set!:    (value: T) => void;
    private _update!: (fn: Updater<T>) => void;

    /**
     * Initialize a new store object.
     * @param defaultValue Default store value
     */
    constructor(defaultValue: T) {
        this._store = writable(defaultValue, (set, update) => {
            this._set    = set;
            this._update = update;
        });
    }

    /**
     * Store contract: Subscribe
     */
    subscribe(run: Subscriber<T>, invalidate?: () => void): Unsubscriber {
        return this._store.subscribe(run, invalidate);
    }

    /**
     * Get current value without subscription.
     */
    get value(): T {
        return get(this._store);
    }

    /**
     * Set new value.
     */
    set(value: T) {
        this._set(value);
    }

    /**
     * Modify the current value. The callback function receives the current value
     * and must return a new value.
     */
    update(fn: Updater<T>) {
        this._update(fn);
    }

    /**
     * Internal method for other stores to set a new value. Kept for compatibility
     * with the `ReadableStore` class, even though this is writeable store.
     */
    public changeValue(value: T) {
        this._set(value);
    }
}
