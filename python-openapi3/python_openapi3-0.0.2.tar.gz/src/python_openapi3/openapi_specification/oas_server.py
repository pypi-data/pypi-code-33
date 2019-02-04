import urllib

from python_openapi3._util import ensure_class, OASBase, TypedMapFactory
from python_openapi3.logger import log
from python_openapi3.pycompat23_local import urlopen


class OASExternalDocumentationObject(OASBase):
    def __init__(self,url,description=None):
        self._data = {'url':url}
        if description:
            self._data['description'] = description
    def validate(self):
        try:
            code = urlopen(self._data.get('url',''))
        except:
            log.exception("Unable to connect to {url}".format(url=self._data['url']))
            return False
        else:
            if code >= 400:
                return False
            return True

class OASServerVariableObject(OASBase):
    def __init__(self, default, description=None, enum=None):
        """
        >>> sorted(OASServerVariableObject("5","some desc",["1","2","4","5"]).to_dict().items())
        [('default', '5'), ('description', 'some desc'), ('enum', ['1', '2', '4', '5'])]

        :param default: the default value for this variable **REQUIRED
        :param description: An optional description for the server variable. CommonMark syntax MAY be used for rich text representation.
        :param enum: An (optional) enumeration of string values to be used if the substitution options are from a limited set.
        """
        self._data = {'default':default}
        if description:
            self._data['description'] = description
        if enum:
            self._data['enum'] = enum

class OASServerObject(OASBase):
    def __init__(self,url,description=None,variables=None):
        """
        >>> srv = OASServerObject("a","b",{"b":"d","e":{"default":"f","description":"g"}})
        >>> sorted(srv.to_dict().items())
        [('description', 'b'), ('url', 'a'), ('variables', {'b': {'default': 'd'}, 'e': {'default': 'f', 'description': 'g'}})]
        >>> srv['variables']['b'] # doctest:+ELLIPSIS
        <component_section.OASServerVariableObject object at 0x...>


        :param url: the url of this server
        :param description: a string description of this server
        :param variables:
        :type variables: Dict[str,OASServerVariableObject]
        """
        self._data = {'url':url}
        if description:
            self._data['description'] = description
        if variables:
            self._data['variables'] = TypedMapFactory(OASServerVariableObject)(variables)
