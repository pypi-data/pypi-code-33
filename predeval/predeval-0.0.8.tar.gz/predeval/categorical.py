"""Library of classes for evaluating categorical model outputs."""
from numbers import Real
from functools import partial
import numpy as np
from scipy import stats
from .parent import ParentPredEval

__author__ = 'Dan Vatterott'
__license__ = 'MIT'


def _chi2_test(reference, test_data):
    """Change chi2_contingency inputs for partial evaluation.

    Uses `chi2_contingency test from scipy
    <https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html>`_.

    Parameters
    ----------
    reference : list or np.array
        This the reference data that will be used for the comparison.
    test_data : list or np.array
        This the data compared to the reference data.

    Returns
    -------
    chi2 : float
        The test statistic.
    p : float
        The p-value of the test
    dof : int
        Degrees of freedom
    expected : ndarray, same shape as `observed`
        The expected frequencies, based on the marginal sums of the table.

    """
    obs = np.append([reference], [test_data], axis=0)
    return stats.chi2_contingency(obs)


class CategoricalEvaluator(ParentPredEval):
    """
    Evaluator for categorical model outputs (e.g., classification models).

    By default, this will run the tests listed in the assertions
    attribute (['chi2_test', 'exist']).
    You can change the tests that will run by listing the desired tests in the assertions parameter.

    The available tests are chi2_test and exist.

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

        * chi2_stat : float
            Chi2-test-statistic. When this value is exceeded. The test 'failed'.
        * chi2_test : func
            Partially evaluated chi2 test.
        * cat_exists : list of int or str
            This is a list of the expected model outputs
    assertions : list of str
        This list of strings describes the tests that will be run on comparison data.
        Defaults to ['chi2_test', 'exist']

    """
    def __init__(
            self,
            ref_data,
            assertions=None,
            verbose=True,
            **kwargs):
        super(CategoricalEvaluator, self).__init__(ref_data, verbose=verbose)

        # ---- Fill in Assertion Parameters ---- #
        self._assertion_params_ = {
            'cat_exists': None,
            'chi2_test': None,
        }

        assert isinstance(kwargs.get('chi2_stat', 2),
                          Real), 'expected number, input chi2_test_stat is not a number'
        self._assertion_params_['chi2_stat'] = kwargs.get('chi2_stat', 2)

        # ---- create list of assertions to test ---- #
        self._possible_assertions_ = {
            'exist': (self.update_exist, self.check_exist),
            'chi2_test': (self.update_chi2_test, self.check_chi2),
        }

        # ---- create list of assertions to test ---- #
        assertions = ['exist', 'chi2_test'] if assertions is None else assertions
        self._assertions_ = self._check_assertion_types(assertions)

        # ---- populate assertion tests with reference data ---- #
        for i in self._assertions_:
            self._possible_assertions[i][0](self.ref_data)

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

    def update_chi2_test(self, input_data):
        """Create partially evaluated chi2 contingency test.

        Uses `chi2_contingency test from scipy
        <https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html>`_.

        Parameters
        ----------
        input_data : list or np.array
            This the reference data for the ks-test. All future data will be compared to this data.

        Returns
        -------
        None

        """
        input_data = np.array(input_data) if isinstance(input_data, list) else input_data
        assert len(input_data.shape) == 1, 'Input data not a single vector'
        _, counts = np.unique(input_data, return_counts=True)
        assert all([x >= 5 for x in counts]), \
            'Not enough data of each type for reliable Chi2 Contingency test. Need at least 5.'
        self.assertion_params['chi2_test'] = partial(_chi2_test, np.array(counts))

    def update_exist(self, input_data):
        """Create input data for test checking whether all categorical outputs exist.

        Parameters
        ----------
        input_data : list or np.array
            This the reference data for the check_exist. All future data will be compared to it.

        Returns
        -------
        None

        """
        input_data = np.array(input_data) if isinstance(input_data, list) else input_data
        assert len(input_data.shape) == 1, 'Input data not a single vector'
        self.assertion_params['cat_exists'] = np.unique(input_data)

    def check_chi2(self, test_data):
        """Test whether test_data is similar to reference data.

        If the returned chi2-test-statistic is greater than the threshold (default 2),
        the test failed.

        The threshold is set by assertion_params['chi2_test'].

        Uses `chi2_contingency test from scipy
        <https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html>`_.

        Parameters
        ----------
        test_data : list or np.array
            This the data that will be compared to the reference data.

        Returns
        -------
        (string, bool)
            2 item tuple with test name and boolean expressing whether passed test.

        """
        assert self.assertion_params['chi2_test'], 'Must input or load reference data chi2-test'
        test_data = np.array(test_data) if isinstance(test_data, list) else test_data
        assert len(test_data.shape) == 1, 'Input data not a single vector'
        _, counts = np.unique(test_data, return_counts=True)
        assert all([x >= 5 for x in counts]), \
            'Not enough data of each type for reliable Chi2 Contingency test. '\
            'Need at least 5 values in each cell.'
        try:
            test_stat, p_value, _, _ = self.assertion_params['chi2_test'](counts)  # pylint: disable=E1102
        except ValueError:
            test_stat = 1000.0
            p_value = 0.00
            print('WARNING: NOT ALL CATEGORIES PRESENT')
        passed = True if test_stat <= self.assertion_params['chi2_stat'] else False
        pass_fail = 'Passed' if passed else 'Failed'
        if self.verbose:
            print('{0} chi2 check; test statistic={1:.4f}, p={2:.4f}'.format(
                pass_fail,
                float(test_stat),
                float(p_value)))
        return ('chi2', passed)

    def check_exist(self, test_data):
        """Check that all distinct values present in test_data.

        If any values missing, then the function will return a False (rather than true).

        The expected values is controlled by assertion_params['cat_exists'].

        Parameters
        ----------
        test_data : list or np.array
            This the data that will be compared to the reference data.

        Returns
        -------
        (string, bool)
            2 item tuple with test name and boolean expressing whether passed test.
        """
        assert self.assertion_params['cat_exists'] is not None,\
            'Must input or load reference categories'
        test_data = np.array(test_data) if isinstance(test_data, list) else test_data
        assert len(test_data.shape) == 1, 'Input data not a single vector'
        obs = np.unique(np.array(test_data))
        exp = list(self.assertion_params['cat_exists'])
        passed = True if all([x in exp for x in obs]) and all([x in obs for x in exp]) else False
        pass_fail = 'Passed' if passed else 'Failed'
        if self.verbose:
            print('{0} exist check; observed={1} (Expected {2})'.format(pass_fail, obs, exp))
        return ('exist', passed)
