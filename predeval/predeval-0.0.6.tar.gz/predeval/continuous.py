"""Library of classes for evaluating continuous model outputs."""
from numbers import Real
from functools import partial
import numpy as np
from scipy import stats
from .parent import ParentPredEval

__author__ = 'Dan Vatterott'
__license__ = 'MIT'


class ContinuousEvaluator(ParentPredEval):
    """
    Evaluator for continuous model outputs (e.g., regression models).

    By default, this will run the tests listed in the assertions
    attribute (['min', 'max', 'mean', 'std', 'ks_test']).
    You can change the tests that will run by listing the desired tests in the assertions parameter.

    The available tests are min, max, mean, std, and ks_test.

    ...

    Parameters
    ----------
    ref_data : list of int or float or np.array
        This the reference data for all tests. All future data will be compared to this data.
    assertions : list of str, optional
        These are the assertion tests that will be created. Defaults is ['chi2_test', 'exist'].
    verbose : bool, optional
        Whether tests should print their output. Default is true

    Attributes
    ----------
    assertion_params : dict
        dictionary of test names and values defining these tests.

        * minimum : float
            Expected minimum.
        * maximum : float
            Expected maximum.
        * mean : float
            Expected mean.
        * std : float
            Expected standard-deviation.
        * ks_stat: float
            ks-test-statistic. When this value is exceeded. The test 'failed'.
        * ks_test : func
            Partially evaluated ks test.
    assertions : list of str
        This list of strings describes the tests that will be run on comparison data.
        Defaults to ['min', 'max', 'mean', 'std', 'ks_test']

    """
    def __init__(
            self,
            ref_data,
            assertions=None,
            verbose=True,
            **kwargs):
        super(ContinuousEvaluator, self).__init__(ref_data, verbose=verbose)

        # ---- Fill in Assertion Parameters ---- #
        self._assertion_params_ = {
            'minimum': kwargs.get('min', None),
            'maximum': kwargs.get('max', None),
            'mean': kwargs.get('mean', None),
            'std': kwargs.get('std', None),
            'ks_test': None
        }

        assert isinstance(kwargs.get('ks_stat', 0.5),
                          Real), 'expected number, input ks_test_stat is not a number'
        self._assertion_params_['ks_stat'] = kwargs.get('ks_stat', 0.5)

        # ---- create list of assertions to test ---- #
        self._possible_assertions_ = {
            'min': (self.update_min, self.check_min),
            'max': (self.update_max, self.check_max),
            'mean': (self.update_mean, self.check_mean),
            'std': (self.update_std, self.check_std),
            'ks_test': (self.update_ks_test, self.check_ks),
        }

        # ---- create list of assertions to test ---- #
        assertions = ['min', 'max', 'mean', 'std', 'ks_test'] if assertions is None else assertions
        self._assertions_ = self._check_assertion_types(assertions)

        # ---- populate assertion tests with reference data ---- #
        for i in self._assertions_:
            self._possible_assertions[i][0](self.ref_data)

        if ('std' not in assertions) and ('mean' in assertions):
            self._possible_assertions['std'][0](self.ref_data)

        # ---- populate list of tests to run and run tests ---- #
        self._tests_ = [self._possible_assertions_[i][1] for i in self._assertions_]

    @property
    def assertion_params(self):
        return self._assertion_params_

    @property
    def _possible_assertions(self):
        return self._possible_assertions_

    @property
    def assertions(self):
        return self._assertions_

    @property
    def _tests(self):
        return self._tests_

    def update_ks_test(self, input_data):
        """Create partially evaluated ks_test.

        Uses `Kolmogorov-Smirnov test from scipy
        <https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kstest.html>`_.

        Parameters
        ----------
        input_data : list or np.array
            This the reference data for the ks-test. All future data will be compared to this data.

        Returns
        -------
        None

        """
        input_data = np.array(input_data) if isinstance(input_data, list) else input_data
        assert len(input_data) >= 25, 'Not enough data for reliable KS tests'
        self.assertion_params['ks_test'] = partial(stats.ks_2samp, np.array(input_data))

    def update_min(self, input_data):
        """Find min of input_data.

        Parameters
        ----------
        input_data : list or np.array
            This the reference data for the min-test. All future data will be compared to this data.

        Returns
        -------
        None

        """
        input_data = np.array(input_data) if isinstance(input_data, list) else input_data
        assert len(input_data.shape) == 1, 'Input data not a single vector'
        self.assertion_params['minimum'] = np.min(input_data)

    def update_max(self, input_data):
        """Find max of input data.

        Parameters
        ----------
        input_data : list or np.array
            This the reference data for the max-test. All future data will be compared to this data.

        Returns
        -------
        None

        """
        input_data = np.array(input_data) if isinstance(input_data, list) else input_data
        assert len(input_data.shape) == 1, 'Input data not a single vector'
        self.assertion_params['maximum'] = np.max(input_data)

    def update_mean(self, input_data):
        """Find mean of input data.

        Parameters
        ----------
        input_data : list or np.array
            This the reference data for the max-test. All future data will be compared to this data.

        Returns
        -------
        None

        """
        input_data = np.array(input_data) if isinstance(input_data, list) else input_data
        assert len(input_data.shape) == 1, 'Input data not a single vector'
        self.assertion_params['mean'] = np.mean(input_data)

    def update_std(self, input_data):
        """Find standard deviation of input data.

        Parameters
        ----------
        input_data : list or np.array
            This the reference data for the max-test. All future data will be compared to this data.

        Returns
        -------
        None

        """
        input_data = np.array(input_data) if isinstance(input_data, list) else input_data
        assert len(input_data.shape) == 1, 'Input data not a single vector'
        self.assertion_params['std'] = np.std(input_data)

    def check_min(self, test_data):
        """Check whether test_data has any smaller values than expected.

        The expected min is controlled by assertion_params['min'].

        Parameters
        ----------
        comparison_data : list or np.array, optional
            This the data that will be compared to the reference data.

        Returns
        -------
        (string, bool)
            2 item tuple with test name and boolean expressing whether passed test.

        """
        assert self.assertion_params['minimum'] is not None, 'Must input or load reference minimum'
        test_data = np.array(test_data) if isinstance(test_data, list) else test_data
        assert len(test_data.shape) == 1, 'Input data not a single vector'
        min_obs = np.min(np.array(test_data))
        passed = True if min_obs >= self.assertion_params['minimum'] else False
        pass_fail = 'Passed' if passed else 'Failed'
        if self.verbose:
            print('{0} min check; min observed={1:.4f}'.format(pass_fail, min_obs))
        return ('min', passed)

    def check_max(self, test_data):
        """Check whether test_data has any larger values than expected.

        The expected max is controlled by assertion_params['max'].

        Parameters
        ----------
        comparison_data : list or np.array, optional
            This the data that will be compared to the reference data.

        Returns
        -------
        (string, bool)
            2 item tuple with test name and boolean expressing whether passed test.

        """
        assert self.assertion_params['maximum'] is not None, 'Must input or load reference maximum'
        test_data = np.array(test_data) if isinstance(test_data, list) else test_data
        assert len(test_data.shape) == 1, 'Input data not a single vector'
        max_obs = np.max(np.array(test_data))
        passed = True if max_obs <= self.assertion_params['maximum'] else False
        pass_fail = 'Passed' if passed else 'Failed'
        if self.verbose:
            print('{0} max check; max observed={1:.4f}'.format(pass_fail, max_obs))
        return ('max', passed)

    def check_mean(self, test_data):
        """Check whether test_data has a different mean than expected.

        If the observed mean is more than 2 standard deviations from the expected mean,
        the test fails.

        The expected mean is controlled by assertion_params['mean'].

        The expected standard deviation is controlled by assertion_params['std'].

        Parameters
        ----------
        comparison_data : list or np.array, optional
            This the data that will be compared to the reference data.

        Returns
        -------
        (string, bool)
            2 item tuple with test name and boolean expressing whether passed test.

        """
        assert self.assertion_params['mean'] is not None, 'Must input or load reference mean'
        assert self.assertion_params['std'] is not None, 'Must input or load reference mean'
        test_data = np.array(test_data) if isinstance(test_data, list) else test_data
        assert len(test_data.shape) == 1, 'Input data not a single vector'
        mean_obs = np.mean(np.array(test_data))

        two_std = self.assertion_params['std'] * 2

        passed = [False, False]
        passed[0] = True if mean_obs >= self.assertion_params['mean'] - two_std else False
        passed[1] = True if mean_obs <= self.assertion_params['mean'] + two_std else False

        pass_fail = 'Passed' if all(passed) else 'Failed'
        if self.verbose:
            print('{0} mean check; mean observed={1:.4f} (Expected {2:.4f} +- {3:.4f})'.format(
                pass_fail,
                mean_obs,
                self.assertion_params['mean'],
                two_std))
        return ('mean', all(passed))

    def check_std(self, test_data):
        """Check whether test_data has any larger values than expected.

        If the observed standard deviation is less than 1/2 the expected std or
        greater than 1.5 times the expected std, then the test fails.

        The expected standard deviation is controlled by assertion_params['std'].

        Parameters
        ----------
        comparison_data : list or np.array, optional
            This the data that will be compared to the reference data.

        Returns
        -------
        (string, bool)
            2 item tuple with test name and boolean expressing whether passed test.

        """
        assert self.assertion_params['std'] is not None, 'Must input or load reference std'
        test_data = np.array(test_data) if isinstance(test_data, list) else test_data
        assert len(test_data.shape) == 1, 'Input data not a single vector'
        std_obs = np.std(np.array(test_data))

        half_std = self.assertion_params['std'] * 0.5

        passed = [False, False]
        passed[0] = True if std_obs >= self.assertion_params['std'] - half_std else False
        passed[1] = True if std_obs <= self.assertion_params['std'] + half_std else False

        pass_fail = 'Passed' if all(passed) else 'Failed'
        if self.verbose:
            print('{0} std check; std observed={1:.4f} (Expected {2:.4f} +- {3:.4f})'.format(
                pass_fail,
                std_obs,
                self.assertion_params['std'],
                half_std))
        return ('std', all(passed))

    def check_ks(self, test_data):
        """Test whether test_data is similar to reference data.

        If the returned ks-test-statistic is greater than the threshold (default 0.2),
        the test failed.

        The threshold is set by assertion_params['ks_test'].

        Uses `Kolmogorov-Smirnov test from scipy
        <https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kstest.html>`_.

        Parameters
        ----------
        comparison_data : list or np.array, optional
            This the data that will be compared to the reference data.

        Returns
        -------
        (string, bool)
            2 item tuple with test name and boolean expressing whether passed test.

        """
        assert self.assertion_params['ks_test'], 'Must input or load reference data ks-test'
        test_data = np.array(test_data) if isinstance(test_data, list) else test_data
        assert len(test_data.shape) == 1, 'Input data not a single vector'
        assert len(test_data) >= 25, 'Not enough data for reliable KS tests'
        test_stat, p_value = self.assertion_params['ks_test'](np.array(test_data))  # pylint: disable=E1102
        passed = True if test_stat <= self.assertion_params['ks_stat'] else False
        pass_fail = 'Passed' if passed else 'Failed'
        if self.verbose:
            print('{0} ks check; test statistic={1:.4f}, p={2:.4f}'.format(
                pass_fail,
                float(test_stat),
                float(p_value)))
        return ('ks', passed)
