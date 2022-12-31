"""Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html

-- Project information -----------------------------------------------------
https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
"""
import os
import sys
from re import Match, match

sys.path.insert(0, os.path.abspath("../"))

from uoshardware import PROJECT, __author__, __copyright__, __version__

project = PROJECT
# Copyright name shadowed by sphinx design.
copyright = __copyright__
author = __author__
# The short MAJOR.MINOR version.
if isinstance(version_match := match(r"^\d.\d", __version__), Match):
    version = version_match.group(0)
else:
    version = "None"
# The full version, including alpha/beta/rc tags.
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_logo = "https://raw.githubusercontent.com/CreatingNull/NullTek-Assets/main/img/uos/UOSLogoSmall.png"
