#############################################################################
# Various allowed KWARGS and Values, as defined by OAS3.0 Specification    ##
# https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md
##############################################################################

schema_kwargs = [ # kwargs allowed for the [Schema Object](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#schemaObject)
    'title','multipleOf','maximum','minimum','exclusiveMaximum','exclusiveMinimum','maxLength','minLength',
    'pattern','maxItems','minItems','uniqueItems', 'maxProperties','minProperties','required','enum',
    'type','allOf','oneOf','anyOf','not','items','properties','additionalProperties','description',
    'format','default','nullable','discriminator','readOnly','writeOnly','xml','externalDocs','example',
    'depreciated'
]

path_kwargs = [ # kwargs allowed for the [PathItem Object](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#pathItemObject)
    '$ref','ref','summary','description','get','put','post','delete','options','head','patch',
    'trace','servers','parameters'
]

operation_kwargs = [ # kwargs allowed for the [Operation Object](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#operationObject)
    # this is basically the endpoint definition
    'tags','summary','description','externalDocs','operationId','parameters',
    'requestBody', 'responses', 'callbacks', 'deprecated','security','servers'
]
#: kwargs allowed for the [SecurityScheme Object](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#securitySchemeObject)
security_kwargs = ['type','description','name','in','scheme','bearerFormat','flows','openIdConnectUrl']
parameter_kwargs = [ # kwargs for the the [Parameter Object](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#parameterObject)
    'name','in','description','required','deprecated','allowEmptyValue',
    'style','explode','allowReserved','schema','example','examples','content',
]
#: kwargs for the MediaType Object
mediaType_kwargs = ['schema', 'example', 'examples', 'encoding']
#: kwargs for the Components Object
componentsObject_kwargs = ['schemas', 'responses', 'parameters', 'examples', 'requestBodies',
                           'headers', 'securitySchemes', 'links', 'callbacks']
#: header kwargs are most of the parameters allowed for parameter, but `in` is guaranteed to be 'header'
header_kwargs = parameter_kwargs[2:] # and the name is described by this variables key
style_values = [ # values allowed for the schema objects, `style` property
    'matrix','label','form','simple','spaceDelimited','pipeDelimited','deepObject'
]
allowed_aos_base_types = ['string','number','integer','object','array']
#: values allowed for the SecurityScheme `type` property
security_type_values = ['apiKey','http','oauth2','openIdConnect']

