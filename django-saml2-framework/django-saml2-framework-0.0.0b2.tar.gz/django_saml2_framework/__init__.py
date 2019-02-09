__version__ = '0.0.0-beta.2'

default_app_config = 'django_saml2_framework.apps.Saml2Config'

IDP_SERVERS = {}
SP_SERVERS = {}

def get_idp(entity_id):
    return IDP_SERVERS.get(entity_id, None)

def set_idp(entity_id, idp):
    # todo check idp is an IdP server
    return IDP_SERVERS.update({entity_id: idp})
