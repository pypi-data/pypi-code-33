import lxml.html
from contextlib import suppress


def xpath_get(node, xpath):
    with suppress(RuntimeError):
        return lxml.html.fromstring(node).xpath(xpath)[0].text
    return ''


def xpath_filter(node, xpath):
    with suppress(RuntimeError):
        return [w.text for w in lxml.html.fromstring(node).xpath(xpath)]
    return []
