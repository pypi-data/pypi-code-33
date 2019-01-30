'''
instances.py: Dfines the ecpc Instance class.
'''
from ecpc import utilities
from ecpc.configuration import database

class Instance(object):
    '''
    The ecpc version of an instance
    '''
    def __init__(self, region=None, instance_type=None):
        self.uid, self.region, self.instance_type = utilities.register(region, instance_type)
        self.pem_file = None
        self.security_group_id = None
        self.ami_id = None
        self.instance_id = None
        database[self.uid] = {
                              'region':, self.region,
                              'instance_type':, self.instance_type,
                              'security_group_id': None,
                              'ami_id': None,
                              'instance_id': None,
                             }

    def create_key_pair(self):
        self.pem_file = utilities.create_key_pair(self.region, self.uid)

    def delete_key_pair(self):
        utilities.delete_key_pair(self.region, self.uid)
        self.pem_file = None

    def create_security_group(self):
        self.security_group_id = utilities.create_security_group(self.region, self.uid)
        database[self.uid]['security_group_id'] = self.security_group_id

    def delete_security_group(self):
        utilities.delete_security_group(self.region, self.security_group_id)
        self.security_group_id = None
        database[self.uid]['security_group_id'] = None

    def select_ami(self, source):
        self.ami_id = utilities.ami_from_source(self.region, source)
        database[self.uid]['ami_id'] = self.ami_id

    def launch(self):
        self.instance_id = utilities.launch(self.region, self.ami_id, self.instance_type, self.uid, self.security_group_id)
        database[self.uid]['instance_id'] = self.instance_id

    def login_string(self):
        return utilities.login_string(self.region, self.uid)

    def terminate(self):
        utilities.terminate(self.region, self.uid)
        self.instance_id = None
