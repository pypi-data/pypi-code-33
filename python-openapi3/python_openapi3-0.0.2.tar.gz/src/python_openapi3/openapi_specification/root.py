from python_openapi3._util import ensure_class, OASBase, TypedMapFactory, TypedListFactory

from python_openapi3.openapi_specification.info_section import OASInfoObject
from python_openapi3.openapi_specification.oas_server import OASExternalDocumentationObject, OASServerObject
from python_openapi3.openapi_specification.paths_sections import OASPathItemObject


class OASTagDefinitionObject(OASBase):
    def __init__(self,name,description=None,externalDocs=None):
        self._data = {'name':name}
        if description:
            self._data['description'] = description
        if externalDocs:
            self._data['externalDocs'] = ensure_class(externalDocs,OASExternalDocumentationObject)

class OAS3Specification(OASBase):
    def __init__(self,info,paths,servers=None,components=None,security=None,tags=None,externalDocs=None):
        data = {
            "openapi": "3.0.0",
            "info": ensure_class(info,OASInfoObject),
            "paths": TypedMapFactory(OASPathItemObject)(paths)
        }
        if tags:
            data['tags'] = TypedListFactory(OASTagDefinitionObject)(tags)
        if servers:
            data['servers'] = [ensure_class(server,OASServerObject) for server in servers]
        if components:
            data['components'] = ensure_class(components,)
        if self.security:
            data['security'] = self.security.to_dict()
        if self.externalDocs:
            data['externalDocs'] = self.externalDocs.toDict()
        self._data = data

    def validate(self):
        errors = None
        return errors