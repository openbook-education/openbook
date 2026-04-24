/*
 * OpenBook: Interactive Online Textbooks
 * © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 */

import fs      from "node:fs/promises";
import path    from "node:path";
import process from "node:process";

import {Ajv}   from "ajv";
import {glob}  from "glob";
import JSZip   from "jszip";
import shelljs from "shelljs";
import yaml    from "yaml";

/**
 * Shared logic for all scripts to determine the build options.
 */
export function getOptions() {
    const cwd  = process.cwd();

    return {
        infile: path.join(cwd, "src", "index.ts"),
        watch:  process.argv[2] === "--watch",

        outfiles:  [
            path.join(cwd, "dist", "library.js"),
        ],

        plugins: [
            logHeader(cwd),
            validateAndCopyComponentYml(cwd, path.join(cwd, "dist")),
            createLibraryYml(cwd, path.join(cwd, "dist", "library.yml")),
            createLibraryZip(path.join(cwd, "dist"), path.join(cwd, "zip", "library.zip")),
            copyToInstallLocation(
                cwd,
                path.join(cwd, "zip", "library.zip"),
                path.join(cwd, "..", "..", "_media", "lib-install")),
        ],
    };
}

/**
 * Internal plugin that logs a header with the name of the currently built library.
 * @param {string} cwd Root directory of the library
 * @returns esbuild plug-in instance
 */
function logHeader(cwd) {
    return {
        name: "logHeader",
        setup(build) {
            try {
                build.onStart(async () => {
                    let packageJsonFile = await fs.readFile(path.join(cwd, "package.json"), "utf-8");
                    let packageJson     = JSON.parse(packageJsonFile);
                    let logLine         = `Building library ${packageJson.name} ${packageJson.version}`;
                    let separator       = "=".repeat(logLine.length);
    
                    console.log();
                    console.log(separator);
                    console.log(logLine);
                    console.log(separator);
                    console.log();
                });
            } catch (err) {
                console.error(err);
                throw err;
            }
        },
    };
}

/**
 * Copy YML files describing the custom components to the WYSIWYG editor to a
 * new directory called `components`. Also validates the YML files and raises
 * an error when validation fails.
 * 
 * @param {string} cwd Root directory of the library
 * @param {string} outdir Build output directory
 * @returns esbuild plug-in instance
 */
function validateAndCopyComponentYml(cwd, outdir) {
    return {
        name: "copyComponentYml",
        setup(build) {
            build.onEnd(async () => {
                try {
                    console.log("COPY COMPONENT YAML FILES");
    
                    let srcDir              = path.join(cwd, "src");
                    let componentSchemaFile = await fs.readFile(path.join(import.meta.dirname, "component-schema.yml"), "utf-8");
                    let componentSchemaYml  = yaml.parse(componentSchemaFile);
                    let ajv = new Ajv();
    
                    for (let srcFile of await glob([path.join(srcDir, "**", "*.yml")])) {
                        // Validate file
                        let componentFile = await fs.readFile(path.join(srcFile), "utf-8");
                        let componentYml  = yaml.parse(componentFile);
    
                        await ajv.validate(componentSchemaYml, componentYml);
                        if (ajv.errors) throw ajv.errors;
    
                        // Copy file
                        srcFile = path.relative(srcDir, srcFile);
                        shelljs.mkdir("-p", path.join(outdir, "components", path.dirname(srcFile)));
                        shelljs.cp("-R", path.join("src", srcFile), path.join(outdir, "components", srcFile));
                    }
                } catch (err) {
                    console.error(err);
                    throw err;
                }
            });
        },
    };
}

/**
 * Internal plugin that reads the meta-data from `package.json` and `README.md`
 * to creates the `library.yml` file. This file is used by the OpenBook server
 * when installing a library to check that it is a valid library and show some
 * information to the admin.
 * 
 * @param {string} cwd Root directory of the library
 * @param {string} outfile Path of the created file
 * @returns esbuild plug-in instance
 */
