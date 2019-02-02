import csv

import pytest

from smallerize.smallerize import (
    Arm, Factor, Minimizer,
)
from smallerize.simulate import SimulatedTrial


@pytest.fixture
def example_table_one():
    """
    Recreate Table 1 from PS1975, and create a Minimizer that matches
    the example from the article. The exact factor combinations
    are not reported in the original article but matching ones
    were created by simulation and are listed in the csv file.
    """
    factors = [
        Factor('Factor1', levels=['level1', 'level2'], weight=2.0),
        Factor('Factor2', levels=['level1', 'level2'], weight=1.0),
        Factor('Factor3', levels=['level1', 'level2', 'level3'],
               weight=1.0)
    ]
    arms = [Arm('Arm1'), Arm('Arm2'), Arm('Arm3')]
    minimizer = Minimizer(
        factors=factors,
        arms=arms,
        d_imbalance_method='range',
        total_imbalance_method='weighted_sum',
        probability_method='best_only',
        preferred_p=2 / 3
    )

    with open('tests/ps1975_table1_participants.csv') as file_in:
        csv_in = csv.DictReader(file_in)
        t1_participant_counts = [row for row in csv_in]

    for participant_info in t1_participant_counts:
        arm = participant_info.pop('Arm')
        count = int(participant_info.pop('Count'))
        for ppt_num in range(count):
            ppt = participant_info.copy()
            minimizer.add_existing_participant(ppt, arm=arm)

    return minimizer


@pytest.fixture
def factor_age():
    name = 'Age'
    levels = ['10-20', '20-30', '30+']
    factor = Factor(name=name, levels=levels)
    return factor


@pytest.fixture
def factor_sex():
    return Factor('Sex', ['Male', 'Female'])


@pytest.fixture
def arm_one():
    return Arm('Treat1')


@pytest.fixture
def arm_two():
    return Arm('Treat2')


@pytest.fixture
def example_male_age_participants():
    """
    20 existing male participants, equal numbers of males in each arm,
    different numbers of '10-20' and '20-30' participants in each arm
    """
    participants = []
    for i in range(6):
        participants.append({'Sex': 'Male', 'Age': '10-20', 'Arm': 'Treat1'})
    for i in range(4):
        participants.append({'Sex': 'Male', 'Age': '10-20', 'Arm': 'Treat2'})
    for i in range(4):
        participants.append({'Sex': 'Male', 'Age': '20-30', 'Arm': 'Treat1'})
    for i in range(6):
        participants.append({'Sex': 'Male', 'Age': '20-30', 'Arm': 'Treat2'})
    return participants


@pytest.fixture
def get_simple_minimizer(factor_sex, arm_one, arm_two):
    # Allow overriding the default factors and arms
    #   when needed with kwargs
    def _create_minimizer(**kwargs):
        factors = kwargs.pop('factors', [factor_sex])
        arms = kwargs.pop('arms', [arm_one, arm_two])
        return Minimizer(
            factors=factors,
            arms=arms,
            **kwargs
        )

    return _create_minimizer


@pytest.fixture
def get_example_3to1(get_simple_minimizer):

    def _create_data(**kwargs):
        minimizer = get_simple_minimizer(**kwargs)
        example_ppts = [
            {'Sex': 'Male', 'Arm': 'Treat1'},
            {'Sex': 'Male', 'Arm': 'Treat1'},
            {'Sex': 'Male', 'Arm': 'Treat1'},
            {'Sex': 'Male', 'Arm': 'Treat2'}
        ]
        for ppt in example_ppts:
            arm = ppt.pop('Arm')
            minimizer.add_existing_participant(ppt, arm)
        return minimizer

    return _create_data


@pytest.fixture
def get_simple_simulated_trial(get_simple_minimizer, factor_sex):
    def _create_simulated_trial(minimizers=None, factors=None):
        default_minimizers = {
            'range': get_simple_minimizer(d_imbalance_method='range'),
            'std_dev': get_simple_minimizer(
                d_imbalance_method='standard_deviation'
            )
        }
        if minimizers is None:
            minimizers = default_minimizers
        if factors is None:
            factors = [factor_sex]
        return SimulatedTrial(minimizers=minimizers, factors=factors)

    return _create_simulated_trial
