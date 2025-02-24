# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
from recommonmark.parser import CommonMarkParser
source_suffix = ['.rst', '.md']
source_parsers = {
    '.md': CommonMarkParser,
}
sys.path.insert(0, os.path.abspath('../../'))
# print(sys.path)
project = 'Web_scraping'
copyright = '2025, Ryosuke Igarashi'
author = 'Ryosuke Igarashi'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'myst_parser'
]
templates_path = ['_templates']
exclude_patterns = []
language = 'ja'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'
# html_theme = 'sphinx_material'
html_static_path = ['_static']
