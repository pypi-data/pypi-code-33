import numpy, re, sys, logging
from circus.shared.messages import print_and_log
from .datafile import DataFile, comm

import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=FutureWarning)
    import h5py

logger = logging.getLogger(__name__)

class H5File(DataFile):

    description    = "hdf5"    
    extension      = [".h5", ".hdf5"]
    parallel_write = h5py.get_config().mpi
    is_writable    = True

    _required_fields = {'h5_key'        : str,
                        'sampling_rate' : float}
    
    _default_values  = {'dtype_offset'  : 'auto', 
                        'gain'          : 1.}


    def _check_compression(self):
        # HDF5 does not support parallel writes with compression
        if self.compression != '':
            self.parallel_write = False
            if self.is_master:
                print_and_log(['Data are compressed thus parallel writing is disabled'], 'debug', logger)

    def __check_valid_key__(self, key):
        file       = h5py.File(self.file_name, mode='r')
        all_fields = []
        file.visit(all_fields.append)    
        if not key in all_fields:
            print_and_log(['The key %s can not be found in the dataset! Keys found are:' %key, 
                         ", ".join(all_fields)], 'error', logger)
            sys.exit(1)
        file.close()

    def _read_from_header(self):

        self.__check_valid_key__(self.h5_key)
        self._open()

        header = {}
        header['data_dtype']   = self.my_file.get(self.h5_key).dtype
        self.compression       = self.my_file.get(self.h5_key).compression

        self._check_compression()
        
        self.size        = self.my_file.get(self.h5_key).shape
        
        if self.size[0] > self.size[1]:
            self.time_axis = 0
            self._shape = (self.size[0], self.size[1])
        else:
            self.time_axis = 1
            self._shape = (self.size[1], self.size[0])

        header['nb_channels']  = self._shape[1]
        self._close()

        return header

    def read_chunk(self, idx, chunk_size, padding=(0, 0), nodes=None):

        t_start, t_stop = self._get_t_start_t_stop(idx, chunk_size, padding)
        
        if nodes is None:
            if self.time_axis == 0:
                local_chunk = self.data[t_start:t_stop, :]
            elif self.time_axis == 1:
                local_chunk = self.data[:, t_start:t_stop].T
        else:
            if self.time_axis == 0:
                local_chunk = self.data[t_start:t_stop, nodes]
            elif self.time_axis == 1:
                local_chunk = self.data[nodes, t_start:t_stop].T

        return self._scale_data_to_float32(local_chunk)

    def write_chunk(self, time, data):

        data = self._unscale_data_from_float32(data)
        
        if self.time_axis == 0:
            self.data[time:time+data.shape[0], :] = data
        elif self.time_axis == 1:
            self.data[:, time:time+data.shape[0]] = data.T

    def _open(self, mode='r'):
        if mode in ['r+', 'w'] and self.parallel_write:
            self.my_file = h5py.File(self.file_name, mode=mode, driver='mpio', comm=comm)
        else:
            self.my_file = h5py.File(self.file_name, mode=mode)

        self.data = self.my_file.get(self.h5_key)
        
    def _close(self):
        self.my_file.close()
        del self.data

    @property
    def h5_key(self):
        return self.params['h5_key']