function createLibraryYml(cwd, outfile) {
    return {
        name: "createLibraryYmlPlugin",
        setup(build) {
            build.onEnd(async () => {
                try {
                    console.log("CREATE LIBRARY YAML");
    
                    let packageJsonFile = await fs.readFile(path.join(cwd, "package.json"), "utf-8");
                    let packageJson     = JSON.parse(packageJsonFile);
                    let readmeFile      = await fs.readFile(path.join(cwd, "README.md"), "utf-8");
    
                    let data = {
                        name:         packageJson.name               || "",
                        version:      packageJson.version            || "",
                        author:       packageJson.author             || "",
                        license:      packageJson.license            || "",
                        website:      packageJson.homepage           || "",
                        coderepo:     packageJson.repository?.url    || "",
                        bugtracker:   packageJson.bugs?.url          || "",
                        dependencies: packageJson["ob-dependencies"] || {},
                        description:  packageJson["ob-translated-description"] || {en: packageJson.description || ""},
                        readme:       readmeFile,
                    };
    
                    await fs.writeFile(outfile, yaml.stringify(data, {lineWidth: 0}));
                } catch (err) {
                    console.error(err);
                    throw err;
                }
            });
        },
    };
}

/**
 * Internal plugin that creates a ZIP file with the bundled library source code,
 * ready to be installed on the OpenBook server.
 * 
 * @param {string} distdir Directory with the pre-built distribution files
 * @param {string} outfile Path of the created file
 * @returns esbuild plug-in instance
 */
function createLibraryZip(distdir, outfile) {
    return {
        name: "createLibraryZipPlugin",
        setup(build) {
            build.onEnd(async () => {
                try {
                    console.log("CREATE LIBRARY ZIP");
    
                    try {
                        await fs.unlink(outfile);
                    } catch {
                        // File didn't exist                
                    }
    
                    fs.mkdir(path.dirname(outfile), {recursive: true});
                    
                    let zip = new JSZip();
                    let folder = zip.folder("openbook-library");
    
                    async function _addDirectoryContent(zip, srcdir) {
                        for (let entry of await fs.readdir(srcdir, {withFileTypes: true})) {
                            let entryPath = path.join(srcdir, entry.name);
    
                            if (entry.isDirectory()) {
                                let subfolder = zip.folder(entry.name);
                                await _addDirectoryContent(subfolder, entryPath);
                            } else {
                                let data = await fs.readFile(entryPath);
                                zip.file(entry.name, data);   
                            }
                        }
                    }
    
                    await _addDirectoryContent(folder, distdir);
                    let zipContent = await zip.generateAsync({type: "nodebuffer"});
                    await fs.writeFile(outfile, zipContent);
                } catch (err) {
                    console.error(err);
                    throw err;
                }
            });
        },
    };
}

/**
 * Internal plugin that copies and renames the built ZIP file so that can be
 * automatically installed by the OpenBook server.
 * 
 * @param {string} cwd Root directory of the library
 * @param {string} zipfile Path to the built ZIP file
 * @param {string} outdir Install directory
 * @returns esbuild plug-in instance
 */
function copyToInstallLocation(cwd, zipfile, outdir) {
    return {
        name: "copyToInstallLocation",
        setup(build) {
            build.onEnd(async () => {
                try {
                    console.log("COPY LIBRARY ZIP TO INSTALL LOCATION");
                    
                    let packageJsonFile = await fs.readFile(path.join(cwd, "package.json"), "utf-8");
                    let packageJson     = JSON.parse(packageJsonFile);
                    let dstFile         = `${packageJson.name.slice(1)}_${packageJson.version}.zip`.replaceAll("/", "_");

                    shelljs.mkdir("-p", path.dirname(path.join(outdir, dstFile)));
                    shelljs.cp("-R", zipfile, path.join(outdir, dstFile));
                } catch (err) {
                    console.error(err);
                    throw err;
                }
            });
        },
    };
}