from python_openapi3._util import ensure_allowed, ensure_class, OASBase, DEFAULT_IGNORE, TypedMapFactory
from python_openapi3.openapi_specification.oas_definitions import path_kwargs
from python_openapi3.openapi_specification.oas_parameters import OASParameterObject, OASReferenceObject
from python_openapi3.openapi_specification.oas_response import OASResponseObject


class OASOperationObject(OASBase):
    """
    Represents an OAS3 [Operation Object](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#operationObject), or endpoint action


    """
    def __init__(self,responses,description=DEFAULT_IGNORE,
                 summary=DEFAULT_IGNORE, tags=DEFAULT_IGNORE,
                 externalDocs=DEFAULT_IGNORE, operationId=DEFAULT_IGNORE,
                 parameters=DEFAULT_IGNORE, requestBody=DEFAULT_IGNORE,
                 callbacks=DEFAULT_IGNORE, deprecated=DEFAULT_IGNORE,
                 security=DEFAULT_IGNORE, servers=DEFAULT_IGNORE
):
        """

        :param tags:
        :param summary:
        :param description:
        :param externalDocs:
        :param operationId:
        :param parameters:
        :param requestBody:
        :param responses:
        :param callbacks:
        :param deprecated:
        :param security:
        :param servers:
        """
        if parameters is not DEFAULT_IGNORE:
            parameters = [ensure_class(p,OASParameterObject) for p in parameters]
        responses = TypedMapFactory(OASResponseObject)(responses)
        self._data = {}
        self.update(locals())



class OASPathItemObject(OASBase):
    """
    Represents OAS3.0 [PathItem Object](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#pathItemObject)
    """

    @staticmethod
    def ensure_parameter(p):
        return
    @staticmethod
    def ensure_operation(p):
        return ensure_class(p,OASOperationObject)
    def __init__(self,**kwargs):
        """

        :param $ref: a reference to a schema item
        :param ref: alias for $ref
        :param summary: a summary object
        :param description: a description
        :param get:
        :param put:
        :param post:
        :param delete:
        :param options:
        :param head:
        :param patch:
        :param trace:
        :param servers:
        :param parameters:
        """
        ensure_allowed(kwargs,path_kwargs)
        if 'ref' in kwargs:
            if '$ref' not in kwargs:
                kwargs['$ref'] = kwargs.pop('ref')
            else:
                raise TypeError("You can supply ref or $ref but not both!")

            OASReferenceObject.pending_refs.append(kwargs['$ref'])
        else:
            if 'parameters' in kwargs:
                kwargs['parameters'] = [ensure_class(val, OASParameterObject) for val in kwargs['parameters']]
            for method in ['get','put','post','patch','delete','options','head']:
                if method in kwargs:
                    kwargs[method] = ensure_class(kwargs[method],OASOperationObject)

        self._data = {}
        self._data.update(kwargs)

