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
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_llm.txt",
]

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "navigation_depth": 4,
    "titles_only": False,
}

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
