
import centreonapi.webservice.configuration.common as common


class ContactGroup(common.CentreonObject):

    def __init__(self, properties):
        self.id = properties.get('id')
        self.name = properties.get('name')


class Contact(common.CentreonObject):

    def __init__(self, properties):
        self.id = properties.get('id')
        self.name = properties.get('name')