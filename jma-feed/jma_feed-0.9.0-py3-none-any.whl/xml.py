import urllib.error
import urllib.request
import xml.etree.ElementTree as ET


class XmlDocument:
    """Model class which represents XML document / element."""

    def __init__(self, target, ns_map):
        """Initialize class.

        Args:
            target (ElementTree.Element or str): XML element or URL
        """

        self.ns_map = ns_map

        if isinstance(target, ET.Element):
            self.root = target
        elif isinstance(target, str):
            try:
                self.root = ET.fromstring(target)
            except ET.ParseError:
                try:
                    xml_text = urllib.request.urlopen(target).read()
                    self.root = ET.fromstring(xml_text)
                except (urllib.error.URLError, urllib.error.HTTPError):
                    raise ValueError('target string must be valid URL or XML string.')
        else:
            raise ValueError('target parameter can take only Element or URL or XML string.')

    def _find_element(self, *xpaths):
        for xpath in xpaths:
            element = self.root.find(xpath, self.ns_map)
            if element is not None:
                return xpath, element
        return (None, None)

    def _find_elements(self, *xpaths):
        for xpath in xpaths:
            elements = self.root.findall(xpath, self.ns_map)
            if elements:
                return xpath, elements
        return (None, None)

    def _element(self, xpath):
        return self.root.find(xpath, self.ns_map)

    def _elements(self, xpath):
        return self.root.findall(xpath, self.ns_map)

    def _element_text(self, xpath):
        element = self._element(xpath)
        if element == None:
            return None
        return element.text

    def _element_attr(self, xpath, attr_name):
        element = self._element(xpath)
        if element == None:
            return None
        return element.get(attr_name)
