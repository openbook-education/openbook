"""Sphinx configuration for OpenBook documentation."""

import tomllib
from pathlib import Path

# Extract version string from pyproject.toml
pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"

with pyproject.open("rb") as f:
    release = tomllib.load(f)["tool"]["poetry"]["version"]

project = "OpenBook"
author = "Dennis Schulmeister-Zimolong and contributors"
copyright = "OpenBook contributors"

extensions = [
    "sphinx.ext.graphviz",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_llm.txt",
]

llms_txt_build_parallel = False     # Don't spawn subprocess to avoid race-conditions
autodoc_typehints = "description"   # Include type-hints in API docs

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "navigation_depth": 4,
    "titles_only": False,
}
html_static_path = ["_static", "_openapi"]
html_css_files = ["custom.css"]
html_logo = "_static/logo.svg"

# Ensure standalone OpenAPI HTML pages are published on RTD as build artifacts.
# NOTE: The files need to be manually updated and checked into git.
# html_extra_path = ["_openapi"]

exclude_patterns = ["Thumbs.db", ".DS_Store"]
