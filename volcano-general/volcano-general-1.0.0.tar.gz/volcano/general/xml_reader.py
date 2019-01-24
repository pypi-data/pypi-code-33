#!/usr/bin/python3

# Line numbering
# https://stackoverflow.com/questions/6949395/is-there-a-way-to-get-a-line-number-from-an-elementtree-element

# Force python XML parser not faster C accelerators
# because we can't hook the C implementationimport sys
import sys
import os.path

sys.modules['_elementtree'] = None
import xml.etree.ElementTree as ET  # pylint: disable=wrong-import-position;     # noqa: E402


class LineNumberingParser(ET.XMLParser):
    def __init__(self, file_name):
        super().__init__()
        self.file_name_ = os.path.basename(os.path.normpath(file_name))

    def _start(self, tag, attr_list):
        element = super()._start(tag, attr_list)

        element.line_number = self.parser.CurrentLineNumber
        element.file_name = self.file_name_

        return element


def get_node_location(node):
    if hasattr(node, 'line_number'):
        assert hasattr(node, 'file_name')
        return '{}|L{}|<{}>'.format(node.file_name, node.line_number, node.tag)
    else:
        return node.tag


def load_xml_file_le(file_name: str):
    try:
        rs = ET.parse(file_name, parser=LineNumberingParser(file_name))
        return rs
    except Exception as e:
        raise LoadException(e)


class LoadException(Exception):
    def __init__(self, msg_or_exc, node=None):
        if node is not None:  # using 'if node' is not recommended - the behaviour will change
            super().__init__('{}: {}'.format(get_node_location(node), msg_or_exc))
        else:
            super().__init__(msg_or_exc)


class XmlReader:
    def __init__(self, xml_node):
        self.node_ = xml_node

    def location(self):
        return self.node_.tag

    def assert_node_name(self, names: (str, tuple, list)) -> None:
        assert isinstance(names, (str, tuple, list)), names

        if self.node_.tag not in ((names,) if isinstance(names, str) else names):   # pylint: disable=superfluous-parens
            raise LoadException('Unknown node name {}. Available: {}'.format(self.node_.tag, names), self.node_)

    def get_str(self, name, default=None, allowed=None) -> str:
        v = self.node_.attrib.get(name, None)
        if v is None:
            if default is None:
                raise LoadException('Attribute "{}" is missing'.format(name), self.node_)
            return default

        if allowed and v not in allowed:
            raise LoadException('Attribute "{}={}" is invalid. Allowed values: {}'.format(name, v, allowed), self.node_)

        return v

    def get_bool(self, name, default=None):
        s = self.node_.attrib.get(name, None)
        if s is None:
            if default is None:
                raise LoadException('Attribute "{}" is missing'.format(name), self.node_)
            return default

        if s == '0':
            return False
        elif s == '1':
            return True
        else:
            raise LoadException('Attribute "{}={}" is not a valid bool. Use "0" and "1"'.format(name, s), self.node_)

    def get_int(self, name, default=None, min_val=None, max_val=None):
        v = self.node_.attrib.get(name, None)
        if v is None:
            if default is None:
                raise LoadException('Attribute "{}" is missing'.format(name), self.node_)
            return default
        try:
            iv = int(v)

            if min_val is not None and iv < min_val:
                raise LoadException('Attribute "{}={}" is less than {}'.format(name, v, min_val), self.node_)

            if max_val is not None and iv > max_val:
                raise LoadException('Attribute "{}={}" is greater than {}'.format(name, v, max_val), self.node_)

            return iv
        except Exception as e:
            raise LoadException('Attribute "{}={}" is not a valid int: {}'.format(name, v, e), self.node_)

    def get_dic(self, name, dic, default_value=None):
        v = self.node_.attrib.get(name, None)
        if v is None:
            if default_value is None:
                raise LoadException('Attribute "{}" is missing'.format(name), self.node_)
            return default_value

        rs = dic.get(v, None)
        if rs is None:
            raise LoadException('Attribute "{}={}" is invalid. Available values: {}'.format(name, v, dic.keys()), self.node_)

        return rs

    def get_time_secs(self, name, default=None, min_val=None, max_val=None):
        s = self.node_.attrib.get(name, None)
        if s is None:
            if default is None:
                raise LoadException('Attribute "{}" is missing'.format(name), self.node_)
            return default

        val_secs = None
        try:
            if s.endswith('ms'):
                val_secs = int(s[:-2]) / 1000.0
            elif s.endswith('s'):
                val_secs = float(s[:-1])
            else:
                raise LoadException(
                    'Attribute "{}={}" is invalid. Value should be in a form "123.45s" or "12345ms" where s=seconds, ms=milliseconds.'.format(
                        name, s), self.node_)
        except ValueError as e:
            raise LoadException('Attribute "{}={}" is not a valid time: {}'.format(name, s, e), self.node_)

        if min_val is not None and val_secs < min_val:
            raise LoadException('Attribute "{}={}" is less than {}'.format(name, val_secs, min_val), self.node_)

        if max_val is not None and val_secs > max_val:
            raise LoadException('Attribute "{}={}" is greater than {}'.format(name, val_secs, max_val), self.node_)

        return val_secs
