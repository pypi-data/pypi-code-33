import xml.etree.ElementTree as ElementTree

from flask_script import Option

from probator import PROBATOR_PLUGINS
from probator.config import dbconfig, DBCString
from probator.plugins.commands import BaseCommand


class ImportSAML(BaseCommand):
    """Imports a SAML metadata.xml file and populates the SAML configuration"""
    name = 'ImportSAML'
    option_list = (
        Option(
            '-m', '--metadata-file',
            dest='metadata',
            type=str,
            help='Path to the metadata.xml file',
            required=True
        ),
        Option(
            '-f', '--fqdn',
            dest='fqdn',
            type=str,
            help='Domain name of the instance',
            required=True
        )
    )

    def run(self, **kwargs):
        for entry_point in PROBATOR_PLUGINS['probator.plugins.auth']['plugins']:
            if entry_point.module_name == 'probator_auth_onelogin_saml':
                cls = entry_point.load()
                config_namespace = cls.ns
                break
        else:
            self.log.error('The SAML authentication plugin is not installed')
            return

        try:
            ns = {
                'ds': 'http://www.w3.org/2000/09/xmldsig#',
                'saml': 'urn:oasis:names:tc:SAML:2.0:metadata'
            }

            xml = ElementTree.parse(kwargs['metadata'])
            root = xml.getroot()

            idp_entity_id = root.attrib['entityID']
            idp_cert = root.find('.//ds:X509Certificate', ns).text
            idp_sls = root.find('.//saml:SingleLogoutService', ns).attrib['Location']
            idp_ssos = root.find(
                './/saml:SingleSignOnService[@Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"]',
                ns
            ).attrib['Location']

            fqdn = kwargs['fqdn']
            sp_acs = f'https://{fqdn}/saml/login/consumer'
            sp_sls = f'https://{fqdn}/saml/logout/consumer'

            dbconfig.set(config_namespace, 'idp_entity_id', DBCString(idp_entity_id))
            dbconfig.set(config_namespace, 'idp_sls', DBCString(idp_sls))
            dbconfig.set(config_namespace, 'idp_ssos', DBCString(idp_ssos))
            dbconfig.set(config_namespace, 'idp_x509cert', DBCString(idp_cert.replace('\n', '')))
            dbconfig.set(config_namespace, 'sp_entity_id', DBCString(fqdn))
            dbconfig.set(config_namespace, 'sp_acs', DBCString(sp_acs))
            dbconfig.set(config_namespace, 'sp_sls', DBCString(sp_sls))

            self.log.info(f'Updated SAML configuration from {kwargs["metadata"]}')

        except OSError as ex:
            self.log.error(f'Unable to load metadata file {kwargs["metadata"]}: {ex}')
            return 1

        except ElementTree.ParseError as ex:
            self.log.error(f'Failed reading metadata XML file: {ex}')
            return 2

        except Exception as ex:
            self.log.error(f'Error while updating configuration: {ex}')
            return 3
