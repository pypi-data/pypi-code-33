# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
from dx_utilities.exceptions import CodedException


__all__ = ['ReinforcementError', 'ImplementationError',
           'UnrecognizedMaterialError']


class ReinforcementError(CodedException):
    pass


class ImplementationError(CodedException):
    pass


class UnrecognizedMaterialError(CodedException):
    """Exception to be raised if a user
    tries to configure a material not supported
    in the dx ecosystem.
    """
    pass
