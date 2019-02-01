#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

__all__ = []


class NullMPIImplementor(object):
    """
    Singleton fake MPI Class which doesn't even depend on the MPI module being
    available
    """

    __shared_state = {}

    def __init__(self, *args, **kwargs):
        # Quick way of implementing a singleton
        self.__dict__ = self.__shared_state

        if not getattr(self, 'initialised', False):
            self.initialised = True
            self.setup(*args, **kwargs)

    def setup(self, use_mpi=False):
        self.rank = 0
        self.size = 1
        self.master = True

    def recv(self, obj=None, source=0, tag=0, status=None):
        return obj

    def send(self, obj=None, dest=0, tag=0):
        return obj

    def bcast(self, data_in=None, root=0):
        return data_in

    def get_scatter_indices(self, num_pts):
        return [(0, num_pts,)]

    def scatter_array(self, data_in=None, root=0):
        return data_in

    def scatter_list(self, data_in=None, root=0):
        return data_in

    def gather(self, data_in, root=0):
        return data_in

    def allgather(self, data_in, root=0):
        return data_in

    def gather_list(self, data_in, total_trials, return_all=False):
        return data_in

    def abort(self):
        return


__all__.append('NullMPIImplementor')
