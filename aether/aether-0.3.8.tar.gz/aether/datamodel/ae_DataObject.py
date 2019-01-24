import abc

from aether.datamodel.ae_DataModel import ae_DataModel
from aether.session.GlobalConfig import GlobalConfig


##############################################################################################################
#
# DataModel objects have their ID generated upon instantiation, when saved for the first time. This helps
# reduce the namespace of IDs used.
#
#
##############################################################################################################

# Either let Firestore create a new id. Or, if one is present, we are either
# creating a new application with a pre-defined ID, or updating an existing application ID
# with new parameters, both of which follow the same syntax.

class ae_DataObject(object):

    def __init__(self, collection):
        self._collection = collection
        self._id = None
        self._datamodel = ae_DataModel(GlobalConfig._getInstance().aether_client())

    def save(self):
        r = self._datamodel.save(self._collection, self._id, self._to_dm_dict())
        if r is None:
            return None
        self._id = r["id"]
        return r["id"]

    def load(self, id):
        r = self._datamodel.load(self._collection, id)
        if r is None:
            return None
        self._id = id
        return self._from_dm_dict(r["datamodel"])

    @abc.abstractmethod
    def _to_dm_dict(self):
        pass

    @abc.abstractmethod
    def _from_dm_dict(self, dm):
        pass

