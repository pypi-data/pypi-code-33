import copy
import statistics

import pytest

from smallerize.smallerize import (
    Arm, Factor, Minimizer
)
from .fixtures import (
    factor_age,
    factor_sex,
    arm_one,
    arm_two,
    get_simple_minimizer,
    get_example_3to1,
    example_male_age_participants,
    example_table_one
)


class TestFactor:

    def test_creation(self, factor_age):
        assert factor_age.name == 'Age'
        assert ['10-20', '20-30', '30+'] == list(factor_age.levels)

    def test_not_enough_levels(self):
        with pytest.raises(ValueError,
                           message="Factors must have 2 or more levels"):
            Factor('Age', levels=['10-20'])

    def test_valid_weight(self):
        with pytest.raises(ValueError,
                           message="Factor weight must be a positive number"):
            Factor('Age', ['10-20', '20-30'], weight=-1)

    def test_print(self, factor_age):
        assert (
            str(factor_age) == "Factor(Age, levels=('10-20', '20-30', '30+'))"
        )
        assert (
            repr(factor_age) == "Factor(Age, levels=('10-20', '20-30', '30+'))"
        )

    def test_random_levels(self, factor_age):
        single = factor_age.get_random_level()
        assert single in factor_age.levels
        multiple = factor_age.get_random_level_multiple(n=5)
        assert all(random_level in factor_age.levels
                   for random_level in multiple)


class TestArm:

    def test_creation(self, arm_one):
        assert arm_one.name == 'Treat1'
        # Default allocation ratio
        assert arm_one.allocation_ratio == 1

    def test_print(self, arm_one):
        assert str(arm_one) == "Arm(Treat1, allocation_ratio=1)"

    def test_other_allocation_ratio(self):
        name = 'Treat2'
        ratio = 2
        arm = Arm(name, allocation_ratio=ratio)

        assert arm.allocation_ratio == ratio

    def test_non_integer_ratio(self):
        name = 'Treat1'
        ratio = 0.5
        with pytest.raises(ValueError,
                           message="Allocation ratio must be an integer."):
            arm = Arm(name, allocation_ratio=ratio)


