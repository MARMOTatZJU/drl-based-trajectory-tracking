# Documentation


## Sphinx

This project adopts [Google-style Python docstrings](https://google.github.io/styleguide/pyguide.html), [Example Google Style Python Docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) for auto-generation of Python API pages.

The authors would like to thank [PyTorch](https://pytorch.org/docs/stable/index.html) for being an exemplar of documentation.

### For initialization

Initialize requirements of documentation generation:

```bash
pip install -r requirements/pypi-doc.txt
```

Initialize Sphinx project:

```bash
mkdir docs && cd docs
sphinx-quickstart
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


### Start the server and view documentation pages

Start the HTTP server on the remote side

```bash
cd docs/build/html
python -m http.server 8080 -b localhost
```

Create an SSH tunneling on the local side, which forwards connections/requests from local to remote (server)

```bash
ssh -L 8080:localhost:8080 remote-server
```

## Doxygen

Besides Sphinx, this project utilizes Doxygen for auto-generation of API pages of C++ SDK.

```bash
cd sdk
doxygen Doxyfile-cpp
```
