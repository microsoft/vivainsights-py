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

# Add the parent directory to sys.path to make vivainsights importable
sys.path.insert(0, os.path.abspath('..'))

# Try to import vivainsights to check if it's available
try:
    import vivainsights
except ImportError as e:
    print(f"Warning: Could not import vivainsights: {e}")

# Mock imports for autodoc in case some dependencies are missing
autodoc_mock_imports = ["adjustText", "PyQt5", "igraph"]
    
project = 'vivainsights'
copyright = '2026, Microsoft Corporation'
author = 'Martin Chan'
release = '0.4.2'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
  "myst_parser",
  "sphinx.ext.autodoc",
  "sphinx.ext.napoleon",
  "sphinx.ext.viewcode",
  "sphinx.ext.autosummary",
  "sphinx.ext.todo",
  "nbsphinx",
  "sphinx_design"
]

# Enable MyST extensions
myst_enable_extensions = [
    "colon_fence",
    "deflist"
]

# Generate the autosummary pages
autosummary_generate = True

# Autodoc configuration for better presentation
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'member-order': 'bysource',
    'class-doc-from': 'both'
}

# Make autodoc more compact
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'autosummary_collapsible.rst', 'setup.rst']

# Add path to logo and favicon
html_logo = '_static/vivainsights-py.png'
html_favicon = '_static/favicon.svg'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']

# Custom CSS files
html_css_files = [
    'custom.css',
]

# Recognize both .rst and .md files as source files
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
