import re
import yaml
from urllib.robotparser import RobotFileParser


def parse(path):
    """Parse user-prepared configuration file (yaml).

    Args:
        path (pathlib.Path/str): configuration file
    Returns:
        Config: Configuration class

    """
    with open(path, "r") as f:
        config = yaml.load(f)
    return Config.parse(config)


class Config(object):
    def __init__(self, name, deviceconfs):
        self.name = name
        self.deviceconfs = deviceconfs

    @classmethod
    def parse(cls, config):
        return cls(config["name"], [DeviceConfig.parse(config, d) for d in config["options"].keys()])

    def __iter__(self):
        return iter(self.deviceconfs)


class DeviceConfig(object):
    def __init__(self, name, device, robotsurl, options, nodes):
        self.name = name
        self.device = device
        self._robots = RobotsConfig(robotsurl)
        self.options = options
        self.nodes = nodes

    @classmethod
    def parse(cls, config, device):
        nodes = [Node.parse(n, device) for n in config["nodes"]]
        options = BrowserOptions.parse(config["options"], device)
        return cls(config["name"], device, config["robots"][device], options, nodes)
        
    def check_robots_txt(self, nodes):
        self._robots.load()
        for n in nodes:
            if not self._robots.can_fetch(n.url, self.options.useragent):
                raise RuntimeError("許可されていません")


class BrowserOptions(object):
    def __init__(self, useragent, viewport):
        self.useragent = useragent
        self.viewport = viewport

    @classmethod
    def parse(cls, config, device):
        c = config[device]
        return cls(c.get("useragent", None), c.get("viewport", None))


class Node(object):
    def __init__(self, name, url, childs):
        self.name = name
        self.url = url
        self.childs = childs

    @classmethod
    def parse(cls, conf, device):
        childs = [ChildNode.parse(x, device) for x in conf.get("childs", [])]
        return cls(conf["name"], conf["url"][device], childs)


class ChildNode(object):
    def __init__(self, name, url_regexp, childs):
        self.name = name
        self._url_regexp = re.compile(url_regexp)
        self._childs = childs

    @classmethod
    def parse(cls, conf, device):
        childs = [ChildNode.parse(x, device) for x in conf.get("childs", [])]
        return cls(conf["name"], conf["url_regexp"][device], childs)

    def parse_child_node(self, urls):
        """候補となるURLからノードを作る
        """
        for url in urls:
            if self._url_regexp.match(url):
                return Node(self.name, url, self._childs)
        raise ValueError(f"Url Not Found.: {urls}")


class RobotsConfig(object):
    def __init__(self, robotsurl):
        self._parser = RobotFileParser()
        self._parser.set_url(robotsurl)
        self._loaded = False

    def load(self):
        if self._loaded:
            return
        self._parser.read()
        self._loaded = True

    def can_fetch(self, useragent, url):
        return self._parser.can_fetch(useragent, url)