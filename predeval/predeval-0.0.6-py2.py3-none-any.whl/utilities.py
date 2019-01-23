"""Helper functions for the predeval module."""

__author__ = 'Dan Vatterott'
__license__ = 'MIT'


def evaluate_tests(test_ouputs, assert_test=False, verbose=True):
    """Check whether the data passed evaluation tests.

    Parameters
    ----------
    test_ouputs : list of tuples
        Each tuple has a string a boolean. The string describes the test.
        The boolean describes the outcome. True is a pass and False is a fail.
        This is the output of the check_data method.
    assert_test : bool
        Whether to assert the test passed. Default is False.
    verbose : bool
        Whether to print whether each test was passed or not.

    Returns
    -------
    None

    """
    for test_name, test_val in test_ouputs:
        if test_val:
            if verbose:
                print('Passed {} test.'.format(test_name))
        else:
            if verbose:
                print('Failed {} test.'.format(test_name))
            if assert_test:
                assert test_val, 'Error. Failed {} test.'  # pragma: no cover
