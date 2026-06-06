#!/usr/bin/env python3
"""
OpenBook: Interactive Online Textbooks
© 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
"""

from __future__  import annotations

import argparse
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

from dataclasses import dataclass


@dataclass(frozen=True)
class Endpoint:
    """Descriptor of a schema download target."""

    url: str
    output_file: str
    label: str

def parse_args() -> argparse.Namespace:
    """Parse and return command-line arguments for OpenAPI synchronization."""

    parser = argparse.ArgumentParser(description="Synchronize OpenAPI schemas to a local directory.")
    parser.add_argument("-u", default="http://localhost:8000", help="Base URL of the running OpenBook instance.")
    parser.add_argument("-d", default="", help="Django root directory. If provided, runserver is started there.")
    parser.add_argument("-o", default="", help="Output directory for downloaded OpenAPI specs.")
    parser.add_argument("-p", default="python", help="Python executable to use when starting Django.")
    return parser.parse_args()

def get_endpoints(args: argparse.Namespace) -> list[Endpoint]:
    """Return endpoints to query and respective output file names"""
    return [
        Endpoint(
            url         = f"{args.u}/api/schema/",
            output_file = "openbook.yaml",
            label       = "OpenBook REST API YAML schema",
        ),
        Endpoint(
            url         = f"{args.u}/api/schema/?format=json",
            output_file = "openbook.json",
            label       = "OpenBook REST API JSON schema",
        ),
        Endpoint(
            url         = f"{args.u}/auth-api/openapi.yaml",
            output_file = "auth.yaml",
            label       = "Authentication API YAML schema",
        ),
        Endpoint(
            url         = f"{args.u}/auth-api/openapi.json",
            output_file = "auth.json",
            label       = "Authentication API JSON schema",
        ),
        Endpoint(
            url         = f"{args.u}/ws/schema/",
            output_file = "asyncapi.json",
            label       = "Asynchronous WebSocket API",
        ),
    ]

def wait_for_server_ready(health_url: str, server_process: subprocess.Popen[object]) -> None:
    """Poll a health endpoint until the Django server responds or a timeout is reached."""

    timeout_ms = 30_000
    poll_interval_s = 0.5
    start = time.monotonic()

    while (time.monotonic() - start) * 1000 < timeout_ms:
        if server_process.poll() is not None:
            raise RuntimeError(f"Django server exited unexpectedly with code {server_process.returncode}")

        try:
            with urllib.request.urlopen(health_url, timeout=2) as response:
                if 200 <= response.status < 300:
                    return
        except (urllib.error.URLError, TimeoutError):
            # Ignore connection errors while waiting for server start.
            pass

        time.sleep(poll_interval_s)

    raise RuntimeError(f"Timed out while waiting for Django server at {health_url}")


def download(url: str, destination: str, label: str) -> None:
    """Download one schema document from url and write it to destination."""

    try:
        with urllib.request.urlopen(url) as response:
            if not 200 <= response.status < 300:
                raise RuntimeError(
                    f"Failed to download {label} from {url}: HTTP {response.status}"
                )

            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            f"Failed to download {label} from {url}: HTTP {exc.code}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to download {label} from {url}: {exc.reason}") from exc

    with open(destination, "w", encoding="utf-8") as file_handle:
        file_handle.write(body)

    print(f"Downloaded {label} -> {destination}")


def stop_server(child: subprocess.Popen[object] | None) -> None:
    """Terminate a spawned Django server process gracefully, then force kill if needed."""

    if child is None or child.poll() is not None:
        return

    child.terminate()

    try:
        child.wait(timeout=5)
    except subprocess.TimeoutExpired:
        child.kill()
        child.wait(timeout=5)


def main() -> int:
    """Run the OpenAPI synchronization workflow and return a process exit code."""

    args = parse_args()

    if not args.o:
        print("Output directory not given. Argument -o missing!", file=sys.stderr)
        return 1

    server_process: subprocess.Popen[object] | None = None

    try:
        os.makedirs(args.o, exist_ok=True)

        if args.d:
            server_process = subprocess.Popen(
                [args.p, "manage.py", "runserver", "--noreload"],
                cwd=args.d,
            )

            wait_for_server_ready(f"{args.u}/api/schema/?format=json", server_process)

        for endpoint in get_endpoints(args):
            destination = os.path.join(args.o, endpoint.output_file)
            download(endpoint.url, destination, endpoint.label)

        print(f"OpenAPI specs synchronized to {args.o}")
        return 0
    finally:
        stop_server(server_process)


if __name__ == "__main__":
    raise SystemExit(main())
