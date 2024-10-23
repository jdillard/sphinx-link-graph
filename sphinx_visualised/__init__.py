#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import json
import sphinx
import os
from collections import Counter
from pathlib import Path

__version__ = "0.2.2"


def setup(app):
    app.connect("builder-inited", create_objects)
    app.connect("doctree-resolved", get_links)
    app.connect("build-finished", create_json)

    return {
        "version": __version__,
        "parallel_read_safe": False,
        "parallel_write_safe": True,
    }


def create_objects(app):
    """
    Create objects when builder is initiated
    """
    builder = getattr(app, "builder", None)
    if builder is None:
        return
    builder.env.app.nodes = [] # a list of nodes and their metadata
    builder.env.app.links = [] # a list of links between pages
    builder.env.app.pages = [] # an index of page names
    builder.env.app.groups = [] # an index of page groups


def get_links(app, doctree, docname):
    """
    Gather internal link connections
    """
    references = [] # a list of every internal reference made between pages

    for node in doctree.traverse():
        # add internal references
        if node.tagname == 'reference' and 'internal' in node.attributes and node.attributes['internal'] and 'refuri' in node.attributes and node.attributes['refuri']:
            ref = node.attributes['refuri'].split("#")[0]
            # path of the referenced page
            absolute_ref = os.path.abspath(os.path.join(os.path.dirname(f"/{docname}.html"), ref))[1:-5]

            # add each link as an individual reference
            references.append((f"/{docname}.html", f"/{absolute_ref}.html"))

            # a group is the name of the top level directory
            docname_group = f"/{docname}.html".split('/')[1]
            if not docname_group in app.env.app.groups:
                app.env.app.groups.append(docname_group)

            absolute_ref_group = f"/{absolute_ref}.html".split('/')[1]
            if not absolute_ref_group in app.env.app.groups:
                app.env.app.groups.append(absolute_ref_group)

            # add to index of page names
            if not f"/{docname}.html" in app.env.app.pages:
                app.env.app.pages.append(f"/{docname}.html")

            if not f"/{absolute_ref}.html" in app.env.app.pages:
                app.env.app.pages.append(f"/{absolute_ref}.html")

            # check if node exists based on docname's id
            if not any(d.get("id") == app.env.app.pages.index(f"/{docname}.html") for d in app.env.app.nodes):
                if app.env.titles.get(docname):
                    title = app.env.titles.get(docname).astext()
                else:
                    title = f"/{docname}.html"

                app.env.app.nodes.append({
                    "id": app.env.app.pages.index(f"/{docname}.html"),
                    "group": app.env.app.groups.index(docname_group),
                    "label": title,
                    "path": f"../{docname}.html",
                    "level": 1
                })

            # check if node exists based on absolute_ref's id
            if not any(d.get("id") == app.env.app.pages.index(f"/{absolute_ref}.html") for d in app.env.app.nodes):
                if app.env.titles.get(absolute_ref):
                    title = app.env.titles.get(absolute_ref).astext()
                else:
                    title = f"/{absolute_ref}.html"

                app.env.app.nodes.append({
                    "id": app.env.app.pages.index(f"/{absolute_ref}.html"),
                    "group": app.env.app.groups.index(absolute_ref_group),
                    "label": title,
                    "path": f"../{absolute_ref}.html",
                    "level": 1
                })

    # create object that links references between pages
    references_counts = Counter(references)
    for ref, count in references_counts.items():
        #TODO check if unique else strength++
        app.env.app.links.append({
            "target": app.env.app.pages.index(ref[1]),
            "source": app.env.app.pages.index(ref[0]),
            "strength": 1,
        })


def build_toctree_hierarchy(app):
    """
    Take toctree_includes and build the hierarchy while gathering page metadata.
    """
    node_map = {}
    data = app.env.toctree_includes

    for key, value in data.items():
        if key not in node_map:
            node_map[key] = {
                "id": key,
                "label": app.env.titles.get(key).astext(),
                "path": f"../{key}.html",
                "children": [],
            }

        for child in data[key]:
            if child not in node_map:
                node_map[child] = {
                    "id": child,
                    "label": app.env.titles.get(child).astext(),
                    "path": f"../{child}.html",
                    "children": [],
                }
            node_map[key]["children"].append(node_map[child])

    return node_map[app.builder.config.root_doc]


def create_json(app, exception):
    """
    Create static files for visualizations
    """
    filename = Path(app.outdir) / "_static" / "links.js"
    with open(filename, "w") as json_file:
        json_file.write(f'var links = {json.dumps(app.env.app.links, indent=4)};')

    filename = Path(app.outdir) / "_static" / "nodes.js"
    with open(filename, "w") as json_file:
        json_file.write(f'var nodes = {json.dumps(app.env.app.nodes, indent=4)};')

    filename = Path(app.outdir) / "_static" / "toctree.js"
    with open(filename, "w") as json_file:
        json_file.write(f'var toctree = {json.dumps(build_toctree_hierarchy(app), indent=4)};')

    filename = "link-graph.html"
    sphinx.util.fileutil.copy_asset_file(
        os.path.join(os.path.dirname(__file__), "static", "html", filename),
        os.path.join(app.builder.outdir, '_static', filename),
        force=True,
    )

    filename = "link-graph.js"
    sphinx.util.fileutil.copy_asset_file(
        os.path.join(os.path.dirname(__file__), "static", "js", filename),
        os.path.join(app.builder.outdir, '_static', filename),
        force=True,
    )

    filename = "toctree-graph.html"
    sphinx.util.fileutil.copy_asset_file(
        os.path.join(os.path.dirname(__file__), "static", "html", filename),
        os.path.join(app.builder.outdir, '_static', filename),
        force=True,
    )

    filename = "toctree-graph.js"
    sphinx.util.fileutil.copy_asset_file(
        os.path.join(os.path.dirname(__file__), "static", "js", filename),
        os.path.join(app.builder.outdir, '_static', filename),
        force=True,
    )
