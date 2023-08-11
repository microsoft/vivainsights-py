# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import matplotlib
matplotlib.use('agg')

sys.path.insert(0, os.path.abspath('..'))
project = 'vivainsights'
copyright = '2023, Microsoft Corporation'
author = 'Martin Chan'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["myst_parser", "sphinx.ext.autodoc", "sphinx.ext.viewcode", "sphinx.ext.todo"]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Add path to logo and favicon
html_logo = '_static/vivainsights-py.png'
html_favicon = '_static/favicon.svg'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']

html_theme_options = {
    'github_user': 'microsoft',
    'github_repo': 'vivainsights-py',
    'github_banner': True,
    'github_button': True,
    'github_type': 'star',
    'github_count': 'true',
    'show_related': 'true',
}