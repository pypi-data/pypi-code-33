from datahelper.mongodb.mongodb_data_helper import MongoDBDataHelper
from datahelper.mongodb.data_platform_dev import find as Finder

class DataHelper(MongoDBDataHelper):

    def __init__(
        self, 
        logger=None,
        config_file='go_servers.ini',
        host_name='DataPlatform_DEV_ReadOnly'):
        super().__init__( 
            logger=logger,
            config_file=config_file,
            host_name=host_name)

    def connect(self):
        super().connect()

    def get_battery_swap_log_b(self, start_ts, end_ts=0):
        return super().find(
            Finder.CollectionNames().battery_swap_log_b, 
            Finder.get_battery_swap_log(start_ts, end_ts))

    def get_battery_swap_log(self, start_ts, end_ts=0):
        return super().find(
            Finder.CollectionNames().battery_swap_log, 
            Finder.get_battery_swap_log(start_ts, end_ts))

    def get_vm_status_b(self, start_ts, end_ts=0):
        return super().find(
            Finder.CollectionNames().vm_status_b, 
            Finder.get_vm_status(start_ts, end_ts))

    def get_vm_status(self, start_ts, end_ts=0):
        return super().find(
            Finder.CollectionNames().vm_status, 
            Finder.get_vm_status(start_ts, end_ts))
