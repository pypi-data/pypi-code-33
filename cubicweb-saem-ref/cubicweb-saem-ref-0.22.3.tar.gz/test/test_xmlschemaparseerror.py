from os import path
from lxml import etree


def test_xmlschemaparseerror():
    fpath = path.join(path.dirname(__file__), 'data', 'cpf.xsd')
    etree.XMLSchema(file=fpath)
