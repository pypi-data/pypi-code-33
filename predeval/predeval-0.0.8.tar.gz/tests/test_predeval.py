#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `predeval` package."""
import sys
import os
import numpy as np
from numpy.random import choice, seed
# import pytest

sys.path.append(os.path.abspath("../predeval"))
from predeval import ContinuousEvaluator  # noqa pylint: disable=W0611, C0413
from predeval import CategoricalEvaluator  # noqa pylint: disable=W0611, C0413
from predeval import evaluate_tests  # noqa pylint: disable=W0611, C0413


class TestContinuous(object):
    """Class containing continuous evaluator tests."""

    con_eval = ContinuousEvaluator(np.array([x for x in range(31)]))

    def test_inheritance(self):
        """Assert that continuous evaluator inheriting from parent."""
        assert 'check_data' in dir(self.con_eval), 'Inheritance failed'

    def test_min_param(self):
        """Assert that correctly setting min value."""
        assert self.con_eval.assertion_params['minimum'] == 0

    def test_max_param(self):
        """Assert that correctly setting max value."""
        assert self.con_eval.assertion_params['maximum'] == 30

    def test_mean_param(self):
        """Assert that correctly setting mean value."""
        assert self.con_eval.assertion_params['mean'] == 15.0

    def test_std_param(self):
        """Assert that correctly setting std value."""
        assert self.con_eval.assertion_params['std'] == 8.9442719099991592

    def test_kstest_param(self):
        """Assert that correctly setting ks_stat."""
        assert self.con_eval.assertion_params['ks_stat'] == 0.5

    def test_kstest(self, capsys):
        """Assert that check_ks correct."""
        self.con_eval.check_ks(np.array([x for x in range(31)]))
        captured = capsys.readouterr()
        assert captured.out == "Passed ks check; test statistic=0.0000, p=1.0000\n"
        self.con_eval.check_ks(np.array([x for x in range(20, 51)]))
        captured = capsys.readouterr()
        assert captured.out == "Failed ks check; test statistic=0.6452, p=0.0000\n"

    def test_checkmin(self, capsys):
        """Assert that check_min correct."""
        self.con_eval.check_min(np.array([x for x in range(51)]))
        captured = capsys.readouterr()
        assert captured.out == "Passed min check; min observed=0.0000\n"
        self.con_eval.check_min([-1])
        captured = capsys.readouterr()
        assert captured.out == "Failed min check; min observed=-1.0000\n"

    def test_checkmax(self, capsys):
        """Assert that check_max correct."""
        self.con_eval.check_max(np.array([x for x in range(51)]))
        captured = capsys.readouterr()
        assert captured.out == "Failed max check; max observed=50.0000\n"
        self.con_eval.check_max([30])
        captured = capsys.readouterr()
        assert captured.out == "Passed max check; max observed=30.0000\n"

    def test_checkmean(self, capsys):
        """Assert that check_mean correct."""
        self.con_eval.check_mean(np.array([x for x in range(101)]))
        captured = capsys.readouterr()
        assert captured.out == "Failed mean check; mean observed=50.0000 (Expected 15.0000 +- 17.8885)\n"  # noqa pylint: disable=C0301
        self.con_eval.check_mean(np.array([x for x in range(31)]))
        captured = capsys.readouterr()
        assert captured.out == "Passed mean check; mean observed=15.0000 (Expected 15.0000 +- 17.8885)\n"  # noqa pylint: disable=C0301

    def test_checkstd(self, capsys):
        """Assert that check_std correct."""
        self.con_eval.check_std(np.array([x for x in range(101)]))
        captured = capsys.readouterr()
        assert captured.out == "Failed std check; std observed=29.1548 (Expected 8.9443 +- 4.4721)\n"  # noqa pylint: disable=C0301
        self.con_eval.check_std(np.array([x for x in range(31)]))
        captured = capsys.readouterr()
        assert captured.out == "Passed std check; std observed=8.9443 (Expected 8.9443 +- 4.4721)\n"  # noqa pylint: disable=C0301

    def test_update_ks_test(self, capsys):
        """Assert that correctly updating ks_test."""
        self.con_eval.update_ks_test(np.array([x for x in range(20, 51)]))
        self.con_eval.check_ks(np.array([x for x in range(31)]))
        captured = capsys.readouterr()
        assert captured.out == "Failed ks check; test statistic=0.6452, p=0.0000\n"

    def test_update_min(self):
        """Assert that correctly updating min."""
        self.con_eval.update_min([-500])
        assert self.con_eval.assertion_params['minimum'] == -500

    def test_update_max(self):
        """Assert that correctly updating max."""
        self.con_eval.update_max([-500])
        assert self.con_eval.assertion_params['maximum'] == -500

    def test_update_mean(self):
        """Assert that correctly updating mean."""
        self.con_eval.update_mean([-500])
        assert self.con_eval.assertion_params['mean'] == -500

    def test_update_std(self):
        """Assert that correctly updating std."""
        self.con_eval.update_std([0, 5])
        assert self.con_eval.assertion_params['std'] == 2.5

    def test_check_data(self, capsys):
        """Assert that correctly using check_data."""
        self.con_eval.update_ks_test(np.array([x for x in range(51)]))
        self.con_eval.check_data(np.array([x for x in range(51)]))
        captured = capsys.readouterr()
        expect_out = ("Passed min check; min observed=0.0000\n"
                      "Failed max check; max observed=50.0000\n"
                      "Failed mean check; mean observed=25.0000 (Expected -500.0000 +- 5.0000)\n"
                      "Failed std check; std observed=14.7196 (Expected 2.5000 +- 1.2500)\n"
                      "Passed ks check; test statistic=0.0000, p=1.0000\n")
        assert captured.out == expect_out

    def test_check_assertions(self, capsys):  # pylint: disable=R0201
        """Assert that correctly checking assertions."""
        con_eval = ContinuousEvaluator([x for x in range(30)], assertions='max')
        assert con_eval.assertions == ['max']
        con_eval.check_data(np.array([x for x in range(51)]))
        captured = capsys.readouterr()
        expect_out = ("Failed max check; max observed=50.0000\n")
        assert captured.out == expect_out
        con_eval = ContinuousEvaluator([x for x in range(30)], assertions=['max'])
        assert con_eval.assertions == ['max']
        con_eval = ContinuousEvaluator([x for x in range(30)], assertions=['max', 'min'])
        assert con_eval.assertions == ['max', 'min']
        assert con_eval.assertion_params['std'] is None
        con_eval = ContinuousEvaluator([x for x in range(30)], assertions=['mean'])
        assert con_eval.assertion_params['std'] == 8.65544144839919

    def test_update_param(self):
        """Assert that correctly updating parameters."""
        self.con_eval.update_param('minimum', -1)
        assert self.con_eval.assertion_params['minimum'] == -1


