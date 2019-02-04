# coding=utf-8
from ibm_ai_openscale_cli.setup_classes.setup_services import SetupServices
import logging

logger = logging.getLogger(__name__)

class SetupIBMCloudPrivateServices(SetupServices):

    def __init__(self, args, environment):
        super().__init__(args, environment)

    def setup_aios(self):
        logger.info('Setting up {} instance'.format('AI OpenScale'))
        aios_icp_credentials = {}
        aios_icp_credentials['username'] = self.args.username
        aios_icp_credentials['password'] = self.args.password
        aios_icp_credentials['url'] = '{}'.format(self.args.url)
        aios_icp_credentials['hostname'] = ':'.join(self.args.url.split(':')[:2])
        aios_icp_credentials['port'] = self.args.url.split(':')[2]
        aios_icp_credentials['wml_credentials'] = None
        if self.args.wml is not None:
            aios_icp_credentials['wml_credentials'] = self._read_credentials_from_file(self.args.wml)
        return aios_icp_credentials

    def setup_wml(self):
        logger.info('Setting up {} instance'.format('Watson Machine Learning'))
        wml_credentials = {}
        wml_credentials['username'] = self.args.username
        wml_credentials['password'] = self.args.password
        wml_credentials['url'] = ':'.join(self.args.url.split(':')[:2])
        wml_credentials['instance_id'] = 'icp'
        wml_credentials['apikey'] = ''
        return wml_credentials