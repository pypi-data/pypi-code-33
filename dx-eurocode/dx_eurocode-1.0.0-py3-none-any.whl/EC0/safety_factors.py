"""Abstractions to manipulate safety factors for design
according to principles put forward in §3 of EN 1990.
"""
import pprint

from dx_base.safety_factors import LimitStateFactor


class LimitStateFactors(object):
    """Safety factors for the set of limit states
    referred to in §3.1 (EN-1990)

    :param str design_situation:
    :param dict values: A map of limit-state names to the value
        of the corresponding safety factor.
    """

    def __init__(self, values=None, design_situation='persistent'):
        self.design_situation = design_situation
        self.values = values or {}
        self._ultimate = None
        self._serviceability = None

    def __repr__(self):
        return f'{pprint.pformat(self.values)}'

    @property
    def ultimate(self):
        """The safety factor corresponding to the ultimate limit
        state.

        :rtype: |LimitStateFactor|
        """
        if self._ultimate is None:
            self.ultimate = self.values.get('ultimate', 1.)
        return self._ultimate

    @ultimate.setter
    def ultimate(self, value):
        self._ultimate = LimitStateFactor(
            'ultimate', design_situation=self.design_situation,
            value=value
            )

    @property
    def ULS(self):
        """Alias for the ultimate label.

        :rtype: |LimitStateFactor|
        """
        return self.ultimate

    @ULS.setter
    def ULS(self, value):
        self.ultimate = value

    @property
    def serviceability(self):
        """The safety factor corresponding to the serviceability limit
        state.

        :rtype: |LimitStateFactor|
        """
        if self._serviceability is None:
            self.serviceability = self.values.get('serviceability', 1.0)
        return self._serviceability

    @serviceability.setter
    def serviceability(self, value):
        self._serviceability = LimitStateFactor(
            'serviceability', design_situation=self.design_situation,
            value=value
            )

    @property
    def SLS(self):
        """Alias for the serviceability label.

        :rtype: |LimitStateFactor|
        """
        return self.serviceability

    @SLS.setter
    def SLS(self, value):
        self.serviceability = value


class BaseSafetyFactor(object):
    """Safety factors for the design situations
    and limit-states described in §3 of EN 1990.

    :param dict values: A map between design situations
        and maps of limit-states and corresponding values.
        E.g.::

            {'persistent': {
                'ultimate': 1.15,
                'serviceability': 1.00,
                }}
    """

    def __init__(self, values=None):
        self.values = values or {}
        self._persistent = None
        self._transient = None
        self._accidental = None
        self._seismic = None

    def __repr__(self):
        return f'{pprint.pformat(self.values)}'

    @property
    def persistent(self):
        """The safety factors for all limit-states that
        comprise the 'persistent' design situation

        :rtype: dict
        """
        if self._persistent is None:
            self.persistent = self.values.get('persistent', dict())
        return self._persistent

    @persistent.setter
    def persistent(self, value):
        """
        :param dict values: A map between limit-states and the value
            of the corresponding numerical factor.
        """
        self._persistent = LimitStateFactors(
            design_situation='persistent', values=value
            )

    @property
    def transient(self):
        """The safety factors for all limit-states that
        comprise the 'transient' design situation

        :rtype: dict
        """
        if self._transient is None:
            self.transient = self.values.get('transient', dict())
        return self._transient

    @transient.setter
    def transient(self, value):
        """
        :param dict values: A map between limit-states and the value
            of the corresponding numerical factor.
        """
        self._transient = LimitStateFactors(
            design_situation='transient', values=value
            )

    @property
    def accidental(self):
        """The safety factors for all limit-states that
        comprise the 'accidental' design situation

        :rtype: dict
        """
        if self._accidental is None:
            self.accidental = self.values.get('accidental', dict())
        return self._accidental

    @accidental.setter
    def accidental(self, value):
        """
        :param dict values: A map between limit-states and the value
            of the corresponding numerical factor.
        """
        self._accidental = LimitStateFactors(
            design_situation='accidental', values=value
            )

    @property
    def seismic(self):
        """The safety factors for all limit-states that
        comprise the 'seismic' design situation

        :rtype: dict
        """
        if self._seismic is None:
            self.seismic = self.values.get('seismic', dict())
        return self._seismic

    @seismic.setter
    def seismic(self, value):
        """
        :param dict value: A map between limit-states and the value
            of the corresponding numerical factor.
        """
        self._seismic = LimitStateFactors(
            design_situation='seismic', values=value
            )
