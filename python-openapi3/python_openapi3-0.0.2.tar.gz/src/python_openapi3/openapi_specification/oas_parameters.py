from python_openapi3._util import ensure_allowed, OASBase, ensure_class,\
    TypedMapFactory, TypedListFactory, DEFAULT_IGNORE,  guess_example_from_schema
from python_openapi3.openapi_specification.oas_definitions import parameter_kwargs, \
    schema_kwargs, style_values, allowed_aos_base_types


class OASReferenceObject(OASBase):
    pending_refs = []
    @classmethod
    def preprocess_kwargs(cls,kwargs):
        kwargs['ref'] = kwargs.pop('$ref',kwargs.pop('ref',None))
        if not kwargs['ref']:
            return {}
        return kwargs
    def __init__(self,ref):
        self.update({'$ref':ref})
        self.pending_refs.append(ref)

class OASSchemaObject(OASBase):
    """
    represents an OAS3.0 [SchemaObject](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#schemaObject)

    allowed_params:
        'title','multipleOf','maximum','minimum','exclusiveMaximum','exclusiveMinimum','maxLength','minLength',
        'pattern','maxItems','minItems','uniqueItems', 'maxProperties','minProperties','required','enum',
        'type','allOf','oneOf','anyOf','not','items','properties','additionalProperties','description',
        'format','default','nullable','discriminator','readOnly','writeOnly','xml','externalDocs','example',
        'depreciated'

    >>> sorted(OASSchemaObject('example1').to_dict().items())
    [('title', 'example1')]
    >>> sorted(OASSchemaObject('example1',type="integer",minimum=4,maximum=10).to_dict().items())
    [('maximum', 10), ('minimum', 4), ('title', 'example1'), ('type', 'integer')]
    >>> sorted(OASSchemaObject('example1',type="string",enum=["asd","qqq","eee"],default="asd").to_dict().items())
    [('default', 'asd'), ('enum', ['asd', 'qqq', 'eee']), ('title', 'example1'), ('type', 'string')]

    """
    def __init__(self,_type,description=DEFAULT_IGNORE, **kwargs):
        """
         allowed_params:
            'title','multipleOf','maximum','minimum','exclusiveMaximum','exclusiveMinimum','maxLength','minLength',
            'pattern','maxItems','minItems','uniqueItems', 'maxProperties','minProperties','required','enum',
            'type','allOf','oneOf','anyOf','not','items','properties','additionalProperties','description',
            'format','default','nullable','discriminator','readOnly','writeOnly','xml','externalDocs','example',
            'depreciated'

        :param title:
        :param multipleOf:
        :param maximum:
        :param minimum:
        :param exclusiveMaximum:
        :param exclusiveMinimum:
        :param maxLength:
        :param minLength:
        :param pattern:
        :param maxItems:
        :param minItems:
        :param uniqueItems:
        :param maxProperties:
        :param minProperties:
        :param required:
        :param enum:
        :param type:
        :param allOf:
        :param oneOf:
        :param anyOf:
        :param items:
        :param properties:
        :param additionalProperties:
        :param description:
        :param format:
        :param default:
        :param nullable:
        :param discriminator:
        :param readOnly:
        :param writeOnly:
        :param xml:
        :param externalDocs:
        :param example:
        :param depreciated:
        """
        ensure_allowed(kwargs,schema_kwargs)
        self.update(kwargs)
        d = {'type':_type}
        ensure_allowed(dict.fromkeys(d.values(),1),allowed_aos_base_types,
                       "Unknown Base OAS Type ERROR: {violating_keys} EXPECTED ONE OF {allowed_values}")
        if description is not DEFAULT_IGNORE:
            d['description'] = description
        self.update(d)

        _type = self._data.get('type','')
        if _type.lower() == "object":
            if not self._data.get('properties', None):
                print("Warning: Type object, without properties attribute!")
                # raise TypeError("Cannot assign `object` type to schema, without a `properties` as well")
            self._data['properties'] = TypedMapFactory(OASSchemaObject)(self._data.get('properties',{}))
        if _type.lower() == "array":
            if not self._data.get('items', None):
                raise TypeError("Cannot assign `array` type to schema, without an `items` key as well")
            self._data['items'] = TypedListFactory(OASSchemaObject)(self._data['items'])
        self.update({"example":guess_example_from_schema(self._data)})

    @classmethod
    def preprocess_kwargs(cls,kwargs):

        _type = kwargs.pop('type',kwargs.pop('_type',None))
        if _type:
            kwargs['_type'] = _type
        return kwargs
class OASParameterObject(OASBase):
    """
    represents an OAS3.0 [Parameter Object](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#parameterObject)

    allowed_params:
    	name, in, description, required, deprecated, allowEmptyValue, style,
    	explode, allowReserved, schema, example, examples, content
    """
    def __init__(self,name,_in,_type=None,description=None,deprecated=False,required=True,**kwargs):
        if _type:
            kwargs.setdefault('schema',{})['type'] = _type

        for key,val in list(kwargs.items()):
            if key not in parameter_kwargs and key in schema_kwargs:
                kwargs.setdefault('schema',{})[key] = kwargs.pop(key)

        ensure_allowed(kwargs, parameter_kwargs)
        if 'schema' in kwargs:
            kwargs['schema'] = ensure_class(kwargs['schema'],OASSchemaObject)
        self.update({
            'description': description,
            'name': name,
            'deprecated': deprecated,
            'required': required,
            'in': _in
        })
        self.update(kwargs)
        if self._data.get('style',None):
            err_msg = "Unknown Style: {violating_keys} expected one of {allowed_values}"
            ensure_allowed({self._data['style']:1},style_values,err_msg)