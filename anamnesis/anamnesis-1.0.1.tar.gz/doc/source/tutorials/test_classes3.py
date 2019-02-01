#!/usr/bin/python3

from anamnesis import AbstractAnam, AnamCollection, register_class


class CollectableSubjectStats(AbstractAnam):

    hdf5_outputs = ['zstats', 'rts']

    hdf5_defaultgroup = 'subjectstats'

    def __init__(self, zstats=None, rts=None):
        """
        zstats must be a numpy array of [width, height] dimensions
        rts must be a numpy array of [ntrials, ] dimensions
        """
        AbstractAnam.__init__(self)

        self.zstats = zstats
        self.rts = rts


register_class(CollectableSubjectStats)


class StatsCollection(AnamCollection):
    anam_combine = ['zstats', 'rts']


register_class(StatsCollection)
