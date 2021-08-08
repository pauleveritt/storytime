"""Sphinx configuration."""
from datetime import datetime


project = "Storytime"
author = "Paul Everitt"
copyright = f"{datetime.now().year}, {author}"
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
]
autodoc_typehints = "description"
html_theme = "furo"
myst_enable_extensions = [
    "colon_fence",
]
myst_url_schemes = ["http", "https", "mailto"]