class TestMinimizer:

    @pytest.fixture
    def example_counts_empty(self):
        counts = {
            ('Male',): {'Treat1': 0, 'Treat2': 0},
            ('Female',): {'Treat1': 0, 'Treat2': 0}
        }
        return counts

    def test_creation(self, get_simple_minimizer, example_counts_empty):
        minimizer = get_simple_minimizer()

        assert minimizer.factor_names == ['Sex']
        assert minimizer._count_table == example_counts_empty

    def test_invalid_imbalance_methods(self, get_simple_minimizer):
        with pytest.raises(ValueError) as except_info:
            get_simple_minimizer(d_imbalance_method='square_root')
            assert "Invalid d_imbalance_method" in except_info.value

        with pytest.raises(ValueError) as except_info:
            get_simple_minimizer(
                arms=[Arm('Arm1'), Arm('Arm2'), Arm('Arm3')],
                d_imbalance_method='is_largest'
            )
            assert "more than 2 arms" in except_info.value

        with pytest.raises(ValueError) as except_info:
            get_simple_minimizer(d_imbalance_method='over_max_range')
            assert "d_max_range" in except_info.value

    def test_invalid_probability_methods(self, get_simple_minimizer):
        with pytest.raises(ValueError) as except_info:
            get_simple_minimizer(probability_method='new_method')
            assert "must be one of" in except_info.value
            assert "new_method given" in except_info.value

    def test_probability_method_args(self, get_simple_minimizer, capsys):
        get_simple_minimizer(probability_method='rank_all')
        captured = capsys.readouterr()
        assert "q argument was not provided" in captured.out

    def test_assign_participant(self, get_simple_minimizer):
        minimizer = get_simple_minimizer()
        new_p = {'Sex': 'Male'}
        arm = minimizer.assign_participant(new_p)
        # Not sure what we can really test for when assigning to
        #   a completely empty trial, without testing
        #   the statistical properties
        assert arm in (minimizer.arm_names)
        assigned = minimizer._count_table[('Male',)][arm]
        assert assigned == 1
        assert sum(minimizer._count_table[('Male',)].values()) == 1

    def test_get_total_imbalance_empty(self, get_simple_minimizer):
        minimizer = get_simple_minimizer()
        new_p = {'Sex': 'Male'}
        imbalances = minimizer.get_new_total_imbalances(new_p)
        # All imbalances should be equal when no participants
        #   have been assigned (not true when allocation
        #   ratios are not equal)
        assert len(set(imbalances.values())) == 1

    def test_pure_random_probs(self, get_simple_minimizer):
        # This is special cased, as we can skip calculating the imbalance
        # when using pure_random
        # Basic tests to ensure this special case isn't broken
        minimizer = get_simple_minimizer(probability_method='pure_random')
        info = minimizer.get_assignment_info({'Sex': 'Male'})
        assert info['prob'] == 0.5
        assert info['arm'] in minimizer.arm_names
        arm = minimizer.assign_participant({'Sex': 'Male'})
        assert arm in minimizer.arm_names

    def test_single_or_multiple_factors(
            self,
            factor_sex,
            factor_age,
            arm_one,
            arm_two):
        """
        Allow either a single factor, or a list of factors, when
        creating a Minimizer.
        """
        min1 = Minimizer(factor_sex, [arm_one, arm_two])
        assert min1.factor_names == [factor_sex.name]
        min2 = Minimizer([factor_sex, factor_age], [arm_one, arm_two])
        assert min2.factor_names == [factor_sex.name, factor_age.name]

    def test_set_allocation_ratios(self, get_simple_minimizer):
        arm1 = Arm('Treat1', allocation_ratio=2)
        arm2 = Arm('Treat2', allocation_ratio=3)
        minimizer = get_simple_minimizer(arms=[arm1, arm2])

        assert minimizer._arm_ratios == {'Treat1': 2, 'Treat2': 3}

    def test_x_counts(self, get_example_3to1):
        """
        Check that when we assign x participants with the same factor
        level to treatment A, and y to treatment B, we get
        {A: x, B: y} as the result.
        """
        minimizer = get_example_3to1()

        example_xs = minimizer.get_current_x_counts({'Sex': 'Male'})
        assert example_xs['Sex'] == {'Treat1': 3, 'Treat2': 1}

    def test_x_counts_invalid_factor_levels(
            self,
            factor_age,
            factor_sex,
            arm_one,
            arm_two,
            example_male_age_participants):
        minimizer = Minimizer(
            [factor_age, factor_sex],
            [arm_one, arm_two]
        )
        for participant in example_male_age_participants:
            arm = participant.pop('Arm')
            minimizer.add_existing_participant(participant, arm)

        with pytest.raises(ValueError) as except_info:
            minimizer.get_current_x_counts({'Sex': 'Male'})
            assert "All factors in the trial" in except_info.value

    def test_x_counts_multiple_factors(
            self,
            factor_age,
            factor_sex,
            arm_one,
            arm_two,
            example_male_age_participants):
        minimizer = Minimizer(
            [factor_age, factor_sex],
            [arm_one, arm_two]
        )
        for participant in example_male_age_participants:
            arm = participant.pop('Arm')
            minimizer.add_existing_participant(participant, arm)

        example_xs = minimizer.get_current_x_counts(
            {'Sex': 'Male', 'Age': '10-20'}
        )
        assert example_xs['Sex'] == {'Treat1': 10, 'Treat2': 10}
        assert example_xs['Age'] == {'Treat1': 6, 'Treat2': 4}

    def test_x_counts_with_ratios(self, get_example_3to1):
        """
        When arms have different allocation ratios, we divide the x counts by
        the ratio before calculating balance.
        """
        arm1 = Arm('Treat1', allocation_ratio=3)
        arm2 = Arm('Treat2', allocation_ratio=1)
        minimizer = get_example_3to1(arms=[arm1, arm2])

        example_xs = minimizer.get_current_x_counts({'Sex': 'Male'})
        assert example_xs['Sex'] == {'Treat1': 1, 'Treat2': 1}

    def test_x_count_after_allocation(self, get_example_3to1):
        minimizer = get_example_3to1()

        example_xs = minimizer.get_current_x_counts({'Sex': 'Male'})

        example_x_after_treat1 = minimizer._get_count_after_assignment(
            arm_counts=example_xs['Sex'],
            arm_name='Treat1'
        )
        assert example_x_after_treat1 == {'Treat1': 4, 'Treat2': 1}

        example_x_after_treat2 = minimizer._get_count_after_assignment(
            arm_counts=example_xs['Sex'],
            arm_name='Treat2'
        )
        assert example_x_after_treat2 == {'Treat1': 3, 'Treat2': 2}

    def test_get_all_counts_after_assignment(self, get_example_3to1):
        minimizer = get_example_3to1()

        example_counts = minimizer.get_all_new_counts({'Sex': 'Male'})
        treat1_sex_counts = example_counts['Treat1']['Sex']
        assert treat1_sex_counts == {'Treat1': 4, 'Treat2': 1}
        treat2_sex_counts = example_counts['Treat2']['Sex']
        assert treat2_sex_counts == {'Treat1': 3, 'Treat2': 2}

    def test_d_imbalance_methods(self):
        # Examples from Han 2009
        imbalance_methods = ('range', 'standard_deviation', 'variance',
                             'marginal_balance')
        female = {'a1': 41, 'a2': 47, 'a3': 45}
        f_scores = {
            method: Minimizer.D_IMBALANCE_METHODS[method](female)
            for method in imbalance_methods
        }
        assert f_scores['range'] == 6
        assert pytest.approx(f_scores['standard_deviation'], 3.06)
        assert pytest.approx(f_scores['variance'], 9.33)
        assert pytest.approx(f_scores['marginal_balance'], 0.0451)

        site4 = {'a1': 7, 'a2': 8, 'a3': 7}
        s_scores = {
            method: Minimizer.D_IMBALANCE_METHODS[method](site4)
            for method in imbalance_methods
        }
        assert s_scores['range'] == 1
        assert pytest.approx(s_scores['standard_deviation'], 0.577)
        assert pytest.approx(s_scores['variance'], 0.333)
        assert pytest.approx(s_scores['marginal_balance'], 0.0455)

    def test_get_ds_after_assignment(self, get_example_3to1):
        new_p = {'Sex': 'Male'}

        std_minimizer = get_example_3to1(
            d_imbalance_method='standard_deviation'
        )
        std_ds = std_minimizer.get_new_ds(new_p)
        assert std_ds['Treat1']['Sex'] == statistics.stdev([4, 1])
        assert std_ds['Treat2']['Sex'] == statistics.stdev([3, 2])

        var_minimizer = get_example_3to1(d_imbalance_method='variance')
        var_ds = var_minimizer.get_new_ds(new_p)
        assert var_ds['Treat1']['Sex'] == statistics.variance([4, 1])
        assert var_ds['Treat2']['Sex'] == statistics.variance([3, 2])

        range_minimizer = get_example_3to1(d_imbalance_method='range')
        range_ds = range_minimizer.get_new_ds(new_p)
        assert range_ds['Treat1']['Sex'] == (4 - 1)
        assert range_ds['Treat2']['Sex'] == (3 - 2)

        over_minimizer = get_example_3to1(
            d_imbalance_method='over_max_range',
            d_max_range=2
        )
        over_ds = over_minimizer.get_new_ds(new_p)
        assert over_ds['Treat1']['Sex'] == 1
        assert over_ds['Treat2']['Sex'] == 0

        largest_minimizer = get_example_3to1(d_imbalance_method='is_largest')
        largest_ds = largest_minimizer.get_new_ds(new_p)
        assert largest_ds['Treat1']['Sex'] == 1
        assert largest_ds['Treat2']['Sex'] == 0

    def test_get_total_imbalances_after_assignment(
            self,
            factor_sex, factor_age,
            arm_one, arm_two,
            example_male_age_participants):

        minimizer = Minimizer(
            [factor_age, factor_sex],
            [arm_one, arm_two],
            d_imbalance_method='range'
        )
        for participant in example_male_age_participants:
            arm = participant.pop('Arm')
            minimizer.add_existing_participant(participant, arm)

        imbalance = minimizer.get_new_total_imbalances(
            {'Sex': 'Male', 'Age': '10-20'}
        )
        assert imbalance == {'Treat1': 4, 'Treat2': 2}

    def test_get_total_imbalances_after_assignment_weighted(
            self, factor_sex, factor_age, arm_one, arm_two,
            example_male_age_participants
    ):
        sex = factor_sex
        sex.weight = 0.5
        age = factor_age
        age.weight = 3

        minimizer = Minimizer(
            [sex, age],
            [arm_one, arm_two],
            d_imbalance_method='range',
            total_imbalance_method='weighted_sum'
        )
        for participant in example_male_age_participants:
            arm = participant.pop('Arm')
            minimizer.add_existing_participant(participant, arm)

        imbalance = minimizer.get_new_total_imbalances(
            {'Sex': 'Male', 'Age': '10-20'}
        )
        assert imbalance == {
            'Treat1': 1 * 0.5 + 3 * 3,
            'Treat2': 1 * 0.5 + 1 * 3
        }

    def test_rank_imbalances(self):
        imbalance = {'largest': 5, 'smallest': 2, 'tied1': 3,
                     'tied2': 3}
        # Result should be randomized so test multiple times
        for i in range(5):
            ranked = Minimizer._rank_imbalances(imbalance)
            first, tied1, tied2, last = ranked
            assert first == 'smallest'
            assert tied1 in ('tied1', 'tied2')
            assert (tied2 in ('tied1', 'tied2')) and (tied1 != tied2)
            assert last == 'largest'

    def test_get_arm_probability(
            self,
            factor_sex, factor_age,
            arm_one, arm_two,
            get_simple_minimizer):
        # Probability based on treatment with lowest imbalance only
        imbalance_best = {'Treat1': 2, 'Treat2': 5}
        minimizer_best = Minimizer(
            factors=[factor_sex, factor_age],
            arms=[arm_one, arm_two],
            probability_method='best_only',
            preferred_p=0.7
        )
        ps_best = minimizer_best.get_arm_probability(imbalance_best)
        assert ps_best['Treat1'] == pytest.approx(0.7)
        assert ps_best['Treat2'] == pytest.approx(0.3)

        imbalance_multi = {'Treat1': 3, 'Treat2': 5, 'Treat3': 4, 'Treat4': 7}
        minimizer_multi = Minimizer(
            factors=[factor_sex, factor_age],
            arms=[Arm('Treat1'), Arm('Treat2'), Arm('Treat3'), Arm('Treat4')],
            probability_method='best_only',
            preferred_p=2 / 3
        )
        ps_multi = minimizer_multi.get_arm_probability(imbalance_multi)
        assert ps_multi['Treat1'] == pytest.approx(2 / 3)
        # Remaining probability divided equally among non-preferred treatments
        assert ps_multi['Treat2'] == pytest.approx(1 / 9)
        assert ps_multi['Treat3'] == pytest.approx(1 / 9)
        assert ps_multi['Treat4'] == pytest.approx(1 / 9)

        # Probabilities based on rank
        # This example from the original Pocock + Simon paper introducing
        #   the method
        minimizer_ranks = Minimizer(
            factors=[factor_sex, factor_age],
            arms=[Arm('Treat1'), Arm('Treat2'), Arm('Treat3'), Arm('Treat4')],
            probability_method='rank_all',
            q=0.5
        )
        ps_ranks = minimizer_ranks.get_arm_probability(imbalance_multi)
        assert ps_ranks['Treat1'] == pytest.approx(0.4)
        assert ps_ranks['Treat2'] == pytest.approx(0.2)
        assert ps_ranks['Treat3'] == pytest.approx(0.3)
        assert ps_ranks['Treat4'] == pytest.approx(0.1)

        # Pure random assignment
        minimizer_equal = get_simple_minimizer(
            arms=[Arm('Treat1'), Arm('Treat2'), Arm('Treat3')],
            probability_method='pure_random'
        )
        imbalances_equal = {'Treat1': 5, 'Treat2': 8, 'Treat3': 1}
        ps_equal = minimizer_equal.get_arm_probability(imbalances_equal)
        assert ps_equal['Treat1'] == ps_equal['Treat2']
        assert ps_equal['Treat1'] == ps_equal['Treat3']

        # Pure random assignment with ratios
        minimizer_ratio = get_simple_minimizer(
            arms=[Arm('Treat1', allocation_ratio=2),
                  Arm('Treat2', allocation_ratio=1)],
            probability_method='pure_random'
        )
        ps_ratio = minimizer_ratio.get_arm_probability(imbalances=None)
        assert ps_ratio['Treat1'] == (2 * ps_ratio['Treat2'])

    def test_get_arm_probability_biased_coin(self, get_simple_minimizer):
        # These examples from the Han 2009 article introducing the
        #   method
        bcm_arms = [
            Arm('AC', allocation_ratio=1),
            Arm('PL', allocation_ratio=2),
            Arm('DI', allocation_ratio=3)
        ]
        minimizer_bcm = get_simple_minimizer(
            arms=bcm_arms,
            probability_method='biased_coin'
        )
        ac_preferred = minimizer_bcm.get_arm_probability(
            imbalances={'AC': 1, 'PL': 2, 'DI': 2}
        )
        assert pytest.approx(ac_preferred['AC'], 0.7)
        assert pytest.approx(ac_preferred['PL'], 0.12)
        assert pytest.approx(ac_preferred['DI'], 0.18)

        pl_preferred = minimizer_bcm.get_arm_probability(
            imbalances={'AC': 2, 'PL': 1, 'DI': 2}
        )
        assert pytest.approx(pl_preferred['AC'], 0.06)
        assert pytest.approx(pl_preferred['PL'], 0.76)
        assert pytest.approx(pl_preferred['DI'], 0.18)

        di_preferred = minimizer_bcm.get_arm_probability(
            imbalances={'AC': 2, 'PL': 2, 'DI': 1}
        )
        assert pytest.approx(di_preferred['AC'], 0.06)
        assert pytest.approx(di_preferred['PL'], 0.12)
        assert pytest.approx(di_preferred['DI'], 0.82)

    def test_invalid_prob_args(self, get_simple_minimizer):
        # preferred_p must be > 1 / N and < 1, for both
        #   best_only and biased_coin
        with pytest.raises(ValueError):
            min1 = get_simple_minimizer(
                probability_method='best_only',
                preferred_p=0.4
            )
        with pytest.raises(ValueError):
            min1 = get_simple_minimizer(
                probability_method='biased_coin',
                preferred_p=0.4
            )
        with pytest.raises(ValueError):
            min2 = get_simple_minimizer(
                probability_method='best_only',
                preferred_p=1.1
            )

        # For q: (1 / N) < q < (2 / (N - 1))
        with pytest.raises(ValueError):
            min3 = get_simple_minimizer(
                probability_method='rank_all',
                q=0.4
            )
        with pytest.raises(ValueError):
            min4 = get_simple_minimizer(
                probability_method='rank_all',
                q=2.1
            )

    def test_get_chosen_arm(self):
        # Not sure of best way to test random results
        probs = {'a': 0.95, 'b': 0.05}
        arms = [
            Minimizer._get_chosen_arm(probs)
            for n in range(20)
        ]

        assert arms.count('a') > arms.count('b')

    def test_deterministic_assignment(self, get_example_3to1):
        """
        Test that the arm with least imbalance is always chosen
        when preferred_p is 1.0
        """
        # NOTE: random results so not guaranteed to show a bad
        #   result every time if the code is wrong,
        #   not sure how to test this fully
        minimizer = get_example_3to1(
            probability_method='best_only',
            preferred_p=1.0
        )
        for i in range(10):
            assign_info = minimizer.get_assignment_info({'Sex': 'Male'})
            assert assign_info['arm'] == 'Treat2'

    def test_get_assignment_info_no_assignment(self, get_example_3to1):
        # Test with deterministic assignment so we know
        # which arm will be assigned
        minimizer = get_example_3to1(
            probability_method='best_only',
            preferred_p=1.0
        )
        counts_before = minimizer.get_current_x_counts({'Sex': 'Male'})
        assign_info = minimizer.get_assignment_info({'Sex': 'Male'})
        assert assign_info['arm'] == 'Treat2'
        assert assign_info['prob'] == 1.0
        assert assign_info['most_favoured']
        counts_after = minimizer.get_current_x_counts({'Sex': 'Male'})
        assert counts_before == counts_after

    def test_get_assignment_info_with_assignment(self, get_example_3to1):
        # Test with deterministic assignment so we know
        # which arm will be assigned
        minimizer = get_example_3to1(
            probability_method='best_only',
            preferred_p=1.0
        )
        counts_before = minimizer.get_current_x_counts({'Sex': 'Male'})
        assign_info = minimizer.get_assignment_info(
            {'Sex': 'Male'},
            do_assignment=True
        )
        assert assign_info['arm'] == 'Treat2'
        assert assign_info['prob'] == 1.0
        assert assign_info['most_favoured']
        counts_after = minimizer.get_current_x_counts({'Sex': 'Male'})
        treat2_before = counts_before['Sex']['Treat2']
        treat2_after = counts_after['Sex']['Treat2']
        assert treat2_after == treat2_before + 1

    def test_reset_counts_to_zero(self, get_simple_minimizer):
        minimizer = get_simple_minimizer()
        before_assignment = copy.deepcopy(minimizer._count_table)
        ppts = ([{'Sex': 'Male'} for i in range(5)] +
                [{'Sex': 'Female'} for i in range(5)])
        for ppt in ppts:
            minimizer.assign_participant(ppt)

        minimizer.reset_counts_to_zero()
        after_reset = minimizer._count_table

        assert before_assignment == after_reset

    def test_invalid_total_imbalance_method(self, factor_age, factor_sex,
                                            arm_one, arm_two):
        with pytest.raises(
                ValueError,
                message="Imbalance method should be 'sum' or 'weighted_sum'"):
            minimizer = Minimizer(
                [factor_age, factor_sex],
                [arm_one, arm_two],
                total_imbalance_method='waited_some'
            )

    def test_biased_coin_warning(self, get_simple_minimizer, capsys):
        min = get_simple_minimizer(
            arms=[Arm('A', 1), Arm('B', 2)],
            probability_method='best_only'
        )
        captured = capsys.readouterr()
        assert "NOTE: 'biased_coin' may give better results" in captured.out

    def test_probability_method_args(self, get_simple_minimizer, capsys):
        get_simple_minimizer(probability_method='rank_all')
        captured = capsys.readouterr()
        assert "q argument was not provided" in captured.out

    def test_ps1975_examples(self, example_table_one):
        """
        Test calculation of imbalance as reported in section 3.4
        of PS1975
        """
        minimizer = example_table_one
        # New example participant as in PS1975
        new_participant = {'Factor1': 'level1', 'Factor2': 'level2',
                           'Factor3': 'level2'}

        imbalance_scores = minimizer.get_new_total_imbalances(new_participant)
        assert imbalance_scores['Arm1'] == 6
        assert imbalance_scores['Arm2'] == 10
        assert imbalance_scores['Arm3'] == 5

        arm_probs = minimizer.get_arm_probability(imbalance_scores)
        assert pytest.approx(arm_probs['Arm3'], 2 / 3)
        assert pytest.approx(arm_probs['Arm1'], 1 / 6)
        assert pytest.approx(arm_probs['Arm2'], 1 / 6)
