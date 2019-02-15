from onepanel.models.api_json import APIJSON

class DatasetMountIdentifier(APIJSON):
    def __init__(self, account_uid=None, dataset_uid=None, version=None, destination=None):
        self.account_uid = account_uid
        self.dataset_uid = dataset_uid
        self.set_version(version)
        self.destination = destination

    def set_source(self, source):
        """Source is expected to be account_uid/dataset_uid"""
        source_parts = source.split('/')
        self.account_uid = source_parts[0]
        self.dataset_uid = source_parts[1]

    @classmethod
    def from_simple_json(cls, dct):
        identifier = cls()

        identifier.set_source(dct['source'])
        identifier.set_version(dct['version'])
        identifier.destination = dct['destination']

        return identifier

    def set_version(self, version):
        if version is None:
            self.version = None
            return
            
        self.version = int(version)

    def api_json(self):
        return {
            'accountUID': self.account_uid,
            'datasetUID': self.dataset_uid,
            'datasetVersion': self.version,
            'alias': self.destination
        }