# Documentation

This project adopts [Google-style Python docstrings](https://google.github.io/styleguide/pyguide.html), [Example Google Style Python Docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) for auto-generation of API pages .

The authors would like to thank [PyTorch](https://pytorch.org/docs/stable/index.html) for being an exemplar of documentation.

## For initialization

Initialize requirements of documentation generation:

```bash
pip install -r requirements/pypi-doc.txt
```

Initialize Sphinx project:

```bash
mkdir docs && cd docs
sphinx-quickstart
```

Build html:

```bash
cd build
make html
```

## For incremental changes

As documentation of current project has already been set up, you can only run `make-html.sh` instead of previous steps:

.. literalinclude:: ../../../make-html.sh
  :language: bash


## Start server and view documentation pages

Start http server on the remote side

```bash
cd build/html
python -m http.server 8080 -b localhost
```

Create a ssh tunneling on the local side, which forward connections/requests from local to remote (server)

```bash
ssh -L 8080:localhost:8080 remote-server
```
