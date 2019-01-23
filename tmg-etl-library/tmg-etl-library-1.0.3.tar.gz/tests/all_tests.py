from tests import BQ_to_X_tests, CSV_to_X_tests
import os

if __name__ == '__main__':
    for test_package in [BQ_to_X_tests, CSV_to_X_tests]:
        print('Running Tests for %s') % test_package.__name__