#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import json
import sphinx
import os
from collections import Counter
from pathlib import Path

__version__ = "0.1.0"

def setup(app):
    app.connect("doctree-resolved", get_links)
    app.connect("builder-inited", create_objects)
    app.connect("build-finished", create_json)

    return {
        "version": __version__,
        "parallel_read_safe": False,
        "parallel_write_safe": True,
    }


def create_objects(app):
    builder = getattr(app, "builder", None)
    if builder is None:
        return
    builder.env.app.nodes = []
    builder.env.app.links = []
    builder.env.app.pages = []
    builder.env.app.groups = []


def get_links(app, doctree, docname):
    references = []

    for node in doctree.traverse():
        # add internal references
        if node.tagname == 'reference' and 'internal' in node.attributes and node.attributes['internal'] and 'refuri' in node.attributes and node.attributes['refuri']:
            ref = node.attributes['refuri'].split("#")[0]
            absolute_ref = os.path.normpath(os.path.join(os.path.dirname(f"/{docname}.html"), ref))

            references.append((f"/{docname}.html", absolute_ref))

            if not f"/{docname}.html".split('/')[1] in app.env.app.groups:
                app.env.app.groups.append(f"/{docname}.html".split('/')[1])

            if not absolute_ref.split('/')[1] in app.env.app.groups:
                app.env.app.groups.append(absolute_ref.split('/')[1])

            if not f"/{docname}.html" in app.env.app.pages:
                app.env.app.pages.append(f"/{docname}.html")

            if not absolute_ref in app.env.app.pages:
                app.env.app.pages.append(absolute_ref)

            #TODO add description for logic
            if not any(d.get("id") == app.env.app.pages.index(f"/{docname}.html") for d in app.env.app.nodes):
                # print("first", f"/{docname}.html",app.env.app.pages.index(f"/{docname}.html"))
                if app.env.titles.get(docname):
                    title = app.env.titles.get(docname).astext()
                else:
                    title = f"/{docname}.html"
                app.env.app.nodes.append({
                    "id": app.env.app.pages.index(f"/{docname}.html"),
                    "group": app.env.app.groups.index(f"/{docname}.html".split('/')[1]),
                    "label": title,
                    "path": f"/{docname}.html",
                    "level": 1
                })

            #TODO add description for logic
            if not any(d.get("id") == app.env.app.pages.index(absolute_ref) for d in app.env.app.nodes):
                # print("second", absolute_ref,app.env.app.pages.index(absolute_ref))
                if app.env.titles.get(absolute_ref):
                    title = app.env.titles.get(absolute_ref).astext()
                else:
                    title = absolute_ref
                app.env.app.nodes.append({
                    "id": app.env.app.pages.index(absolute_ref),
                    "group": app.env.app.groups.index(absolute_ref.split('/')[1]),
                    "label": title,
                    "path": absolute_ref,
                    "level": 1
                })

    #TODO add description for logic
    references_counts = Counter(references)
    for ref, count in references_counts.items():
        app.env.app.links.append({
            "target": app.env.app.pages.index(ref[1]),
            "source": app.env.app.pages.index(ref[0]),
            "strength": 1 #TODO calculate strength based on highest count
        })


def create_json(app, exception):
    filename = Path(app.outdir) / "_static" / "links.json"
    with open(filename, "w") as json_file:
        json_file.write(f'var links = {json.dumps(app.env.app.links, indent=4)};')

    filename = Path(app.outdir) / "_static" / "nodes.json"
    with open(filename, "w") as json_file:
        json_file.write(f'var nodes = {json.dumps(app.env.app.nodes, indent=4)};')

    filename = "link-graph.html"
    sphinx.util.fileutil.copy_asset_file(
        os.path.join(os.path.dirname(__file__), "static", "html", filename),
        os.path.join(app.builder.outdir, '_static', filename)
    )

    filename = "link-graph.js"
    sphinx.util.fileutil.copy_asset_file(
        os.path.join(os.path.dirname(__file__), "static", "js", filename),
        os.path.join(app.builder.outdir, '_static', filename)
    )