class TestCategorical(object):
    """Class containing categorical evaluator tests."""

    seed(1234)
    con_eval = CategoricalEvaluator(choice([0, 1, 2], size=(100,)))

    def test_inheritance(self):
        """Assert that continuous evaluator inheriting from parent."""
        assert 'check_data' in dir(self.con_eval), 'Inheritance failed'

    def test_catexist_param(self):
        """Assert that correctly setting cat_exist value."""
        assert all([a == b for a, b in zip(self.con_eval.assertion_params['cat_exists'], [0, 1, 2])])  # noqa pylint: disable=C0301

    def test_chi2_param(self):
        """Assert that correctly setting chi2_stat."""
        assert self.con_eval.assertion_params['chi2_stat'] == 2

    def test_update_param(self):
        """Assert that correctly updating parameters."""
        self.con_eval.update_param('chi2_stat', 5)
        assert self.con_eval.assertion_params['chi2_stat'] == 5

    def test_chi2test(self, capsys):
        """Assert that check_chi2 correct."""
        seed(1234)
        new_out = choice([0, 1, 2], size=(100,))
        self.con_eval.check_chi2(new_out)
        captured = capsys.readouterr()
        assert captured.out == "Passed chi2 check; test statistic=0.0000, p=1.0000\n"
        new_out[:50] = 0
        self.con_eval.check_chi2(new_out)
        captured = capsys.readouterr()
        assert captured.out == "Failed chi2 check; test statistic=19.3562, p=0.0001\n"

    def test_chi2short(self, capsys):
        """Assert that check_chi2 correct."""
        seed(1234)
        new_out = choice([0, 1], size=(100,))
        self.con_eval.check_chi2(new_out)
        captured = capsys.readouterr()
        assert captured.out == ("WARNING: NOT ALL CATEGORIES PRESENT\n"
                                "Failed chi2 check; test statistic=1000.0000, p=0.0000\n")

    def test_checkexist(self, capsys):
        """Assert that check_exist correct."""
        self.con_eval.check_exist([0, 1, 2])
        captured = capsys.readouterr()
        assert captured.out == "Passed exist check; observed=[0 1 2] (Expected [0, 1, 2])\n"
        self.con_eval.check_exist([1, 2])
        captured = capsys.readouterr()
        assert captured.out == "Failed exist check; observed=[1 2] (Expected [0, 1, 2])\n"

    def test_updateexist(self, capsys):
        """Assert that update_exist correct."""
        self.con_eval.update_exist([1, 2])
        self.con_eval.check_exist([0, 1, 2])
        captured = capsys.readouterr()
        assert captured.out == "Failed exist check; observed=[0 1 2] (Expected [1, 2])\n"

    def test_updatechi2(self, capsys):
        """Assert that update_chi2 correct."""
        seed(1234)
        new_out = choice([0, 1, 2], size=(100,))
        new_out[:50] = 0
        self.con_eval.update_chi2_test(new_out)
        new_out[:50] = 1
        self.con_eval.check_chi2(new_out)
        captured = capsys.readouterr()
        assert captured.out == "Failed chi2 check; test statistic=61.1210, p=0.0000\n"

    def test_check_assertions(self):  # pylint: disable=R0201
        """Assert that correctly checking assertions."""
        con_eval = CategoricalEvaluator([0, 1, 2], assertions='exist')
        assert con_eval.assertions == ['exist']
        con_eval.check_data([0, 2])

    def test_check_data(self, capsys):
        """Assert that correctly using check data."""
        seed(1234)
        new_out = choice([0, 1, 2], size=(100,))
        self.con_eval = CategoricalEvaluator(new_out)
        self.con_eval.check_data(new_out)
        captured = capsys.readouterr()
        expect_out = ("Passed exist check; observed=[0 1 2] (Expected [0, 1, 2])\n"
                      "Passed chi2 check; test statistic=0.0000, p=1.0000\n")
        assert captured.out == expect_out


