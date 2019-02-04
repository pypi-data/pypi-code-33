from src.py_oas3 import OASBase


class OASComponentsGroup(OASBase):
    def __init__(self,schemas=None,responses=None,parameters=None,examples=None,requestBodies=None,headers=None,securitySchemas=None,links=None,callbacks=None):
        self._data = {}
        if schemas:
            self._data['schemas'] = schemas
        if responses:
            self._data['responses'] = responses
        if parameters:
            self._data['parameters'] = parameters
        if examples:
            self._data['examples'] = examples
        if requestBodies:
            self._data['requestBodies'] = requestBodies
        if headers:
            self._data['securitySchemas'] = securitySchemas
        if securitySchemas:
            self._data['securitySchemas'] = securitySchemas
        if links:
            self._data['links'] = links
        if callbacks:
            self._data['callbacks'] = callbacks



if __name__ == "__main__":
    md = OASMetaData("asd","2.1","asdqweqw e")
    md2 = OASMetaData(**md.to_dict())
    print(md is md2,md == md2)