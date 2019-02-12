import logging

from hashlib import sha1

from saml2.ident import code_binary

from saml2 import md
from saml2 import saml
from saml2.extension import mdui
from saml2.extension import idpdisc
from saml2.extension import dri
from saml2.extension import mdattr
from saml2.extension import ui
from saml2 import xmldsig
from saml2 import xmlenc
from saml2.sdb import context_match

from django.core.cache import caches

from .utils import get_cache_store

logger = logging.getLogger('django')


class SessionStorage(object):
    """Django storage of session information """

    def __init__(self):
        self.db = get_cache_store()
        # self.db = {"assertion": {}, "authn": {}}
        # self.assertion = self.db["assertion"]
        # self.authn = self.db["authn"]

    def key(self, prefix, key):
        return '{}_{}'.format(prefix, key)

    def store_assertion(self, assertion, to_sign):
        logger.info(['LOGGING SESSION', code_binary(assertion.subject.name_id)])
        self.db.set(self.key('assertion', assertion.id), (assertion, to_sign))
        key = sha1(code_binary(assertion.subject.name_id)).hexdigest()

        # below line fails due to django-redis-cache
        # statements = self.db.get_or_set(self.key('authn', key), [])
        statements = self.db.get(self.key('authn', key)) or []

        statements.append(assertion.authn_statement)
        self.db.set(self.key('authn', key), statements)

    def get_assertion(self, cid):
        return self.db.get(self.key('assertion', cid))

    def get_authn_statements(self, name_id, session_index=None, requested_context=None):
        """

        :param name_id:
        :param session_index:
        :param requested_context:
        :return:
        """
        # logger.info(['LOGGING SESSION GETTING AUTHN', code_binary(name_id)])
        result = []
        key = sha1(code_binary(name_id)).hexdigest()
        
        statements = self.db.get(self.key('authn', key))
        if not statements:
            logger.info("Unknown subject %s", name_id)
            return []

        for statement in statements:
            if session_index:
                if statement.session_index != session_index:
                    continue
            if requested_context:
                if not context_match(requested_context, statement[0].authn_context):
                    continue
            result.append(statement)

        return result

    def remove_authn_statements(self, name_id):
        logger.debug("remove authn about: %s", name_id)
        nkey = sha1(code_binary(name_id)).hexdigest()
        self.db.delete(self.key('authn', nkey))
