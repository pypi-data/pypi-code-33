import yaml
from pathlib import Path
from difflib import unified_diff
from .._common import (config as c, path as p)
from ._view import ReportBuilder


def execute(confpath, today, yesterday, path):
    config = c.parse(confpath)
    if not today:
        today = p.current_date(0)
    if not yesterday:
        yesterday = p.current_date(-1)
    
    basepath = Path(path).resolve() / config.name
    m = NodeManager(basepath, config)
    rb = ReportBuilder(basepath, f"{yesterday}-{today}")

    df_list = [AssetsDiffs.parse(t, y) for t, y in zip(m.iter_nodes(today), m.iter_nodes(yesterday))]

    for diffs in df_list:
        with rb.each_page(diffs) as ep:
            ep.build()
        
    with rb.top_page(df_list) as tp:
        tp.build()


class NodeManager(object):
    def __init__(self, basepath, config):
        self._config = config
        self._basepath = basepath / "logs"

    def iter_nodes(self, date):
        basepath = p.current_path(self._basepath, date)
        for devcon in self._config:
            for node in devcon.nodes:
                path = basepath / devcon.device
                yield Reader(path / node.name, devcon)
                yield from (Reader(path / c.name, devcon) for c in node.childs)


class AssetsDiffs(object):
    def __init__(self, name, device, nodename, today, yesterday, after_path, before_path):
        # TODO:: 引数の順番
        self._today = {x.id_url: x for x in today}
        self._yesterday = {x.id_url: x for x in yesterday}
        self.name = name
        self.device = device
        self.nodename = nodename
        self.before_capture_path = before_path
        self.after_capture_path = after_path

    @classmethod
    def parse(cls, today, yesterday):
        return cls(today.name, today.device, today.nodename,
                   today.iter_stylesheets(), yesterday.iter_stylesheets(),
                   today.capture_path, yesterday.capture_path)

    @property
    def added(self):
        keys = set(self._today.keys()) - set(self._yesterday.keys())
        return [self._today[k] for k in keys]

    @property
    def deleted(self):
        keys = set(self._yesterday.keys()) - set(self._today.keys())
        return [self._yesterday[k] for k in keys]

    @property
    def diffs(self):
        keys = set(self._today.keys()) & set(self._yesterday.keys())
        return [FileDiff(self._today[k], self._yesterday[k]) for k in keys]


class FileDiff(object):
    def __init__(self, today_asset, yesterday_asset):
        self._t = today_asset
        self._y = yesterday_asset
        with today_asset.path.open("r") as tf, yesterday_asset.path.open("r") as yf:
            self.diff = "".join(unified_diff(tf.readlines(), yf.readlines()))
    
    @property
    def url(self):
        return self._t.url

    @property
    def id_url(self):
        return self._t.id_url


class Reader(object):
    def __init__(self, path, deviceconfig):
        self._deviceconfig = deviceconfig
        self._path = path
        with (path / "result.yml").open("r") as f:
            self.result = yaml.load(f)
        self.capture_path = Path(self.result["capture_path"]).resolve()
    
    @property
    def name(self):
        return self._deviceconfig.name

    @property
    def device(self):
        return self._deviceconfig.device

    @property
    def nodename(self):
        return self.result["name"]

    def iter_stylesheets(self):
        for s in self.result["stylesheets"]:
            yield StyleSheetInfomation(s["url"], self._path / "stylesheets" / s["path"])


class StyleSheetInfomation(object):
    def __init__(self, url, path):
        self.url = url
        self.path = path
    
    @property
    def id_url(self):
        # TODO:: 数字はバージョンであることが多いので塗りつぶす
        return p.identify_url(self.url)