"""Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html

-- Project information -----------------------------------------------------
https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
"""
import os
import sys
from re import match

sys.path.insert(0, os.path.abspath("../"))

from uoshardware import PROJECT, __author__, __copywright__, __version__  # noqa: E402

project = PROJECT
# Copyright name shadowed by sphinx design.
copyright = __copywright__  # noqa
author = __author__
# The short MAJOR.MINOR version.
version = match(r"^\d.\d", __version__).group(0)
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
