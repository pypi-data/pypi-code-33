import scipy.stats

from abc import ABCMeta, abstractmethod

from crimjustsimpy import Case


class Trial:

    def try_case(self, case:Case):
        assert not case.plead
        assert not case.tried
        assert not case.acquitted
        assert not case.convicted
        assert not case.guilty

        # Random trial outcome based on probability of a conviction.
        draw = scipy.stats.uniform.rvs()
        if draw < case.prob_convict:
            case.convicted = True
            case.guilty = True
            case.sentence = case.sentence_if_convicted
        else:
            case.acquitted = True
            case.sentence = 0

        case.tried = True
