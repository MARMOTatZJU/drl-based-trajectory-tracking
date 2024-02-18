# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
project_root_dir = os.path.realpath(f'{os.path.dirname(__file__)}/../..')  # hardcoded
os.environ['PYTHONPATH'] = f'{project_root_dir}:{os.environ.get('PYTHONPATH', '')}'

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
