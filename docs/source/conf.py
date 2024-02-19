# fmt: off
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import logging
logging.basicConfig(level=logging.INFO)

conf_py_file = os.path.dirname(__file__)
project_dir = os.path.realpath(f'{conf_py_file}/../../')
proto_dir = f'{project_dir}/common/proto/proto_gen_py'

# Reference: https://stackoverflow.com/questions/10324393/sphinx-build-fail-autodoc-cant-import-find-module
sys.path.append(project_dir)
sys.path.append(proto_dir)
logging.info('sys.path:')
for p in sys.path:
    logging.info(p)

project = 'DRL-based Trajectory Tracking (DRLTT)'
copyright = '2024, Yinda Xu, Lidong Yu'
author = 'Yinda Xu, Lidong Yu'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'myst_parser',  # substitute of `recommonmark`
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

import sphinx_rtd_theme
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = []
