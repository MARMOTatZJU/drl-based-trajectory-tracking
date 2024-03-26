# fmt: off
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import subprocess
import logging
logging.basicConfig(level=logging.INFO)

conf_py_file = os.path.dirname(__file__)
project_dir = os.path.realpath(f'{conf_py_file}/../../')
proto_dir = f'{project_dir}/common/proto/proto_gen_py'
waymax_viz_dir = f'{project_dir}/submodules/waymax-visualization'  # TODO: consider move paths to a config files like YAML

# Reference: https://stackoverflow.com/questions/10324393/sphinx-build-fail-autodoc-cant-import-find-module
sys.path.append(project_dir)
sys.path.append(proto_dir)
sys.path.append(waymax_viz_dir)
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
    # 'myst_parser',  # substitute of `recommonmark`
    'm2r2',  # TODO: figure out why myst_parser does not work.
   'breathe',
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}

sdk_name = "drltt-sdk"
breathe_projects = { sdk_name: "../../sdk/doxygen_output/xml/" }
breathe_default_project = sdk_name

templates_path = ['_templates']
exclude_patterns = []



# -- Processing scripts ---------------------------------------------------

# Integrate Doxygen into Sphinx
# Reference: https://leimao.github.io/blog/CPP-Documentation-Using-Sphinx/
# subprocess.call('make clean', shell=True)
# logging.info('Compiling CPP documentation with Doxygen...')
# subprocess.call('cd ../../sdk ; doxygen Doxyfile-cpp ', shell=True)
# logging.info('CPP documentation compiled.')

# protoc-gen-doc
# logging.info('Compiling Protobuf documentation with Doxygen...')
# home_bin_dir = '/home/docs/.local/bin/'
# sys.path.append(home_bin_dir)  # TOOD: use $HOME instead
# append_path_prefix = (f'PATH=${{PATH}}:{home_bin_dir}')
# subprocess.call(f'cd ../../common/proto/proto_def ; {append_path_prefix}  bash compile_proto.sh ', shell=True)
# logging.info('Protobuf documentation compiled.')



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

import sphinx_rtd_theme
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = []
