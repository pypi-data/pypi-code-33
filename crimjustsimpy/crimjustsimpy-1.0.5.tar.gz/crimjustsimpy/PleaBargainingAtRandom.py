import scipy.stats
from crimjustsimpy import Case, Docket, PleaBargainingStrategy


class PleaBargainingAtRandom(PleaBargainingStrategy):
    """
    Simple dumb plea bargaining, independent cases with random probability of pleading.
    """

    def __init__(self,*,prob_plea:float):
        self.prob_plea = prob_plea

    def _handle_case(self, case:Case):
        """
        Handle a single case.
        :param case:
        :return:
        """
        assert not case.plead
        assert not case.tried
        assert not case.acquitted
        assert not case.convicted
        assert not case.guilty

        # Random choice of whether a plea happens.
        draw = scipy.stats.uniform.rvs()
        if draw < self.prob_plea:
            case.plead = True
            case.guilty = True

            # The statistically expected sentence.
            case.sentence = case.prob_convict * case.sentence_if_convicted

    def bargain(self, docket:Docket):
        """
        Calculate plea bargains.
        :param docket:
        :return:
        """
        assert isinstance(docket,Docket)

        # For this dumb strategy, handle the cases independently.
        for case in docket.cases:
            self._handle_case(case)

