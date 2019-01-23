from lbCVMFSchecker.LbCVMFSCheckerPluginBase import PluginBase
import logging

class MockPlugin(PluginBase):

    def __init__(self):
        super(MockPlugin, self).__init__()

    def execute(self):
        logging.info("I'm executed")