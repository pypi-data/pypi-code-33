__all__ = ['Factor', 'Arm', 'Minimizer']

import collections
import itertools
import random
import statistics
import typing

from .utils import (
    _dict_add_inplace,
    _dict_div_inplace,
    _dict_product_inplace
)


class Factor:
    """
    A prognostic factor with 2 or more levels, that needs to be balanced
    between treatment arms.
    """

    def __init__(self, name: str,
                 levels: typing.Iterable[str],
                 weight: float = 1.0):
        """
        :param name: Name/label for the factor
        :type name: str
        :param levels: List of categorical levels for the factor
        :param weight: Optional weight, used if the total imbalance in the
        minimization algorithm is a weighted sum that weighs each factor
        differently.
        :type weight: float
        """
        self.name = name

        self.levels = tuple(levels)
        if not len(self.levels) >= 2:
            raise ValueError("Factors must have 2 or more levels")

        if not weight > 0:
            raise ValueError("Factor weight must be a positive number")
        self.weight = weight

    def __str__(self):
        return "Factor({f.name}, levels={f.levels})".format(f=self)

    def __repr__(self):
        return str(self)

    def get_random_level(self) -> str:
        """
        Return one of the factor's levels at random (all levels have
        equal probability).

        :return: Name of the chosen level
        :rtype: str
        """
        return random.choice(self.levels)

    def get_random_level_multiple(self, n) -> typing.List[str]:
        """
        Return n random levels, sampled with replacement. Faster than calling
        get_random_level multiple times.

        :param n: Number of random levels to generate.
        :return: List of level names.
        """
        return random.choices(self.levels, k=n)


class Arm:
    """
    A treatment arm that participants will be assigned to. Different
    arms in the trial may have different allocation ratios, e.g.
    1:2:1 for arms A, B and C.
    """

    def __init__(self, name: str, allocation_ratio: int = 1):
        self.name = name
        if not (type(allocation_ratio) == int):
            raise ValueError("Allocation ratio must be an integer.")
        self.allocation_ratio = allocation_ratio

    def __str__(self):
        return "Arm({a.name}, allocation_ratio={a.allocation_ratio})".format(
            a=self
        )


def _get_imbalance_std_dev(arm_x_counts: dict) -> float:
    """
    Calculate the imbalance between arms using standard deviation.
    """
    return statistics.stdev(arm_x_counts.values())


def _get_imbalance_variance(arm_x_counts: dict) -> float:
    """
    Calculate the imbalance between arms using variance.
    """
    return statistics.variance(arm_x_counts.values())


def _get_imbalance_range(arm_x_counts: dict) -> float:
    """
    Calculate the imbalance between arms using the range.
    """
    counts = list(arm_x_counts.values())
    return max(counts) - min(counts)


def _get_imbalance_over_max_range(arm_x_counts: dict, max_range: int) -> int:
    """
    Calculate whether the imbalance between arms exceeds the
    ``max_range`` threshold.

    :return: 1 if the range exceeds ``max_range``, 0 otherwise.
    """
    counts = list(arm_x_counts.values())
    count_range = max(counts) - min(counts)
    return int(count_range > max_range)


def _get_imbalance_is_largest(arm_x_counts: dict, current_arm: str) -> int:
    """
    Calculate whether ``current_arm`` has the greatest count.

    :param current_arm: Name of current arm.
    :return: 1 if ``current_arm`` has the most participants assigned,
    0 otherwise.
    """
    max_count = max(arm_x_counts.values())
    has_two_counts = len(set(arm_x_counts.values())) == 2
    current_arm_is_largest = (
            (arm_x_counts[current_arm] == max_count) and
            has_two_counts
    )
    return int(current_arm_is_largest)


