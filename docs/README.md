# Documentation

## Sphinx

### For initialization

Initialize requirements of documentation generation:

```bash
pip install -r requirements/pypi-doc.txt
```

Initialize Sphinx project:

```bash
mkdir docs && cd docs
sphinx-quickstart

# Tips for the interactive configuration phase
#   Choose the option "Separate sources from build"
#   Reference: https://stackoverflow.com/questions/65829149/what-does-separate-source-and-build-directories-mean
```

Build HTML:

```bash
cd build
make html
```

### For incremental changes

As documentation of the current project has already been set up, you can only run `make-html.sh` instead of the previous steps:

.. literalinclude:: ../../../make-html.sh
  :language: bash


### Start the server and view the documentation pages

Start the HTTP server on the remote side

```bash
cd docs/build/html
python -m http.server 8080 -b localhost
```

Create an SSH tunneling on the local side, which forwards connections/requests from local to remote (server)

```bash
ssh -L 8080:localhost:8080 remote-server
```

## Use RST Files within the Sphinx Documentation

### Include Markdown

For including Markdown files into the Sphinx documentation, this project utilizes `m2r2` which needs to be installed through `pip`:

```
pip install m2r2
```

Then in `.rst` file, use the `.. mdinclude::` directive to include Markdown file. The path needs to be relative to the `.rst` file.

```
.. mdinclude:: ../../../README.md
```

### Include Code snippets

Use the `.. literalinclude::` directive to include a code snippet from a script/source file.

For example,

```
.. literalinclude:: ../../../make-html.sh
  :language: bash
```

results in:

.. literalinclude:: ../../../make-html.sh
  :language: bash

## Auto-Generation of API Documentations

The feature of auto-documentation is realized by various Sphinx extensions and third-party tools.

This project adopts [Google-style Python docstrings](https://google.github.io/styleguide/pyguide.html), [Example Google Style Python Docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) for auto-generation of Python API pages.

The authors would like to thank [PyTorch](https://pytorch.org/docs/stable/index.html) for being an exemplar of documentation.

Reference:

* https://sphinx-rtd-theme.readthedocs.io/en/stable/demo/api.html

### Python documentation

Sphinx can utilize Napoleon for auto-generation of API pages of Python code.

```python
import os
import sys
sys.path.insert(0, os.path.abspath(path_to_python_module_dir))
sys.path.insert(0, os.path.abspath(path_to_python_module2_dir))
...

extensions = [
  ...
  'sphinx.ext.autodoc',   # support for auto-doc generation
  'sphinx.ext.napoleon',  # support for numpy / google style
]
```

References:

* https://sphinxcontrib-napoleon.readthedocs.io/en/latest/
* https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
* https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
* https://sphinx-intro-tutorial.readthedocs.io/en/latest/sphinx_extensions.html



### Doxygen documentation

This project utilizes Doxygen for auto-generation of API pages of C++ SDK, and `breathe` for including these pages into the Sphinx documentation.

`breathe` needs to be installed through `pip`:

```bash
pip install breath
```

Firstly, XML files are generated:

```bash
cd sdk
doxygen Doxyfile-cpp
```

Then, in `conf.py`, set up `breathe` to include the XML generated in the previous step.

```python
extensions = [
  "...",
  "breathe",
]
sdk_name = "..."
breathe_projects = { sdk_name: "../../sdk/doxygen_output/xml/" }
breathe_default_project = sdk_name
```

Reference:

* https://www.doxygen.nl/manual/starting.html
* https://leimao.github.io/blog/CPP-Documentation-Using-Sphinx/
  * https://github.com/leimao/Sphinx-CPP-TriangleLib
* https://leimao.github.io/blog/CPP-Documentation-Using-Doxygen/
  * https://github.com/leimao/Doxygen-CPP-TriangleLib



### Protobuf documentation

This project uses `protoc-gen-doc`, an extension of the Protobuf compiler, to automatically generate API pages for Protobuf definitions.

To activate this extension, pass `--doc_out` argument to `protoc`.

```bash
protoc ... \
    --doc_out ${doc_output_dir} \
    ...
```

References:

* https://github.com/pseudomuto/protoc-gen-doc
