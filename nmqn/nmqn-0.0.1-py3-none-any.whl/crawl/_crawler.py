from nmqn.lib import crawler
from urllib.parse import urljoin
from pathlib import Path


def crawl_all_nodes(allconfig, max_tab, path, headless):
    for deviceconf in allconfig:
        client = CrawlClient(deviceconf, max_tab, Path(path) / deviceconf.device, headless)
        for node, result in client.crawl_all_nodes(deviceconf.nodes):
            yield NodeResponse(
                device=deviceconf.device,
                node=node,
                html=result.html,
                stylesheets=result.stylesheets,
                capture_path=result.capture_path)


class NodeResponse(object):
    def __init__(self, *, device, node, html, stylesheets, capture_path):
        self.device = device
        self.node = node
        self.html = html
        self.stylesheets = stylesheets
        self.capture_path = capture_path


class CrawlClient(object):
    def __init__(self, config, max_tab, path, headless):
        self._config = config
        self._max_tab = max_tab
        self._headless = headless
        self._path = path

    def crawl_all_nodes(self, nodes):
        if not nodes:
            return

        self._config.check_robots_txt(nodes)

        childs = []
        with crawler.SyncCrawler(max_tab=self._max_tab, headless=self._headless, capture_path=self._path, options=self._config.options) as c:
            for node, result in zip(nodes, c.walk(nodes)):
                yield node, result
                childs += [c.parse_child_node(result.html.absolute_links) for c in node.childs]

        yield from self.crawl_all_nodes(childs)