def _get_imbalance_marginal_balance(arm_x_counts: dict) -> float:
    """
    Marginal balance, as outlined in Han2009.

    :return: score between 0 and 1, higher score reflecting higher
      total imbalance.
    """
    N = len(arm_x_counts)
    denom = (N - 1) * sum(arm_x_counts.values())

    all_pairs = itertools.combinations(arm_x_counts.keys(), 2)
    num = sum(abs(arm_x_counts[arm_i] - arm_x_counts[arm_j])
              for arm_i, arm_j in all_pairs)

    return num / denom


class Minimizer:
    """
    Given a set of prognostic factors and treatment arms, assigns
    participants to arms based on the minimization algorithm
    (or purely random assignment for comparison).
    """
    D_IMBALANCE_METHODS = {
        'standard_deviation': _get_imbalance_std_dev,
        'variance': _get_imbalance_variance,
        'range': _get_imbalance_range,
        'over_max_range': _get_imbalance_over_max_range,
        'is_largest': _get_imbalance_is_largest,
        'marginal_balance': _get_imbalance_marginal_balance
    }
    TOTAL_IMBALANCE_METHODS = ['sum', 'weighted_sum']
    PROBABILITY_METHODS = ['best_only', 'rank_all', 'pure_random',
                           'biased_coin']

    def __init__(self,
                 factors: typing.Iterable[Factor],
                 arms: typing.Iterable[Arm],
                 d_imbalance_method: str = 'standard_deviation',
                 total_imbalance_method: str = 'sum',
                 probability_method: str = 'best_only',
                 **method_args):
        """
        :param factors: List of prognostic factors to be considered during
        assignment.
        :param arms: List of treatment arms to assign participants
        to (possibly with unequal ratios).
        :param d_imbalance_calculator: Function used to score the
        amount of imbalance, e.g. standard deviation. Must be one
        of the methods in ``Minimizer.D_IMBALANCE_METHODS``.
        :param total_imbalance_method: 'sum' (the default), or 'weighted_sum',
        depending on whether all factors should be weighted equally.
        :param probability_method: Method for assigning probabilities
        to the arms, based on the imbalance that would result. See
        :ref:`trial_setup` for details.
        :param method_args: Additional arguments required by some
        imbalance and probability methods.
        """
        # TODO: Document what all the additional method_args are.
        # Check if we only have a single Factor
        if isinstance(factors, Factor):
            factors = [factors]
        self.factors = list(factors)
        self.arms = list(arms)

        self._d_imbalance_method = self._check_d_imbalance_method(
            d_imbalance_method,
            method_args
        )

        self._total_imbalance_method = self._get_total_imbalance_method(
            total_imbalance_method
        )

        self._probability_method = self._check_probability_method(
            probability_method,
            method_args
        )

        self._count_table = self._create_count_table()
        self._arm_ratios = self._create_ratios()

    @property
    def factor_names(self):
        return [f.name for f in self.factors]

    @property
    def factor_weights(self):
        return {f.name: f.weight for f in self.factors}

    @property
    def arm_names(self):
        return [a.name for a in self.arms]

    def get_n(self) -> int:
        """
        Get the number of arms for the trial.
        """
        return len(self.arms)

    def _check_d_imbalance_method(self, method: str, method_args: dict):
        """
        Check that the supplied imbalance method is valid
        (and any required arguments have been supplied).
        """
        if method not in self.D_IMBALANCE_METHODS:
            raise ValueError(
                "Invalid d_imbalance_method. "
                "See Minimizer.D_IMBALANCE_METHODS for available methods."
            )

        if method == 'is_largest':
            if self.get_n() > 2:
                raise ValueError(
                    "Can't use 'is_largest' with more than 2 arms."
                )

        if method == 'over_max_range':
            d_max_range = method_args.get('d_max_range')
            if d_max_range is None:
                raise ValueError(
                    "If using 'over_max_range', you must supply an"
                    " additional argument d_max_range")
            self._d_max_range = d_max_range

        return method

    def _check_probability_method(self, method: str, method_args: dict) -> str:
        """
        Check that the supplied probability method is valid and
        any required arguments have been provided.
        """
        valid_methods = self.PROBABILITY_METHODS
        if method not in valid_methods:
            raise ValueError(
                ("Probability method must be one of {methods}" +
                 ", {m} given").format(
                    methods=valid_methods,
                    m=method
                )
            )

        # Print a warning when unequal allocation ratios are used
        #   and biased_coin isn't
        if method != 'biased_coin':
            ratios = list(self._create_ratios().values())
            all_equal = all(r == ratios[0] for r in ratios)
            if not all_equal:
                warn_message = (
                    ("NOTE: 'biased_coin' may give better results than {m}") +
                    (" when allocation ratios are unequal.").format(
                        m=method
                    )
                )
                print(warn_message)

        if method in ('best_only', 'biased_coin'):
            # Use midpoint between 1 and 1 / N by default
            default_p = (1 + 1 / self.get_n()) / 2
            if 'preferred_p' not in method_args:
                print("preferred_p argument was not provided. Using default"
                      " value of {p}".format(p=default_p))
            preferred_p = method_args.get('preferred_p', default_p)

            p_valid = (
                    (preferred_p > (1 / self.get_n())) and
                    (preferred_p <= 1.0)
            )
            if not p_valid:
                raise ValueError(
                    "preferred_p must be between (1 / N) and 1"
                )

            self._preferred_p = preferred_p

        elif method == 'rank_all':
            N = self.get_n()
            # Use halfway point between boundaries as a default
            default_q = (
                ((1 / N) + (2 / (N - 1))) / 2
            )
            q = method_args.get('q', default_q)
            if 'q' not in method_args:
                print("q argument was not provided. Using default"
                      " value of {q}".format(q=default_q))

            q_valid = (q > (1 / N)) and (q < (2 / (N - 1)))
            if not q_valid:
                raise ValueError(
                    "q must be between 1 / N and 2 / (N - 1)"
                )

            self._q = q

        return method

    def _get_total_imbalance_method(self, method: str):
        """
        Check that the method given is a valid choice.
        """
        valid_methods = self.TOTAL_IMBALANCE_METHODS
        if method not in valid_methods:
            raise ValueError(
                "Imbalance method should be one of: " +
                str(valid_methods)
            )
        return method

    def _create_ratios(self) -> dict:
        """
        Store the allocation ratios for each treatment arm in a dictionary
        so we can divide/multiply by them easily.

        :return: dict that maps from arm name to allocation ratio
        """
        return {a.name: a.allocation_ratio for a in self.arms}

    def _create_count_table(self) -> dict:
        """
        Set up the dictionary that will count how many participants have been
        assigned to each combination of factor levels and treatment arms.

        The keys are tuples, with length equal to the number of factor
        levels. The values are dictionaries that map from arm name to
        the count within that combination of factor levels.

        So if the factors are Sex, Age and Disease Severity, an entry
        in the count table might be:

        count_table[('Male', '40+', 'Mild')] -> {'Arm1': 5, 'Arm2': 4}

        This way, each participant is only represented in a single entry
        in the count table. Accessing the required counts is also
        relatively straightforward, e.g. if Sex is the second factor
        in the trial, you can find all keys where factor_key[1] == 'Male'.

        :return: Nested dictionary. Outer keys are factor level tuples,
        keys for the inner dictionaries are arm names, and values
        for the inner dictionary are the number of participants assigned
        to each arm within that combination of factor levels.
        """
        # Create inner dicts fresh each time to make sure we
        #   don't hit any problems with mutability
        #   (think doing it within the comprehension would be OK
        #   though)
        def _create_empty_arms() -> dict:
            return {a: 0 for a in self.arm_names}

        all_keys = itertools.product(*(f.levels for f in self.factors))
        count_table = {factor_key: _create_empty_arms()
                       for factor_key in all_keys}
        return count_table

    def add_existing_participant(self, factor_levels: dict, arm: str) -> None:
        """
        Add a participant who has already been assigned to the trial to
        the count table. Modifies the count table in place.

        :param factor_levels: A dictionary where the keys are the names
           of the factors in the trial, and the values are the factor
           levels for the participant.
        :param arm: Name of the arm they are assigned to.
        """
        self._add_participant_to_arm(factor_levels, arm)

    def _add_participant_to_arm(self, factor_levels: dict, arm: str) -> None:
        """
        Add a participant with the given factor levels to ``arm``.
        Modify the count table inplace.
        """
        # Convert factor_levels to ordered tuple that matches the
        #   keys of the count table
        participant_index = tuple(
            factor_levels[factor] for factor in self.factor_names
        )
        self._count_table[participant_index][arm] += 1

    @staticmethod
    def _get_chosen_arm(arm_probs: dict) -> str:
        """
        Return a randomly chosen arm, weighted by the probabilities
        in ``arm_probs``

        :param arm_probs: dict giving the probability of assignment
          for each arm.
        """
        choice = random.choices(list(arm_probs.keys()),
                                weights=list(arm_probs.values()),
                                k=1)
        # random.choices returns a list so grab
        #   first element
        return choice[0]

    def assign_participant(self, factor_levels: dict) -> str:
        """
        Assign a new participant to the trial, using the
        minimization algorithm. Modifies the count table in place,
        and returns the chosen arm.

        :param factor_levels: A dictionary that maps from factor
          names to participants.
        :type factor_levels: dict
        :return: Name of chosen arm
        :rtype: str
        """
        # Special case: avoid calculating imbalances when
        #    doing pure_random assignment
        if self._probability_method == 'pure_random':
            arm_probs = self._get_arm_probability_pure_random()
        else:
            imbalances = self.get_new_total_imbalances(factor_levels)
            arm_probs = self.get_arm_probability(imbalances)
        arm = self._get_chosen_arm(arm_probs)
        self._add_participant_to_arm(factor_levels, arm)
        return arm

    def get_assignment_info(self, factor_levels: dict,
                            do_assignment: bool = False) -> dict:
        """
        Alternative to assign_participant(), takes factor levels
        for a new participant, chooses an arm,  and returns the arm along
        with extra details about whether the most-favoured arm was chosen.
        By default, the participant is not actually assigned. To
        assign the participant at the same time, set
        ``do_assignment=True``.

        :return: dict with keys: ``'arm'``: chosen arm, ``'prob'``:
          probability that was assigned to that arm before the selection,
          ``'most_favoured'``: Whether the chosen arm was the arm
          with the highest probability (including if it was tied for
          highest probability).
        """
        # Special case: avoid calculating imbalances when
        #    doing pure_random assignment
        if self._probability_method == 'pure_random':
            arm_probs = self._get_arm_probability_pure_random()
        else:
            imbalances = self.get_new_total_imbalances(factor_levels)
            arm_probs = self.get_arm_probability(imbalances)
        arm = self._get_chosen_arm(arm_probs)

        if do_assignment:
            self._add_participant_to_arm(factor_levels, arm)

        return {'arm': arm,
                # Probability of the chosen arm
                'prob': arm_probs[arm],
                'most_favoured': arm_probs[arm] == max(arm_probs.values())}

    def _get_arm_probability_pure_random(self):
        # Need to account for allocation ratio
        total = sum(self._arm_ratios.values())
        ps = {a: self._arm_ratios[a] / total
              for a in self.arm_names}
        return ps

    def _get_arm_probability_biased_coin(self, ranked_arms: list):
        allocation_order = sorted(
            self.arm_names, key=lambda a: self._arm_ratios[a]
        )
        smallest_arm = allocation_order[0]

        preferred_arm = ranked_arms[0]
        preferred_num = sum(ratio for arm, ratio in self._arm_ratios.items()
                            if arm != preferred_arm)
        preferred_denom = sum(ratio for arm, ratio in self._arm_ratios.items()
                              if arm != smallest_arm)
        preferred_p = (
                1 - (preferred_num / preferred_denom) * (1 - self._preferred_p)
        )

        arm_probs = [preferred_p]
        for other_arm in ranked_arms[1:]:
            other_num = self._arm_ratios[other_arm]
            other_denom = sum(ratio for arm, ratio in self._arm_ratios.items()
                              if arm != preferred_arm)
            other_p = (other_num / other_denom) * (1 - preferred_p)
            arm_probs.append(other_p)

        return arm_probs

    def get_arm_probability(
            self,
            imbalances: dict) -> dict:
        """
        Calculate the probability assigned to each arm, based
        on the current imbalances and the chosen
        probability method.
        """
        # Don't need to do any imbalance calculations
        #   if doing purely random assignment
        if self._probability_method == 'pure_random':
            return self._get_arm_probability_pure_random()

        # All other methods depend on imbalance scores
        ranked_arms = self._rank_imbalances(imbalances)

        if self._probability_method == 'best_only':
            p1 = self._preferred_p
            N = len(self.arms)
            other_p = (1 - p1) / (N - 1)
            ps = [p1] + [other_p] * (N - 1)

        elif self._probability_method == 'rank_all':
            q = self._q
            N = len(self.arms)

            num = 2 * (N * q - 1)
            denom = N * (N + 1)
            ks = range(1, N + 1)
            ps = [q - (num / denom) * k
                  for k in ks]

        elif self._probability_method == 'biased_coin':
            ps = self._get_arm_probability_biased_coin(ranked_arms)

        return dict(zip(ranked_arms, ps))

    @staticmethod
    def _rank_imbalances(imbalances: dict) -> list:
        """
        In the Pocock + Simon method, treatments are ranked according to their
        total imbalance (in ascending order). When two treatments tie,
        they are ranked in random order.

        :param imbalances: A dictionary that maps from arm names to imbalance
        scores.
        :return: List of treatment names, in ranked order.
        """

        def _shuffle_list_slice(lst, start, end) -> None:
            """
            Shuffle the elements of lst[start:end] inplace.
            """
            lst[start:end] = random.sample(
                lst[start:end],
                len(lst[start:end])
            )

        ranked = sorted(
            imbalances.keys(),
            key=lambda a: imbalances[a]
        )

        # Break ties randomly by shuffling them, as suggested
        # in PS1975
        start_index = 0
        groups = itertools.groupby(
            ranked,
            key=lambda a: imbalances[a]
        )
        for val, group in groups:
            group_size = len(list(group))
            if group_size > 1:
                _shuffle_list_slice(ranked, start_index,
                                    start_index + group_size)
            start_index += group_size

        return ranked

    def get_new_total_imbalances(
            self,
            factor_levels: dict) -> \
            typing.Dict[str, typing.Union[int, float]]:
        """
        Get the total imbalance scores that would result from assigning
        a participant with the given factor levels to each arm.

        :param factor_levels: Maps from factor names to the participant's
          level for each factor.
        :type factor_levels: dict
        :return: Total imbalance score for each potential arm.
        :rtype: dict
        """
        d_imbalance_scores = self.get_new_ds(factor_levels)

        total_imbalances = {}

        for potential_arm in self.arm_names:
            current_d_scores = d_imbalance_scores[potential_arm]

            if self._total_imbalance_method == 'weighted_sum':
                _dict_product_inplace(current_d_scores, self.factor_weights)

            total_imbalances[potential_arm] = sum(current_d_scores.values())

        return total_imbalances

    def get_all_new_counts(
            self,
            factor_levels: dict) -> typing.Dict[str, dict]:
        """
        For each potential arm that a new participant could be assigned
        to, calculate the number of participants that would be in each arm
        if the potential arm was chosen, within each factor level that the
        new participant belongs to.

        :param factor_levels: A dictionary that maps from factor names to
           factor levels, giving the participant's factor levels for each
           factor used in the trial.
        :type factor_levels: dict
        :return: A nested dictionary, that maps from (potential arm) ->
          (factor name) -> dict of arm counts within that factor
        """
        # NOTE: this takes into account the allocation ratios
        # (divides each raw count by its ratio)
        current_factor_counts = self.get_current_x_counts(factor_levels)

        # Potential counts, if assigned to that arm
        p_counts = collections.defaultdict(dict)
        for potential_treatment in self.arm_names:
            for i_factor in self.factor_names:
                count_within_factor = self._get_count_after_assignment(
                    arm_counts=current_factor_counts[i_factor],
                    arm_name=potential_treatment
                )
                p_counts[potential_treatment][i_factor] = count_within_factor

        return p_counts

    def get_new_ds(self, factor_levels: dict) -> \
            typing.Dict[str, dict]:
        """
        Calculate the d_ik scores, the imbalance score within each factor,
        for each potential arm that a new participant could be assigned to.

        :param factor_levels: A dict that maps from (factor name) ->
          (new participant's factor level)
        :return: A dict that maps from (potential arm) -> (dict of scores
          for each factor)
        """
        get_imbalance = self.D_IMBALANCE_METHODS[self._d_imbalance_method]

        counts_after_assignment = self.get_all_new_counts(factor_levels)

        arm_ds = {}

        for potential_arm in self.arm_names:
            factor_scores = []
            for i_factor in self.factor_names:
                arm_counts = counts_after_assignment[potential_arm][i_factor]

                # Some imbalance methods need special cases, the rest just
                #  need the counts
                if self._d_imbalance_method == 'is_largest':
                    imbalance_score = get_imbalance(
                        arm_counts,
                        current_arm=potential_arm
                    )
                elif self._d_imbalance_method == 'over_max_range':
                    imbalance_score = get_imbalance(
                        arm_counts,
                        max_range=self._d_max_range
                    )
                else:
                    imbalance_score = get_imbalance(arm_counts)

                factor_scores.append(imbalance_score)

            # NOTE: this may not be necessary, since factor scores should
            #   always be in factor order
            arm_ds[potential_arm] = dict(zip(self.factor_names, factor_scores))

        return arm_ds

    def get_current_x_counts(
            self,
            factor_levels: dict) -> typing.Dict[str, dict]:
        """
        Return the current x_ijk (arm counts within each factor), when
        considering a participant with the given ``factor_levels``.

        :param factor_levels: A dictionary that maps from factor names to
           factor levels, giving the participant's factor levels for each
           factor used in the trial.
        :type factor_levels: dict
        :return:
        """
        if not all(f in factor_levels for f in self.factor_names):
            raise ValueError("All factors in the trial must be "
                             "in factor_levels.")

        factor_x_counts = {}
        for i_factor, j_level in factor_levels.items():
            current_index = self.factor_names.index(i_factor)

            current_x_ijk = {a: 0 for a in self.arm_names}
            for factor_key in self._count_table:
                if factor_key[current_index] == j_level:
                    _dict_add_inplace(current_x_ijk,
                                      self._count_table[factor_key])
            # Divide by allocation ratios to get weighted counts
            #   (has no effect when ratios are all 1)
            _dict_div_inplace(current_x_ijk, self._arm_ratios)

            factor_x_counts[i_factor] = current_x_ijk

        return factor_x_counts

    def _get_count_after_assignment(self, arm_counts: dict,
                                    arm_name: str) -> dict:
        """
        Take the current x_ijk (arm_counts), and return the count
        after assigning to a potential treatment (arm_name).
        """
        new_counts = arm_counts.copy()
        new_counts[arm_name] += 1
        return new_counts

    def reset_counts_to_zero(self):
        """
        Reset the counts of assigned participants to zero, i.e.
        starting over as if no participants had been assigned.
        """
        self._count_table = self._create_count_table()
