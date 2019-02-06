__all__ = ['app', 'artemis', 'billing', 'logistics', 'rrhh', 'security']

import string

from sqlalchemy import type_coerce, func, String
from sqlalchemy.dialects.postgresql import BYTEA


# General methods
class PGPString(BYTEA):
    def __init__(self, passphrase, length=None):
        super(PGPString, self).__init__(length)
        self.passphrase = passphrase

    def bind_expression(self, bindvalue) -> bytearray:
        bindvalue = type_coerce(bindvalue, String)
        return func.pgp_sym_encrypt(bindvalue, self.passphrase)

    def column_expression(self, col) -> string:
        return func.pgp_sym_decrypt(col, self.passphrase)
