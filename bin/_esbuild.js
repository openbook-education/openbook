/*
 * OpenBook: Interactive Online Textbooks
 * © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import * as esbuild from "esbuild";
import path         from "node:path";
import shelljs      from "shelljs";
import sveltePlugin from "esbuild-svelte";

/**
 * Centralized esbuild configuration to build JavaScript assets. This is used
 * by the higher-level build scripts which find the source files and determine
 * what destination files need to be created.
 *
 * There must be exactly one source file that imports all other files to be
 * included in the build. Normally a single bundle will be created from that.
 * For the libraries we however support creating multiple identical bundles
 * at different locations. Bundles always consist of a *.js and *.css file
 * plus copied over static files.
 *
 * @param {string} infile Full path of the main source file
 * @param {string[]} outfiles Full path of all bundle files to be created
 * @param {string[]} staticdirs Paths with static files to be copied (optional)
 * @param {bool} watch Keep running and rebuild on file changes (optional)
 * @param {object[]} plug-in Additional esbuild plug-ins (optional)
 */
export async function runEsbuild({infile, outfiles, staticdirs, watch, plugins} = {}) {
    plugins = plugins || [];

    let ctx = await esbuild.context({
        entryPoints: [infile],
        bundle:      true,
        minify:      true,
        outfile:     outfiles[0],
        sourcemap:   true,
        format:      "esm",

        mainFields: ["svelte", "browser", "module", "main"],
        conditions: ["svelte", "browser"],

        plugins: [
            sveltePlugin({
                compilerOptions: {
                    compatibility: {
                        componentApi: 4
                    },
                    customElement: true
                }
            }),
            additionalOutfilesPlugin(outfiles),
            staticFilesPlugin(outfiles, staticdirs),
            ...plugins
        ],

        loader: {
            ".svg":   "text",
            ".ttf":   "dataurl",
            ".woff":  "dataurl",
            ".woff2": "dataurl",
            ".eot":   "dataurl",
            ".jpg":   "dataurl",
            ".png":   "dataurl",
            ".gif":   "dataurl",
        },
    });

    if (watch) {
        console.log("esbuild - starting watch mode");
        await ctx.watch();
    } else {
        console.log("esbuild - building bundles");
        await ctx.rebuild();
        await ctx.dispose();
    }
}

/**
 * Internal plug-in that creates duplicate output files, if the same bundle
 * shall be built multiple times at different locations. The first entry of
 * the given array will be ignored as this is the file that esbuild creates
 * anyway. The plug-in just copies this file to the other locations after
 * the build.
 *
 * @param {string[]} outfiles Full path of bundle files to be created
 * @param {string[]} staticdirs Path with static files to be copied (optional)
 * @returns esbuild plug-in instance
 */
function additionalOutfilesPlugin(outfiles) {
    return {
        name: "additionalOutfilesPlugin",
        setup(build) {
            if (outfiles.length < 2) return;
            console.log(">>> CREATE ADDITIONAL OUTPUT FILES <<<");

            let bundle = path.parse(outfiles[0]);
            let src = path.join(bundle.dir, `${bundle.name}.*`);

            build.onEnd(() => {
                for (let outfile of outfiles.slice(1)) {
                    let dst = path.dirname(outfile);
                    shelljs.mkdir("-p", dst);
                    shelljs.cp("-R", src, dst);
                }
            });
        },
    };
}

/**
 * Internal plug-in that copies additional static files
 *
 * @param {string[]} outfiles Full path of all bundle files to be created
 * @param {string[]} staticdirs Paths with static files to be copied (optional)
 * @returns esbuild plug-in instance
 */
function staticFilesPlugin(outfiles, staticdirs) {
    return {
        name: "staticFilesPlugin",
        setup(build) {
            if (!outfiles   || outfiles.length   < 1) return;
            if (!staticdirs || staticdirs.length < 1) return;
            let watchDirsAdded = false;

            build.onLoad({filter: /.*/}, () => {
                // Dirty-Hack: We must add ourselves to the file loading handlers of esbuild,
                // without actually loading a file (then the next plugin is tried), just to
                // tell esbuild about additional files to watch in watch mode.
                let watchDirs  = [];    // Directories to watch for wew or deleted files or sub-directories
                let watchFiles = [];    // Files to watch for modifications

                if (!watchDirsAdded) {
                    for (let staticdir of staticdirs) {
                        let watchDir = getStaticWatchDir(staticdir);
                        if (!shelljs.test("-d", watchDir)) continue;

                        watchDirs.push(watchDir);

                        for (let entry of shelljs.ls("-lR", watchDir)) {
                            let fullname = path.join(watchDir, entry.name);

                            if (entry.isDirectory()) watchDirs.push(fullname);
                            else watchFiles.push(fullname);
                        }
                    }

                    watchDirsAdded = true;
                }

                return {watchDirs, watchFiles};
            });

            build.onEnd(build => {
                console.log(">>> COPY STATIC FILES <<<");

                for (let staticdir of staticdirs) {    
                    let staticFiles = getStaticCopySources(staticdir);
                    if (staticFiles.length < 1) continue;

                    for (let outfile of outfiles) {
                        let dst = path.dirname(outfile);
                        shelljs.mkdir("-p", dst);
                        shelljs.cp("-R", staticFiles, dst);
                    }
                }

                watchDirsAdded = false;
            });
        },
    };
}

/**
 * Returns the directory path to be watched for static assets.
 *
 * If `staticdir` ends with `*`, this strips the wildcard and returns only
 * the parent directory.
 *
 * @param {string} staticdir Static directory configuration value
 * @returns {string} Directory path for watch mode
 */
function getStaticWatchDir(staticdir) {
    return staticdir.endsWith("*") ? path.dirname(staticdir) : staticdir;
}

/**
 * Expands a static directory configuration value into copy sources.
 *
 * If the watched directory does not exist, an empty list is returned.
 * For wildcard values ending with `*`, all top-level entries are returned.
 * Otherwise the single configured path is returned.
 *
 * @param {string} staticdir Static directory configuration value
 * @returns {string[]} Paths to pass to `shelljs.cp`
 */
function getStaticCopySources(staticdir) {
    let watchDir = getStaticWatchDir(staticdir);

    if (!shelljs.test("-d", watchDir)) return [];
    if (!staticdir.endsWith("*")) return [staticdir];

    return shelljs.ls("-A", watchDir).map(entry => path.join(watchDir, entry));
}
