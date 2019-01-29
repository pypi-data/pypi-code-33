from unittest import TestCase

from dx_eurocode.EC0.safety_factors import LimitStateFactors, BaseSafetyFactor


class TestLimitStatesFactor(TestCase):

    def setUp(self):
        self.values = {
            'ultimate': 10.,
            'serviceability': 1.,
            }

    def test_instantiation(self):
        values = LimitStateFactors(self.values)
        self.assertIsInstance(values, LimitStateFactors)
        self.assertAlmostEqual(values.ultimate, 10.)
        self.assertAlmostEqual(values.ULS, 10.)
        self.assertAlmostEqual(values.serviceability, 1.)
        self.assertAlmostEqual(values.SLS, 1.)
        values.ULS = 2.
        self.assertAlmostEqual(values.ULS, 2.)
        self.assertAlmostEqual(values.ultimate, 2.)
        values.SLS = 2.
        self.assertAlmostEqual(values.SLS, 2.)
        self.assertAlmostEqual(values.serviceability, 2.)

    def test_default_values(self):
        values = LimitStateFactors()
        self.assertAlmostEqual(values.ULS, 1.)
        self.assertAlmostEqual(values.SLS, 1.)


class TestBaseSafetyFactor(TestCase):

    def setUp(self):
        self.values = {
            'seismic': {
                'ultimate': 3.,
                'serviceability': 2.,
                }
            }

    def test_instantiation(self):
        factor = BaseSafetyFactor(self.values)
        self.assertAlmostEqual(factor.seismic.ultimate, 3.)
        self.assertAlmostEqual(factor.seismic.SLS, 2.)

    def test_default_values(self):
        factor = BaseSafetyFactor()
        self.assertAlmostEqual(factor.persistent.SLS, 1.)
