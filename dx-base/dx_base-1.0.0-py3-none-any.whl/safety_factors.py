# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
"""Base abstractions to handle safety-factors in
structural design codes.

We assume the following hierarchy:

* Design-situation

  * Limit-state, performance level etc.

    * Safety Factor
"""


class SafetyFactor(float):
    """A subclass of `float` with a couple of additional attributes.

    >>> from dx_base.safety_factors import SafetyFactor
    >>> sf = SafetyFactor(1.24, 'persistent', 'serviceability')
    >>> sf
    1.24
    >>> sf.design_situation
    'persistent'
    >>> sf.limit_stte
    'serviceability'

    :param float value: The value of the safety factor.
    :param str design_situation: Typically this is provided by
        the implemented design codes.
    :param str limit_state: This design limit-state.
    """

    def __new__(cls, value, *args, **kwargs):
        # Subclassing an immutable type requires setting
        # the __new__ method
        return super().__new__(cls, value)

    def __init__(self, value, design_situation='persistent',
                 limit_state='ultimate'):
        self.design_situation = design_situation
        self.limit_state = limit_state


class LimitStateFactor(SafetyFactor):
    """Safety factor for an arbitrary limit-state.

    :param str name: The name of state.
    :param family: The name of the family of states (if any).
    :param str design_situation:
    :type family: str or None
    """

    def __new__(cls, *args, value=1., **kwargs):
        return super().__new__(cls, value)

    def __init__(self, name, family=None, design_situation='persistent',
                 value=1.):
        self.name = name
        self.family = family
        super().__init__(value, design_situation=design_situation,
                         limit_state=str(self))

    def __str__(self):
        return '-'.join(filter(None, (self.name, self.family)))
