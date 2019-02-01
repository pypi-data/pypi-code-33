#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

from numpy import array, arange, empty, dtype, prod
from numpy import string_ as npstring

from mpi4py import MPI

from ..register import find_class

__all__ = []

# This shouldn't be needed in mpi4py >= 1.2
MPI_TYPE = {dtype('int16'): MPI.SHORT,
            dtype('int32'): MPI.INT,
            dtype('int64'): MPI.LONG,
            dtype('float32'): MPI.FLOAT,
            dtype('float64'): MPI.DOUBLE}


# Quite a lot of this class may well be unnecessary with newer versions of
# mpi4py If it is necessary, we should try and get the changes (e.g. array
# scatter / gather) upstream
class MPI4PyImplementor(object):
    __shared_state = {}

    def __init__(self, *args, **kwargs):
        # Quick way of implementing a singleton
        self.__dict__ = self.__shared_state

        if not getattr(self, 'initialised', False):
            self.initialised = True
            self.setup(*args, **kwargs)

    def setup(self):
        self.mpi = MPI.COMM_WORLD
        self.rank = self.mpi.Get_rank()
        self.master = (self.rank == 0)

    def get_size(self):
        return self.mpi.group.size

    size = property(get_size)

    def recv(self, obj=None, source=0, tag=0, status=None):
        # Get type
        t = self.mpi.recv(None, source=source, tag=tag, status=status)
        if t == 'ANAM':
            clsname = self.mpi.recv(None, source=source,
                                    tag=tag, status=status)
            cls = find_class(clsname)
            if cls is None:
                raise RuntimeError("Cannot find class %s during "
                                   "MPI recieve" % clsname)
            return cls.recv(source=source, tag=tag, status=status)
        elif t == 'NORMAL':
            return self.mpi.recv(None, source=source, tag=tag, status=status)
        else:
            raise Exception("Rank %d cannot understand MPI recieve type "
                            "%s, expecting ANAM or NORMAL" %
                            (self.rank, t))

    def send(self, obj=None, dest=0, tag=0):
        if hasattr(obj, 'get_hdf5name') and hasattr(obj, 'send'):
            self.mpi.send('ANAM', dest=dest, tag=tag)
            self.mpi.send(obj.get_hdf5name(), dest=dest, tag=tag)
            return obj.send(dest=dest, tag=tag)
        else:
            self.mpi.send('NORMAL', dest=dest, tag=tag)
            # Deal with numpy.string_ instances coming back from HDF5
            # This should be dealt with elsewhere in the code but
            # isn't for some reason and we're more robust in MPI
            # mode here by dealing with it
            if isinstance(obj, npstring):
                obj = str(obj)
            return self.mpi.send(obj, dest=dest, tag=tag)

    def bcast(self, data_in=None, root=0):
        if self.rank != root:
            # Get type
            t = self.mpi.bcast(None, root=root)
            if t == 'ANAM':
                clsname = self.mpi.bcast(None, root=root)
                cls = find_class(clsname)
                if cls is None:
                    raise RuntimeError("Cannot find class %s during "
                                       "MPI recieve" % clsname)
                return cls.bcast_recv(root=root)
            elif t == 'NORMAL':
                return self.mpi.bcast(None, root=root)
            else:
                raise Exception("Rank %d cannot understand MPI broadcast "
                                "type %s, expecting ANAM or NORMAL" %
                                (self.rank, t))
        else:
            if hasattr(data_in, 'get_hdf5name') and hasattr(data_in, 'bcast'):
                self.mpi.bcast('ANAM', root=root)
                self.mpi.bcast(data_in.get_hdf5name(), root=root)
                return data_in.bcast(root=root)
            else:
                self.mpi.bcast('NORMAL', root=root)
                # Deal with numpy.string_ instances coming back from HDF5
                # This should be dealt with elsewhere in the code but
                # isn't for some reason and we're more robust in MPI
                # mode here by dealing with it
                if isinstance(data_in, npstring):
                    data_in = str(data_in)
                return self.mpi.bcast(data_in, root=root)

    def abort(self):
        self.mpi.Abort()

    def get_scatter_indices(self, num_pts):
        num_nodes = self.mpi.size

        ret = []
        cur = 0
        for j in range(num_nodes):
            jump = num_pts / num_nodes
            if j < (num_pts % num_nodes):
                jump += 1

            jump = int(jump)

            ret.append((cur, cur + jump, ))

            cur += jump

        return ret

    def scatter_array(self, data_in=None, root=0):
        # Send a copy of the data metadata to every node

        if self.mpi.rank == root:
            # If the array is not contiguous, make it so
            if data_in.flags['C_CONTIGUOUS']:
                data = data_in
            else:
                data = data_in.copy()

            info = list(data.shape) + [data.dtype]
        else:
            data = None
            info = None

        info = self.mpi.bcast(info)
        data_shape = info[:-1]
        data_type = info[-1]

        # Calculate share size for this node
        p = int(data_shape[0] / self.mpi.size)
        if self.mpi.rank < (data_shape[0] % self.mpi.size):
            p += 1

        recvbuf = empty(tuple([p]+data_shape[1:]), data_type)

        if data_shape[0] % self.mpi.size == 0:
            # All nodes get exactly the same amount of data
            self.mpi.Scatter((data, MPI_TYPE[data_type]),
                             (recvbuf, MPI_TYPE[data_type]))
        else:
            # Calculate number of data elements in one 'row'
            rsz = prod(data_shape[1:]).astype(int)
            if self.mpi.rank == root:
                # share out jobs as equally as possible
                counts = array([int(data_shape[0]/self.mpi.size)]*self.mpi.size)
                counts[:data_shape[0] % self.mpi.size] += 1
                # Calculate total data elements for each node
                counts *= rsz
                counts_offset = [sum(counts[:i]) for i in range(self.mpi.size)]
            else:
                counts = []
                counts_offset = []

            self.mpi.Scatterv((data, (counts, counts_offset),
                               MPI_TYPE[data_type]),
                              (recvbuf, p*prod(data_shape[1:]),
                               MPI_TYPE[data_type]))

        return recvbuf

    def scatter_list(self, data_in=None, root=0):
        """
        Scatter a list of data between the nodes.  We do this by broadcasting
        the list and then scattering an array of indices into the list.
        """

        # Broadcast the whole list to everywhere
        data_in = self.mpi.bcast(data_in)

        # If we're the root node, we need to calculate who gets which items
        # in the list
        if self.mpi.rank == root:
            data_info = arange(len(data_in))
        else:
            data_info = None

        data_info = self.scatter_array(data_info)

        # Yuck - but this is an easy way to index into the list
        return list(array(data_in)[data_info])

    def _gather_array(self, data_in, all_gather=False, root=0):
        """
        Only gathers along zero axis.

        :param data_in: data to gather
        :param all_gather: Whether all nodes should gather all data (defaults
                           to False)
        :param root: Index of root node (defaults to 0)
        """

        # If the array is not contiguous, make it so
        if data_in.flags['C_CONTIGUOUS']:
            data = data_in
        else:
            data = data_in.copy()

        # first do a 'Gather' on size of data chunk from each node
        if all_gather:
            sz = self.mpi.allgather(data.shape[0])
        else:
            sz = self.mpi.gather(data.shape[0], root=root)

        # Fix a corner case where some nodes in the allgather operation
        # have zero data size
        data_root_shape = None
        if self.mpi.rank == root:
            data_root_shape = data.shape

        if all_gather:
            data_root_shape = self.mpi.bcast(data_root_shape)

        # Allocate space for gathered data, and indexing
        if (self.mpi.rank == root) or all_gather:
            recvbuf = empty(tuple([sum(sz)]+list(data_root_shape[1:])),
                            data.dtype)
            counts = [sz[i]*prod(data_root_shape[1:])
                      for i in range(self.mpi.size)]
            counts_offset = [sum(counts[:i]) for i in range(self.mpi.size)]
        else:
            recvbuf = None
            counts = []
            counts_offset = []

        if all_gather:
            self.mpi.Allgatherv((data, prod(data.shape),
                                 MPI_TYPE[data.dtype]),
                                (recvbuf, (counts, counts_offset),
                                 MPI_TYPE[data.dtype]))
        else:
            self.mpi.Gatherv((data, prod(data.shape),
                              MPI_TYPE[data.dtype]),
                             (recvbuf, (counts, counts_offset),
                              MPI_TYPE[data.dtype]))
        return recvbuf

    def gather(self, data_in, root=0):
        return self._gather_array(data_in, all_gather=False, root=root)

    def allgather(self, data_in, root=0):
        return self._gather_array(data_in, all_gather=True, root=root)

    def gather_list(self, data_in, total_trials, return_all=False):
        scatterindices = self.get_scatter_indices(total_trials)

        ret = []

        # Gather up the data
        for node in range(len(scatterindices)):
            pos = 0
            for trialnum in range(*scatterindices[node]):
                if node == self.mpi.rank:
                    # (it's us)
                    obj = data_in[pos]
                    self.bcast(data_in[pos], root=node)
                    pos += 1
                else:
                    # Just grab it from broadcast
                    obj = self.bcast(None, root=node)

                if return_all:
                    ret.append(obj)

        return ret


__all__.append('MPI4PyImplementor')
