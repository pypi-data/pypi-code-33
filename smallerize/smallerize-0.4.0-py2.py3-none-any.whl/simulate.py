import typing

from .smallerize import Minimizer, Factor


class SimulatedTrial:

    def __init__(self,
                 minimizers: typing.Dict[str, Minimizer],
                 factors: typing.List[Factor]):
        self.minimizers = minimizers
        self.factors = {factor.name: factor for factor in factors}

    def create_random_participants(self, n: int):
        random_levels = {}
        for factor_name, factor in self.factors.items():
            random_levels[factor_name] = factor.get_random_level_multiple(n)

        participants = []
        for participant_num in range(n):
            factor_levels = {
                factor_name: random_levels[factor_name][participant_num]
                for factor_name in self.factors
            }
            participants.append(factor_levels)

        return participants

    def assign_one(self, factor_levels: dict) -> dict:
        result = {}
        for name, minimizer in self.minimizers.items():
            assign_info = minimizer.get_assignment_info(factor_levels)
            minimizer._add_participant_to_arm(factor_levels,
                                              assign_info['arm'])
            assign_info.update(factor_levels)
            result[name] = assign_info
        return result

    def simulate(self, n_trials: int):
        participants = self.create_random_participants(n_trials)
        results = {minimizer_name: [] for minimizer_name in self.minimizers}
        for ppt in participants:
            assignment = self.assign_one(ppt)
            for minimizer_name in self.minimizers:
                results[minimizer_name].append(assignment[minimizer_name])
        return results
