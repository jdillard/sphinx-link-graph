# Sphinx link graph extension

A Sphinx extension to generate an interactive graph of internal links.

![Parallel safe](https://img.shields.io/badge/parallel%20safe-false-red)

## Installing

Directly install via pip by using:

```
pip install sphinx-link-graph
```

Add `sphinx_gitstamp` to the [extensions](https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-extensions) array in your Sphinx **conf.py**.
For example:

```python
extensions = ['sphinx_link_graph']
```

## Usage

After building the docs, open `/_static/link-graph.html` in the browser.

## Inspiration

- https://github.com/ninjaconcept/d3-force-directed-graph