class TestUtilities(object):
    """Class containing test of utility functions."""

    seed(1234)
    con_eval = CategoricalEvaluator(choice([0, 1, 2], size=(100,)), verbose=False)

    def test_eval_tests(self, capsys):
        """assert that evaluate tests is correct."""
        seed(1234)
        new_out = choice([0, 1, 2], size=(100,))
        output = self.con_eval.check_data(new_out)
        evaluate_tests(output)
        captured = capsys.readouterr()
        expect_out = ("Passed exist test.\n"
                      "Passed chi2 test.\n")
        assert captured.out == expect_out

    def test_eval_tests_fail(self, capsys):
        """assert that evaluate tests is correct."""
        seed(1234)
        new_out = choice([0, 1, 2], size=(100,))
        new_out[:50] = 1
        output = self.con_eval.check_data(new_out)
        evaluate_tests(output)
        captured = capsys.readouterr()
        expect_out = ("Passed exist test.\n"
                      "Failed chi2 test.\n")
        assert captured.out == expect_out

    def test_eval_tests_noprint(self, capsys):
        """assert that evaluate tests is correct."""
        seed(1234)
        new_out = choice([0, 1, 2], size=(100,))
        output = self.con_eval.check_data(new_out)
        evaluate_tests(output, verbose=False)
        captured = capsys.readouterr()
        expect_out = ''
        assert captured.out == expect_out
