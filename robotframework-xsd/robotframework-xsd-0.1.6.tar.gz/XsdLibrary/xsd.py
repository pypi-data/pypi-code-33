# -*- coding: utf-8 -*-
import os
import xmlschema
import validators
from xmlschema.exceptions import XMLSchemaException
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


class XsdKeywords(object):
    """
    XsdLibrary is a XSD keyword library that uses to validate XML
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        pass

    @staticmethod
    def xml_should_match_xsd(xml, xsd, msg=None):
        """ Validate if the `xml` match the `xsd`

        ``xml`` can be xml file path, URL path or a string containing the XML data.

        ``xsd`` can be xsd file path, URL path or a string containing the XML Schemas Definition.

        ``msg`` if set, it will override the default error message when match failed.

        Examples:
        | Xml Should Match Xsd | <a>test</a> | http://www.domain.com/xxx/yyy/zzz.xsd |
        | Xml Should Match Xsd | http://www.domain.com/xxx/yyy/zzz.xml | /home/some_user/path_to_file.xsd |
        | Xml Should Match Xsd | /home/some_user/path_to_file.xml | <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">...</xs:schema> |
        """
        try:
            if validators.url(xsd) is True or os.path.exists(xsd):
                _schema = xmlschema.XMLSchema(xsd)
            else:
                ET.fromstring(xsd)
                _schema = xmlschema.XMLSchema("""{0}""".format(xsd,))
        except:
            raise XMLSchemaException("the xsd parameter is invalid")
        try:
            if validators.url(xml) is True or os.path.exists(xml):
                # validate、is_valid方法对URI形式的xml兼容有问题（应该是bug），因此需要load_xml_resource预处理
                _schema.validate(xmlschema.load_xml_resource(xml))
            else:
                _schema.validate("""{0}""".format(xml,))
        except:
            if msg:
                raise Exception(msg)
            else:
                raise
