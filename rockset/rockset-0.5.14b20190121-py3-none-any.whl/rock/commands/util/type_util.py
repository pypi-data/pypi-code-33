class TypeUtil:
    TYPE_COLLECTION="COLLECTION"
    TYPE_INTEGRATION="INTEGRATION"

    """
    returns resource type from upstream resource
    """
    @staticmethod
    def parse_resource_type(type):
        if type in ['col', 'collection', 'collections']:
            return TypeUtil.TYPE_COLLECTION
        elif type in ['int', 'integration', 'integrations']:
            return TypeUtil.TYPE_INTEGRATION
        else:
            return None