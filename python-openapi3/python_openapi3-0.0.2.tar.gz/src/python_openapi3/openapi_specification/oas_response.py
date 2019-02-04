from python_openapi3._util import ensure_class, ensure_allowed, OASBase, TypedMapFactory, UnionTypeFactory, DEFAULT_IGNORE
from python_openapi3.openapi_specification.oas_definitions import header_kwargs, mediaType_kwargs, security_kwargs, style_values
from python_openapi3.openapi_specification.oas_parameters import OASSchemaObject, OASReferenceObject
from python_openapi3.openapi_specification.oas_server import OASServerObject
from python_openapi3.pycompat23_local import basestr


class OASExampleObject(OASBase):
    """
    Represents an OAS3.0 [External Object]()
    """
    @classmethod
    def preprocess_args_kwargs(cls,args,kwargs):
        if 'externalValue' in kwargs:
            if args:
                raise TypeError("Too many 'value' provided for ExternalObject")
            args = (kwargs.pop('externalValue'),)
            kwargs['is_external'] = True
        if 'value' in kwargs:
            if args:
                raise TypeError("Too many 'value' provided for ExternalObject")
            args = (kwargs.pop('value'),)
            kwargs['is_external'] = False
        return args,kwargs

    def __init__(self, value_or_externalValue, summary=DEFAULT_IGNORE, description=DEFAULT_IGNORE, is_external=None,is_ref=False):
        if not isinstance(value_or_externalValue,basestr):
            raise TypeError("OASExampleObject only supports string type for the value... this represents objects not normally serializeable")

        data = {'summary':summary,'description':description}
        if is_external is None:
            if value_or_externalValue[:6] in ["http:/", "https:"]:
                is_external = True
        if is_external:
            data['externalValue'] = value_or_externalValue
        else:
            data['value'] = value_or_externalValue
        self.update(data)

class OASEncodingObject(OASBase):
    def __init__(self,contentType=DEFAULT_IGNORE,headers=DEFAULT_IGNORE,style=DEFAULT_IGNORE,explode=DEFAULT_IGNORE,allowReserved=DEFAULT_IGNORE):
        """
        Represents OAS3.0 [Encoding Object]()

        :param contentType: "application/json" or "application/octet-stream" or "text/plain", etc
        :param headers: a map of headers, that will be returned with this encoding
        :param style: defines how this specific encoding will be serialized
        :param explode: should arrays/objects generate seperate params for each entry?
        :param allowReserved: allow reserved characters
        """
        self.update(locals())
        if not self._data:
            print("Warning ... no values found for encoding")
        updates = {}
        if self._data.get('headers',None):
            updates['headers'] = TypedMapFactory(OASHeaderObject)(self._data['headers'])
        if self._data.get('style',None) is not None:
            ensure_allowed({self._data['style']:1},style_values)

        self.update(updates)
class OASSecuritySchemeObject(OASBase):
    @staticmethod
    def preprocess_args_kwargs(args,kwargs):
        if len(args) < 2:
            kwargs["_in"] = kwargs.pop("in",kwargs.get("_in",None))

        if len(args) < 3:
            kwargs["_type"] = kwargs.pop("type",kwargs.get("_type",None))
        return args,kwargs

    def __init__(self,name,_in,_type,description=DEFAULT_IGNORE,**kwargs):
        ensure_allowed(kwargs, security_kwargs)
        self.update({
            'name': name,
            'in': _in,
            'type': _type,
            'description':description
                      })
        self.update(kwargs)



class OASMediaTypeObject(OASBase):
    """
    represents OAS3.0 [MediaType Object](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#mediaTypeObject
    """
    def __init__(self, schema=DEFAULT_IGNORE, example=DEFAULT_IGNORE, examples=DEFAULT_IGNORE, encoding=DEFAULT_IGNORE):
        """

        :param schema:
        :param example: an example of this media type, it should be in the correct format
        :param examples:
        :param encoding:
        """
        self.update(locals())
        if self._data.get('examples'):
            self._data['examples'] = TypedMapFactory(UnionTypeFactory(OASExampleObject,OASReferenceObject,str))(examples)
        if self._data.get('encoding'):
            self._data['encoding'] = ensure_class(encoding,OASEncodingObject)

class OASHeaderObject(OASBase):
    """
    represents OAS3.0 [Header Object](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#headerObject)

    """
    def __init__(self, description="", deprecated=False, required=True, _type=None, **kwargs):
        ensure_allowed(kwargs, header_kwargs)
        self._data = {}
        self._data.update(kwargs)
        if description:
            self._data['description'] = description
        if deprecated:
            self._data['deprecated'] = True
        if required:
            self._data['required'] = True
        if _type:
            self._data.setdefault('schema', {})['type'] = type


class OASLinkObject(OASBase):
    def __init__(self, operationRef=None, operationId=None, parameters=None, requestBody=None, description=None,
                 server=None):
        """
        represents OAS3.0 [Link Object](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#link-object)

        must include one of operationRef, or operationId

        :param operationRef: a relative or absolute reference to an OAS operation(exclusive to operationID)
        :param operationId: an *existing*, resolveable OAS operation (exclusive to operationRef)
        :param parameters: a dict of key,value maping to pass to the specified operation
        :type parameters: Dict[str,str]
        :param requestBody: a literal string or {expression} to use as the request body
        :param description: a description of this link
        :param server: a server object to be used by the target operation
        """
        if operationRef and operationId:
            raise TypeError("You MUST not include BOTH operationRef and operationId! only one of the TWI")
        if not operationRef and not operationId:
            raise TypeError("You MUST include EITHER operationRef OR operationId!(...but not both!)")
        self._data = {}
        if operationRef:
            self._data['operationRef'] = operationRef
        if operationId:
            self._data['operationId'] = operationId
        if parameters:
            self._data['parameters'] = parameters
        if requestBody:
            self._data['requestBody'] = requestBody
        if description:
            self._data['description'] = description
        if server:
            self._data['server'] = ensure_class(server, OASServerObject)


class OASRequestBodyObject(OASBase):
    """
    https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#requestBodyObject
    Request Body Object
    
    Describes a single request body.
    """

    def __init__(self, content, description=None, required=False):
        self._data = {}
        self._data['content'] = TypedMapFactory(OASMediaTypeObject)(content)
        if description:
            self._data['description'] = description
        if required:
            self._data['required'] = True


class OASResponseObject(OASBase):
    def __init__(self, description, content=None, headers=None, links=None):
        links = links or {}
        headers = headers or {}

        if not isinstance(content, dict) or set(content.keys()).intersection(mediaType_kwargs):
            content = {"*": ensure_class(content, OASMediaTypeObject)}
        elif isinstance(content, dict):
            for key in content:
                content[key] = ensure_class(content[key], OASMediaTypeObject)
        self._data = {
            'description': description,
            'links': {key: ensure_class(lnk, OASLinkObject) for key, lnk in links.items()},
            'content': content,
            'headers': {key: ensure_class(hdr, OASHeaderObject) for key, hdr in headers.items()},
        }
