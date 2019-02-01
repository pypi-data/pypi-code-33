#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import sys

from numpy.random import randn

from .options import AnamOptions

__all__ = []


class MPIHandler(object):
    __shared_state = {}

    def __init__(self, *args, **kwargs):
        # Quick way of implementing a singleton
        self.__dict__ = self.__shared_state

        if not getattr(self, 'initialised', False):
            self.initialised = True
            self._done = False
            self.setup(*args, **kwargs)

            # Register a cleanup routine
            import atexit
            atexit.register(self.atexit_handler)

    def setup(self, use_mpi=False):
        if use_mpi:
            from .mpiimps.mpifourpy import MPI4PyImplementor
            self.handler = MPI4PyImplementor()
        else:
            from .mpiimps.null import NullMPIImplementor
            self.handler = NullMPIImplementor()

        self.output_file = sys.stdout

    def write(self, s):
        """
        Write progress information to the appropriate output file

        :param s: String to write
        :type s: str
        """
        if AnamOptions().verbose:
            self.output_file.write(s)
        self.output_file.flush()

    def write_progress(self, s):
        """
        Write progress information to the appropriate output file but only on
        the root MPI node and only if the progress option is set

        :param s: String to write
        :type s: str
        """
        if self.rank == 0 and AnamOptions().progress:
            self.output_file.write(s)
            self.output_file.flush()

    def write_root(self, s):
        """
        Write progress information to the appropriate output file but only on
        the root MPI node

        :param s: String to write
        :type s: str
        """
        if self.rank == 0:
            self.write(s)

    def get_rank(self):
        return self.handler.rank

    rank = property(get_rank)

    def get_size(self):
        return self.handler.size

    size = property(get_size)

    def get_master(self):
        return self.handler.master

    master = property(get_master)

    def recv(self, obj=None, source=0, tag=0, status=None):
        return self.handler.recv(obj, source, tag, status)

    def send(self, obj=None, dest=0, tag=0):
        return self.handler.send(obj, dest, tag)

    def bcast(self, data_in=None, root=0):
        return self.handler.bcast(data_in, root)

    def get_scatter_indices(self, num_pts):
        """
        Return a list of indices which would be used for scattering num_pts
        across the nodes
        """
        return self.handler.get_scatter_indices(num_pts)

    def scatter_array(self, data_in=None, root=0):
        return self.handler.scatter_array(data_in, root)

    def scatter_list(self, data_in=None, root=0):
        return self.handler.scatter_list(data_in, root)

    def gather(self, data_in, root=0):
        return self.handler.gather(data_in, root)

    def allgather(self, data_in, root=0):
        return self.handler.allgather(data_in, root)

    def gather_list(self, data_in, total_trials, return_all=False):
        return self.handler.gather_list(data_in, total_trials, return_all)

    def done(self):
        self._done = True

    def atexit_handler(self):
        if not self._done:
            self.abort()

    def abort(self):
        self.handler.abort()


__all__.append('MPIHandler')


def mpi_print(txt):
    print("NODE %s: %s" % (MPIHandler().rank, txt))


__all__.append('mpi_print')

# Some test code
if __name__ == '__main__':
    import mpi4py

    print(mpi4py.__version__)

    m = MPIHandler(use_mpi=True)

    if m.rank == 0:
        data = randn(471, 100)
    else:
        data = None

    data = m.scatter_array(data)

    print("NODE %s, %s" % (m.rank, data.shape))

    final = m.gather(data)

    if final is not None:
        print("GATHER NODE %s, %s" % (m.rank, final.shape))
    else:
        print("GATHER NODE %s NONE" % (m.rank))

    finalall = m.allgather(data)
    print("ALLGATHER NODE %s, %s" % (m.rank, finalall.shape))

    m.done()
