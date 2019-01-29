from .._common import (config as c, path as p)
from ._crawler import crawl_all_nodes
from pathlib import Path
import yaml


def execute(confpath, max_tab, path, headless):
    config = c.parse(confpath)
    basepath = p.create_basepath(path, config.name)

    for result in crawl_all_nodes(config, max_tab, basepath, headless):
        saved = _save_stylesheets(basepath, result)
        _save_result(basepath, result, saved)


def _save_stylesheets(basepath, result):
    saved = []
    for stylesheet in result.stylesheets:
        path = basepath / result.device / result.node.name / "stylesheets" / p.encode_css_name(stylesheet.url)
        path.parent.mkdir(exist_ok=True, parents=True)
        with path.open("w") as f:
            f.write(stylesheet.text)
        saved.append({"url": stylesheet.url, "path": path.name})
    return saved


def _save_result(basepath, result, saved):
    path = basepath /result.device / result.node.name / "result.yml"
    path.parent.mkdir(exist_ok=True, parents=True)
    with path.open("w") as f:
        f.write(yaml.dump({
            "name": result.node.name,
            "url": result.node.url,
            "redirected": result.html.url,
            "stylesheets": saved,
            "capture_path": result.capture_path
            }, default_flow_style=False))