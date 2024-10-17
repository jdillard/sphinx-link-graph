# Sphinx visualization extension

A Sphinx extension to generate interactive visualizations.

[![PyPI version](https://img.shields.io/pypi/v/sphinx-visualised.svg)](https://pypi.python.org/pypi/sphinx-visualised)
![Parallel safe](https://img.shields.io/badge/parallel%20safe-false-red)

## Installing

Directly install via pip by using:

```
pip install sphinx-visualised
```

Add `sphinx_visualised` to the [extensions](https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-extensions) array in your Sphinx **conf.py**.
For example:

```python
extensions = ['sphinx_visualised']
```

## Usage

After building the docs, open one of the following in the browser:

- `/_static/link-graph.html` 
- `/_static/toctree-graph.html` 

## Inspiration

- https://github.com/ninjaconcept/d3-force-directed-graph
