class Utils:
    @staticmethod
    def mount_flask_uri(method):
        method_uri = method['path']
        if method["queryParams"] and len(method["queryParams"]) > 0:
            for param in method['queryParams']:
                method_uri = method_uri + '/<' + param['type'] + ':' + param['name'] + '>'
        return method_uri

    @staticmethod
    def mount_openapi_uri(method):
        method_uri = method['path']
        if method['queryParams'] is not None:
            for queryParam in method['queryParams']:
                method_uri = method_uri + "/{" + queryParam['name'] + "}"
        return method_uri
