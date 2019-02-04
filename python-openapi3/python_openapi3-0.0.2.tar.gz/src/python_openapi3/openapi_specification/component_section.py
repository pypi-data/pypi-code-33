from python_openapi3._util import  ensure_class, OASBase, DEFAULT_IGNORE
from python_openapi3.openapi_specification.oas_parameters import OASSchemaObject, OASParameterObject
from python_openapi3.openapi_specification.oas_response import OASResponseObject, OASRequestBodyObject, OASHeaderObject


class OASComponentsSection(OASBase):
    def __init__(self,schemas=DEFAULT_IGNORE, responses=DEFAULT_IGNORE, parameters=DEFAULT_IGNORE,
                 examples=DEFAULT_IGNORE, requestBodies=DEFAULT_IGNORE, headers=DEFAULT_IGNORE,
                 securitySchemes=DEFAULT_IGNORE, links=DEFAULT_IGNORE, callbacks=DEFAULT_IGNORE):
        """
        >>> OASComponentsSection(schemas="ASD")
        :param schemas:
        :param responses:
        :param parameters:
        :param examples:
        :param requestBodies:
        :param headers:
        :param securitySchemes:
        :param links:
        :param callbacks:
        """
        self._data = {}
        q = {k:v for k,v in locals().items() if k not in ('self','cls')}
        self.update(q)
        if schemas:
            self._data['schemas'] = {k:ensure_class(v,OASSchemaObject) for k, v in schemas.items()}
        if responses:
            self._data['responses'] = {k:ensure_class(v,OASResponseObject) for k, v in responses.items()}
        if parameters:
            self._data['parameters'] = {k:ensure_class(v,OASParameterObject) for k, v in parameters.items()}
        if examples:
            self._data['examples'] = {k:ensure_class(v,OASExampleObject) for k, v in examples.items()}
        if requestBodies:
            self._data['requestBodies'] = {k:ensure_class(v,OASRequestBodyObject) for k, v in requestBodies.items()}
        if headers:
            self._data['headers'] = {k: ensure_class(v, OASHeaderObject) for k, v in headers.items()}
        if securitySchemes:
            self._data['securitySchemes'] = {k:ensure_class(v,) for k, v in securitySchemes.items()}