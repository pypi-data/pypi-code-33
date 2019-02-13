from tagliatelle.data.TagRequest import TagRequest


class TagResponse(TagRequest):

    def __init__(self, key, value, resource_uri, id, created_at, created_by, modified_at, modified_by, links):
        TagRequest.__init__(self, key, value, resource_uri)
        self.id = id
        self.createdAt = created_at
        self.createdBy = created_by
        self.modifiedAt = modified_at
        self.modifiedBy = modified_by
        self._links = links