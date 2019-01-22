
##############################################################################################################
#
# DataModel objects have their ID generated upon instantiation, when saved for the first time. This helps
# reduce the namespace of IDs used.
#
##############################################################################################################
import json

class ae_DataModel(object):

    _canonical_name = None
    _http_transmission_header = None

    def __init__(self, client):
        self._aether_client = client

    def save(self, collection, id, dm):
        parameters = dict(collection=collection, method="save", datamodel=json.dumps(dm))
        if id is not None:
            parameters["id"] = id
        response = self._aether_client.call_uri("DataModelData", {}, parameters, JsonAsString())
        response = json.loads(response.json_string)
        return response

    def load(self, collection, id):
        parameters = dict(collection=collection, method="load", id=id)
        response = self._aether_client.call_uri("DataModelData", {}, parameters, JsonAsString())
        response = json.loads(response.json_string)
        return response
