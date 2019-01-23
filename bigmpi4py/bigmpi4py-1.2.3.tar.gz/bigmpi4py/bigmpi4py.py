"""
================================
Toolbox
================================

This file contains many functions that will be shared through several files.
"""

import pandas as pd
import numpy as np
import time
import sys
import os
import itertools
import gc
import sys
import inspect
from sys import getsizeof, stderr
from itertools import chain
from collections import deque
try:
    from reprlib import repr
except ImportError:
    pass

import pandas as pd
import itertools
from mpi4py import MPI
from psutil import virtual_memory

# Unused modules
# import scipy.stats as sts
# import warnings
# from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
# from mpl_toolkits.axes_grid1.colorbar import colorbar
# from matplotlib import gridspec
# import matplotlib.pyplot as plt
# import seaborn as sns
# import time
# import seaborn
# from matplotlib import rc
# from collections import Counter
# from sklearn.preprocessing import normalize
# from scipy.stats import kde
# import scipy.spatial.distance as dist
# from numba import jit
# from line_profiler import LineProfiler
# import memory_profiler



# COSAS VARIADAS
# TODO: Implementar delete = True para borrar el archivo original del scatter/gether/sendr/bcast







# General variables
dict_emptythings = {pd.DataFrame: pd.DataFrame(), np.ndarray: np.array([]), list: [], str: '',
                    int: 0, float: 0.0, dict: {}, set: (), pd.Series: pd.Series(), type(None): None}



# Functions
def _get_size_object(this):
    if isinstance(this, np.ndarray):
        return this.nbytes
    elif isinstance(this, list):
        sum = 0
        for i in this:
            if isinstance(i, np.ndarray): sum += i.nbytes
            else: sum += sys.getsizeof(i)
        return sum
    elif isinstance(this, pd.DataFrame):
        return this.values.nbytes + this.index.values.nbytes + this.columns.values.nbytes
    elif isinstance(this, pd.Series):
        return this.values.nbytes + this.index.values.nbytes
    else:
        return sys.getsizeof(this)


def _is_istring_cols(scatter_object, by_col):
    string_cols = False
    if isinstance(scatter_object, (pd.DataFrame, pd.Series)):
        string_cols = True
        cols = scatter_object.columns.tolist()
        for i in by_col:
            if i not in cols:
                string_cols = False
                break
    return string_cols

def _return_set_type(set_object):
    '''
    Given a set with object types, return if it is "simple" (0), "complex" (1) or "mixed" (2)
    '''
    issimple, iscomplex = False, False
    simple_types = [int, float, str, bool, ]
    complex_types = [list, np.ndarray, pd.Series, pd.DataFrame,  set]

    for i in set_object:
        if type(i) in simple_types:
            issimple = True
            break
        elif type(i) in complex_types:
            iscomplex = True
            break
        else:
            try:
                doesdiswork = 0 == i * 0
                issimple = True
            except:
                    raise TypeError("{} is not recognized so far.".format(i))

    if (issimple) and not (iscomplex):
        return 0
    elif (iscomplex) and not (issimple):
        return 1
    else:
        return 2


def _return_values_df(scatter_object):
    if isinstance(scatter_object, (pd.DataFrame, pd.Series)):
        return scatter_object.values
    else:
        return scatter_object


def _generate_index_list(scatter_object, by_col):
    '''
    This function generates a list with index combination of all elements within
    each category (column) of by_col variable.

    :return: Nested list with index combination.
    '''
    # The 4 variables are:
    # - dict_categories: which contains the numbers of each of the categories
    # - dict_categories_lens: which contains the lengths of the categories
    # - list_dict_categories_idx: mutable list with indexes from categories, which
    #           will be altered after each loop
    # - list_dict_categories_keys: list with the categories

    # For each cycle, list_dict_categories_idx will contain a unique combination of
    # indexes, for which the table with that configuration will be selected.
    # After each cycle, the last number will be decreased in 1 unit, and if it arrives
    # 0, the decrement is passed to the next number.


    string_cols = _is_istring_cols(scatter_object, by_col)

    if string_cols:
        dict_categories = {i: list(dict.fromkeys(_return_slice(scatter_object, col_0=i,
                                    string_cols=True).values.tolist())) for i
                           in by_col}
    else:
        if isinstance(scatter_object, pd.DataFrame):
            cols = scatter_object.columns.tolist()
            dict_categories = {i: list(dict.fromkeys(_return_slice(scatter_object,
                            col_0=i, col_f=i + 1)[cols[i]].values.tolist()))
                               for i in by_col}
        else:
            dict_categories = {i: list(dict.fromkeys(_return_slice(scatter_object,
                                                 col_0=i, col_f=i+1).flatten().tolist())) for i in by_col}

    dict_categories_lens = {i: len(dict_categories[i]) for i in dict_categories.keys()}
    list_dict_categories_idx = [i - 1 for i in list(dict_categories_lens.values())]
    list_dict_categories_keys = list(dict_categories.keys())

    nested_list_idx = []

    while list_dict_categories_idx[0] >= 0:
        loop_combination_idx_list = []

        for i in range(len(list_dict_categories_idx)):
            loop_combination_idx_list.append(dict_categories
                                             [list_dict_categories_keys[i]]
                                             [list_dict_categories_idx[i]])

        nested_list_idx.append(loop_combination_idx_list)

        list_dict_categories_idx[-1] -= 1

        for idx in range(len(list_dict_categories_idx) - 1, 0, -1):

            if -1 in list_dict_categories_idx:
                list_dict_categories_idx[idx] = dict_categories_lens[
                                                    list_dict_categories_keys[idx]] - 1
                list_dict_categories_idx[idx - 1] -= 1
            else:
                break

    return nested_list_idx, list_dict_categories_keys


def _is_vable(optimize, scatter_object):
    numpy = False
    if isinstance(scatter_object, np.ndarray):
        if scatter_object.dtype.kind in ['u', 'i', 'f', 'b']:
            numpy = True

    return  optimize & \
    (numpy) | (type(scatter_object) == type(None))

def _merge_objects(list_objects, delete=False):
    '''
    Given a list with objects, merges them into one single object, provided all elements of the list
    are of the same type.

    :param list_objects: List with objects to merge.
    :param delete: If `True`, deletes list_objects
    :return: merged object
    '''

    if list_objects == None: return None

    if type(list_objects[0]) in [pd.DataFrame, pd.Series]:
        table_return = pd.concat(list_objects, copy=False)
    elif isinstance(list_objects[0], np.ndarray):
        n_rows = sum([len(i) for i in list_objects])
        i_row = 0

        if list_objects[0].ndim >= 2:
            table_return = np.empty((n_rows,) + np.shape(list_objects[0])[1:],
                                    dtype=list_objects[0].dtype)
        else:
            table_return = np.empty(n_rows, dtype=list_objects[0].dtype)

        for i in list_objects:
            if len(i) > 0:
                if list_objects[0].ndim > 1:
                    table_return[i_row:i_row + len(i), :] = i
                else:
                    table_return[i_row:i_row + len(i)] = i



                i_row += len(i)




    elif isinstance(list_objects[0], list):
        table_return = list(itertools.chain.from_iterable(list_objects))

        for i in reversed(table_return):
            if _return_set_type((i, )) == 0:
                pass
            else:
                if len(i) == 0:
                    table_return.remove(i)


    if delete: del [list_objects]

    return table_return


def _return_slice(object_slice, row_0=0, row_f=None, col_0=0, col_f=None, string_cols = False):
    if isinstance(object_slice, (pd.DataFrame, pd.Series, np.ndarray)):
        if row_f == None:
            row_f = object_slice.shape[0]
        elif col_f == None:
            col_f = object_slice.shape[1]

    if isinstance(object_slice, pd.DataFrame):
        if string_cols & (col_0 in object_slice.columns.tolist()):
            return object_slice[col_0].iloc[row_0:row_f]
        else:
            return object_slice.iloc[row_0:row_f, col_0:col_f]
    elif isinstance(object_slice, np.ndarray):
        if object_slice.ndim > 1:
            return object_slice[row_0:row_f, col_0:col_f]
        else:
            return object_slice[row_0:row_f]
    elif isinstance(object_slice, pd.Series):
        return object_slice.iloc[row_0:row_f]
    elif isinstance(object_slice, list):
        return object_slice[row_0:row_f]


def _return_idx_list_k1(idx_list, scatter_object, size, size_limit):
    '''
    Given a scatter object and a idx list of locations to cut that object, return
    the maximum k value of all the objects in the division list, as well as the new division of
    the object in a list.

    :param idx_list: List with indexes of object cutting.
    :type idx_list: list
    :param scatter_object: Object to be cut.
    :type scatter_object: Defined in `scatter()`function.
    :param size: comm.size, number of processors.
    :type size: int
    :param size_limit: limit of memory allocated to each element.
    :type size_limit: int
    :return: k value.
    :type return: int
    :return: idx list.
    :type return: list
    '''


    # Get the size of each element
    # idx_list_sizes = [_get_size_object(_return_slice(scatter_object, idx_list[i],
    #                                                  idx_list[i + 1])) for i
    #                   in range(len(idx_list) - 1)]

    idx_list_sizes = [_get_size_object(_return_slice(scatter_object, idx_list[i],
                       idx_list[i + 1])) for i in range(len(idx_list) - 1)]

    # Get the maximum value of k
    k = int(max([i / size_limit for i in idx_list_sizes])) + 1

    # Subdivide the list again, now taking into account the value of k. In this case,
    # since the list cannot be evenly distributed, linspace is created for each
    # interval, and those new intervals are added to idx_list_k.

    idx_list_k = []

    for i in range(len(idx_list) - 1):
        idx_list_k += [int(z) for z in np.linspace(idx_list[i], idx_list[i + 1], k + 1)][:-1]
    idx_list_k += [len(scatter_object)]

    return k, idx_list_k


def _return_k2(scatter_object, size_limit):
    '''
    Returns the k2 value of an object; concretely, a list with objects.

    :param scatter_object: list from which k2 must be obtained.
    :type scatter_object: list

    :param size_limit: limit of memory for each processor.
    :type size_limit: int

    :return: k2 value
    :type return: int
    '''

    # Get the size of each element
    list_object_sizes = [_get_size_object(i) for i in scatter_object]

    # Get the k2 value, that is, each element in the list in how many parts it
    # will be divided.
    k2 = int(max([i / size_limit for i in list_object_sizes])) + 1

    return k2


def _cut_in_k_parts(scatter_object, k, size, idx_list_k1 = []):
    '''
    Given a scatter object and a k value, cuts the object into k parts, trying to keep the same
    length for all the objects.

    :param scatter_object: Object to be cut.
    :type scatter_object: Defined in `scatter()`function.
    :param k: k value.
    :type k: list
    :param size: number of processors
    :type size: int
    :param idx_list_k1: list with custom cutting indexes
    :type idx_list_k1: list
    :return: cut object.
    :type return: list
    '''

    k1, k2 = k[0], k[1]

    # First, the list with scatter objects in k1 level is created. If k2 is not
    # necessary, each element will not be subdivided.

    # Get the list of indices to cut the object on
    if len(idx_list_k1) == 0:
        idx_list_k1 = [int(i) for i in np.linspace(0, len(scatter_object), size*k1 + 1)]

    scatter_list_objects_k1 = [_return_slice(scatter_object, idx_list_k1[i], idx_list_k1[i + 1])
                                 for i in range(len(idx_list_k1) - 1)]

    if k[1] <= 1:
        scatter_list_objects = scatter_list_objects_k1

        # For instance, a list with 10 arrays, with n = 2 and k1 = 6, then, the list
        # should look like this:
        #         [[A1], [A2], [A3], [A4], [A5], [], [A6], [A7], [A8], [A9], [A10], []]
        #  nk1      11    12    13    14    15   16   21    22    23    24    25    26
        #  If len(list)/n < k1, then the list is filled with empty objects.

        # For each k1, a list with each file for each processor is created:
        # [[A1],[A6]] // [[A2], [A7]] // ... // [[A5], [A10]] // [[], []]

        # In the k1-gathering process an empty list for each process is created (n = 1):
        #        [[], [], [], [], [], []] // [[], [], [], [], [], []]
        # And this list is filled with the k1-th element for each processor:
        #   [[A1], [A2], [A3], [A4], [A5], []] // [[A6], [A7], [A8], [A9], [A10], []]
        # Then, the list is cleaned of empty objects, and all list elements are
        # gathered together:
        #        [A1, A2, A3, A4, A5] // [A6, A7, A8, A9, A10]

        # As another example, a list with 10 arrays, with n = 2 and k1 = 3, then,
        # should look like this:
        #         [[A1, A2], [A3, A4], [A5], [A6, A7], [A8, A9], [A10]]
        #  n,k1      1,1       1,2      1,3    2,1       2,2      2,3

        # for each k1, the sublists must be the following:
        #         [[A1, A2], [A6, A7]] // [[A3, A4], [A8, A9]] // [[A5], [A10]]
        #  n,k1      1,1        2,1          1,2       2,2          1,3   2,3

        # After the gathering each k-th element, the lists should look like this
        #            [[], [], []] // [[], [], []]
        #            [[A1, A2], [A3, A4], [A5]] // [[A6, A7], [A8, A9], [A10]]
        #            [A1, A2, A3, A4, A5] // [A6, A7, A8, A9, A10]

        # If the object is not a list and, for instance, is an array, then the scatter only occurs
        # within the rows of the array. For instance, if n = 2 and k = 3, the array should be
        # divided as:
        #            [A11, A12, A13, A21, A22, A23]

    else:
        # In the case of having to split the arrays/lists/DataFrames into k2 parts,
        # it is important to take into account that k1 = 1 always. In that sense, instead of
        # splitting the list into individual elements, we are going to just divide each element into
        # k2 parts and, then, apply the scatter to those objects.

        # Let's imagine the case with n = 2, and k2 = 5.
        # So far we have the list:
        #         [[A1, A2, A3, A4, A5], [A6, A7, A8, A9, A10]]
        #  n                 1                     2

        # Now, each Ai matrix must be divided into the list [Ai1, Ai2, Ai3, Ai4, Ai5]
        # Therefore, we should arrive to a nested list like this:
        #   [[[A11, A12, A13, A14, A15], [A21, A22, A23, A24, A25], [A31, A32, A33, A34, A35],
        #     [A41, A42, A43, A44, A45], [A51, A52, A53, A54, A55]],
        #    [[A61, A62, A63, A64, A65], [A71, A72, A73, A74, A75], [A81, A82, A83, A84, A85],
        #     [A91, A92, A93, A94, A95], [A101, A102, A103, A104, A105]]]

        # If k2 is bigger than the number of rows of an array, the list is completed
        # with empty elements of the same class as the object. Let's imagine that
        # A1 only has 3 rows. Then, the list would be:
        #   [[[A11, A12, A13, [], []], ...]
        # It is important to notice that the empty elements in this case don't have
        # to be lists; they can be numpy array, pandas dataframes, lists, or any
        # other supported object.

        # The following code performs the splitting. The gathering is explained later.

        scatter_list_objects = [[[dict_emptythings[type(scatter_object[0])]
                                  for y in range(k2)]] for x in range(k1 * size)]

        k_i = 0

        while scatter_list_objects_k1:
            obj_k2 = []

            # Here we take each element of the list, which is an array/df/list
            for obj in scatter_list_objects_k1[0]:
                # First, we find the indexes to cut the array in k2 parts
                idx_list_k2 = [int(i) for i in
                               np.linspace(0, len(obj), k2 + 1)]

                # And then we divide the array into its corresponding parts
                # obj_k2 should contain the fragments of the arrays, e.g.:
                # obj_k2 = [[A81, A82, A83, A84, A85], [A81, A82, A83, A84, A85]]

                obj_k2.append([_return_slice(obj, idx_list_k2[i], idx_list_k2[i + 1])
                    for i in range(len(idx_list_k2) - 1)])

            if len(obj_k2) > 0:
                # If obj_k2 is not empty, then we replace the i-th object with k2.
                # We have to have an empty nested list from the beginning, like
                # [[[], [], [], [], []]] because, otherwise, an empty obj_k2 list
                # would look like this [[]], and we lack the original empty
                # structure shared with the non-empty list indexes.

                scatter_list_objects[k_i] = obj_k2

            # Since arrays can be memory-extensive, in each iteration, the first
            # element of the array is deleted
            del [scatter_list_objects_k1[0]]
            k_i += 1

    return scatter_list_objects



def _scatterv(object, comm, root = 0):
    '''
    Generalized function that automatically uses `comm.Scatterv()` or `comm.scatter()` depending
    on the data type. If the array is numeric, it does so. If the array is not numeric, or it
    is not an array of the class `numpy.ndarray`, it redirects the scattering to do `comm.scatter()`.

    :param object: object to be scattered.
    :type object: `scatter()` object type.
    :param comm: MPI.COMM_WORLD object
    :type comm: MPI.COMM_WORLD object
    :param root: root process
    :type root: int
    :param optimize_scatter: If True, uses `comm.Scaterv()` command with numerical arrays.
    :type optimize_scatter: bool
    :return: Scattered object
    '''



    '''
    This section uses comm.ScatterV method. This method requires four main arguments:
    - object to be scattered
    - counts: a list of elements (cells) of each matrix
    - displs = displacements: a list with the cell index within the matrix that occupies the 
      first position of the cell that will be scattered in the scattered matrix.
    - MPI.TYPE that will be scattered. Due to some problems I found, the only type that MPI4py
      correctly scatters is MPI.DOUBLE, which corresponds to the np.float64 type. Any other 
      combination would yield a mismatched matrix, that is, some elements of the scattered matrix
      would not correspond to the original matrix. 
      
    Therefore, this part also does 2 things: 
     (1) Transforms any numeric type to np.float64
     (2) Transforms the ndarray to 1D array using ravel()
    
    After the scattering has been done, the original shape and data types are recovered, and the 
    scattered matrix is returned.
    '''

    if comm.rank == root:
        if isinstance(object, list):
            counts = [i.size for i in object]
            displs = [0] + list(np.cumsum(counts))
            lens = [len(i) for i in object]

            object = _merge_objects(object)

        else:
            if object.ndim > 1:
                displs = [int(i)*int(object.size/object.shape[0]) for i in
                          np.linspace(0, object.shape[0], comm.size + 1)]
            else:
                displs = [int(i) for i in np.linspace(0, object.shape[0], comm.size + 1)]

            counts = [displs[i+1] - displs[i] for i in range(len(displs)-1)]

            if object.ndim > 1:
                lens = [int((displs[i+1] - displs[i])/(object.shape[1]))
                        for i in range(len(displs)-1)]
            else:
                lens = [displs[i+1] - displs[i] for i in range(len(displs)-1)]

        displs = displs[:-1]
        shape = object.shape
        object_type = object.dtype

        if object.ndim > 1:
            object = object.ravel().astype(np.float64, copy=False)

    else:
        object, counts, displs, shape, lens, object_type = None, None, None, None, None, None

    counts = comm.bcast(counts, root=root)
    displs = comm.bcast(displs, root=root)
    lens = comm.bcast(lens, root=root)
    shape = list(comm.bcast(shape, root=root))
    object_type = comm.bcast(object_type, root=root)


    shape[0] = lens[comm.rank]
    shape = tuple(shape)

    x = np.zeros(counts[comm.rank])
    comm.Scatterv([object, counts, displs, MPI.DOUBLE], x, root=root)

    '''
       This part selects whether the array is scattered using scatter() or comm.Scatterv().
       It chooses the data type of the rank == root processor, and broadcasts the object type.
    '''

    del object

    if len(shape) > 1:
        return  np.reshape(x, (-1,) + shape[1:]).astype(object_type, copy=False)
    else:
        return x.view(object_type)



def _gatherv(object, comm, root, optimize, k1_val):
    '''
       Generalized function that automatically uses `comm.Gatherv()` or `comm.gather()` depending
       on the data type. If the array is numeric, it does so. If the array is not numeric, or it
       is not an array of the class `numpy.ndarray`, it redirects the scattering to do `comm.gather()`.

       :param object: object to be scattered.
       :type object: `gather()` object type.
       :param comm: MPI.COMM_WORLD object
       :type comm: MPI.COMM_WORLD object
       :param root: root process
       type root: int
       :return: Scattered object
       '''

    '''
    This first part selects whether the array is scattered using gather() or comm.Gatherv().
    It chooses the data type of the rank == root processor, and broadcasts whether to optimize
    the scattering, and the object type.
    '''

    optimize_scatter, object_type = 0, None

    if comm.rank == root:
        if (isinstance(object, np.ndarray)) & (optimize):
            if object.dtype in [np.float64, np.float32, np.float16, np.float,
                                np.int, np.int8, np.int16, np.int32, np.int64, int, float,
                                bool]:
                optimize_scatter = 1
                object_type = object.dtype

    optimize_scatter = comm.bcast(optimize_scatter, root=root)
    object_type = comm.bcast(object_type, root=root)


    '''
       This section uses comm.GatherV method. This method requires four main arguments:
       - object to be gathered
       - counts: a list of elements (cells) of each matrix
       - displs = displacements: a list with the cell index within the matrix that occupies the 
         first position of the cell that will be scattered in the scattered matrix.
       - MPI.TYPE that will be gathered. Due to some problems I found, the only type that MPI4py
         correctly scatters is MPI.DOUBLE, which corresponds to the np.float64 type. Any other 
         combination would yield a mismatched matrix, that is, some elements of the scattered matrix
         would not correspond to the original matrix. 

       Therefore, this part also does 2 twings: 
        (1) Transforms any numeric type to np.float64
        (2) Transforms the ndarray to 1D array using ravel()

       After the scattering has been done, the original shape and data types are recovered, and the 
       scattered matrix is returned.
       '''
    if optimize_scatter == 1:

        counts = object.size
        lens = object.shape[0]
        shape = list(object.shape)

        if object.ndim > 1:
            object = object.ravel().astype(np.float64, copy=False)

        counts = comm.allgather(counts)
        lens = comm.gather(lens, root=root)
        displs = None

        if comm.rank == root:
            displs = [sum(counts[:i]) for i in range(len(counts))]
            shape[0] = sum(lens)
            shape = tuple(shape)

        if comm.rank == root:
            x = np.zeros(sum(counts), dtype=np.float64)
        else:
            x = None

        comm.Gatherv([object, counts[comm.rank]], [x, counts, displs, MPI.DOUBLE], root=root)


        if comm.rank == root:
            if len(shape) > 1:
                return_obj = np.reshape(x, (-1,) + shape[1:]).astype(object_type, copy=False)
                if k1_val == 1:
                    return return_obj
                else:
                    lens = [0] + list(np.cumsum(lens))
                    return [return_obj[lens[i] : lens[i+1]] for i in range(len(lens)-1)]
            else:
                return_obj = x.view(object_type)
                if k1_val == 1:
                    return return_obj
                else:
                    lens = [0] + list(np.cumsum(lens))
                    return [return_obj[lens[i]: lens[i + 1]] for i in range(len(lens) - 1)]
        else:
            return x

    else:
        return comm.gather(object, root=root)


def _gather_or_allgather(object, comm, root, type_gather='gather', optimize=True, k1_val=1):
    if type_gather == 'gather':
        return _gatherv(object, comm, root, optimize, k1_val)
    elif type_gather == 'allgather':
        return comm.allgather(object)


def _general_scatter(scatter_object, comm, by, dest, size_limit, root, optimize, scatter_method):
    '''
    This function is a more generalised form of the comm.scatter() function, prepared for arrays
    of any size.

    :param scatter_object: Object to be divided.
    :type scatter_object: `pd.DataFrame`, `np.ndarray`, and list of string, ints, floats, or
                          `pd.DataFrame` or `np.ndarray` objects. If a list of objects is passed
                          objects must all of them be [int, float, str] or [pd.DataFrame, np.array].
                          Lists with elements of mixed classes are yet not supported.

    :param comm: MPI4PY's MPI.COMM_WORLD object.

    :param by: If the table cannot be directly divided by rows and, instead, there are some
               categorical variables that are stored within a column/s in the
               `pd.DataFrame`/`np.ndarray` object, `scatter` can perform the subdivision based
               on this variable.  For instance, it the column has 1000 genes (several rows per
               gene), and the # of processors is 10, each processor will have 100 genes. So far,
               only one `by` variable can be attributed. The table must be sorted by this
    :type by: int (`np.ndarray`) or str (`pd.Dataframe`).

    :param size_limit: maximum byte size allowed for each divisible object. If the size exceeds the
                       size limit, the chunk will be divided in `k`subchunks.
    :type size_limit: int

    :param root: processor from which the object has been created.
    :type root: int

    :param scatter_method: ['scatter' | 'bcast']. If 'scatter', divides de object and distributes it
                            into the processors. If 'bcast', sends a copy of the object to all
                            processors.

    :return: i-th subtable for processor i, already parallelized.
    :type return: `pd.DataFrame`, `np.ndarray`, and list of string, ints, floats, or
                  `pd.DataFrame` or `np.ndarray` objects.
    '''

    rank = comm.rank
    size = comm.size


    scatter_object_type = type(scatter_object)
    tag = 4568121

    if type(by) != list: by = [by]

    size_limit = size_limit / size


    if size == 1:
        return scatter_object

    if rank == root:
        if scatter_method in ['sendrecv']:
            size = 1
            by = []


        if type(scatter_object) in [pd.DataFrame, np.ndarray, pd.Series]:
            by_col = by if by != [] else []
            scatter_object_nrows = scatter_object.shape[0]

            # The division will differ depending on the value of BY argument. If the by value is not
            # empty, the idx list will be created according to the "by" value. After k is calculated,
            # the list of indexes will be subdivided according to the k value.

            if len(by_col) > 0:
                # Divide the array by category

                idx_list = []

                # We are going to obtain the categories for each of the columns, and run a for loop
                # to search the indices. Then, the list will be divided into sublists based on the
                # k value.

                # For example, if the table is divided by category A and category B with values
                # [a, b, c, d], [m, n], then list_categories_keys = [[a, b, c, d], [m, n]]
                # and nested_list_idx = [[3, 1], [3, 0], [2, 1], [2, 0], ..., [0, 1], [0, 0]]
                # nested_list_values is [[d, n], [d, m], [c, n], [c, m], ..., [a, n], [a, m]]

                nested_list_values, list_categories_keys = _generate_index_list(scatter_object,
                                                                               by_col)

                # Once the nested list is obtained, we get the index coordinates of the
                # rows whose combination of elements matches the one from the combination. Then,
                # if the index list is not empty, we get the minimum value and add it to the list.


                string_cols = _is_istring_cols(scatter_object, by_col)

                for value_comb in nested_list_values:

                    for i in range(len(value_comb)):
                        if string_cols: col_f = by_col[i]
                        else: col_f = by_col[i] + 1

                        bool_array_i = _return_slice(scatter_object, col_0=by_col[i],
                                  col_f=col_f, string_cols=string_cols) == value_comb[i]

                        if i == 0:
                            if isinstance(bool_array_i, (pd.DataFrame, pd.Series)):
                                bool_array = bool_array_i.values
                            else:
                                bool_array = bool_array_i
                        else:
                            if isinstance(bool_array_i, (pd.DataFrame, pd.Series)):
                                bool_array = bool_array & bool_array_i.values
                            else:
                                bool_array = bool_array & bool_array_i


                    bool_to_idx = np.argwhere(bool_array.flatten()).flatten()


                    if len(bool_to_idx) > 0: idx_list.append(int(min(bool_to_idx)))

                idx_list.append(len(scatter_object))
                idx_list = sorted(idx_list)

                # Since there might be more categories than processors, we will select the indexes
                # that fit the number of processors for instance, for n = 4 and
                # a list of [0, 10, 15, 20, 35, 40, 50, 55, 60, 70] -> [0, 15, 35, 50, 70]

                lsp = np.linspace(0, len(idx_list) - 1, size + 1)
                idx_list = [idx_list[int(i)] for i in lsp]

                k, idx_list_k = _return_idx_list_k1(idx_list, scatter_object, size, size_limit)

            else:
                # Divide the array by length of rows.
                lsp = np.linspace(0, scatter_object_nrows, size + 1)
                idx_list = [int(i) for i in lsp]

                k, idx_list_k = _return_idx_list_k1(idx_list, scatter_object, size, size_limit)

                # For example, if the object to divide is a dataframe A to be divided into 2
                # procesors, a common division list would be [A1, A2], with each element being
                # the half of the dataframe. Now, if A1 = 1GB and A2 = 5GB, we have to set k = 3.
                # In this case, the division list would be [A11, A12, A13, A21, A22, A23], that is,
                # A23 would be sent to the 2nd processor and with the batch of Ax3 dataframes.

            # Now the list with the objects to be parallelized is created.
            if _is_vable(optimize, scatter_object) & (k == 1):
                scatter_list_objects = scatter_object
            else:
                scatter_list_objects = [_return_slice(scatter_object,idx_list_k[i],idx_list_k[i + 1])
                                        for i in range(len(idx_list_k) - 1)]


        elif type(scatter_object) == list:
            # In the case the list is to be scattered, it can be a list with
            # 1) Simple types (int, float, str)
            # 2) Complex types (pd.DataFrame, np.ndarray, list)
            # It cannot contain elements from both classes.

            set_type = _return_set_type(scatter_object)

            if set_type == 2: # Mixed
                raise TypeError('The list to be scattered cannot contain simple types (int, float, '
                                'str) and complex types (pd.DataFrame, np.ndarray, list) mixed '
                                'together.')

            # Depending on the type of list, the separation will be different.

            elif set_type == 0:
                # In this case, the list can be subdivided into k subfragments if necessary.

                # Divide the array by length of rows.
                idx_list = [int(i) for i in np.linspace(0, len(scatter_object), size + 1)]

                k, idx_list_k = _return_idx_list_k1(idx_list, scatter_object, size, size_limit)

                scatter_list_objects = [scatter_object[idx_list_k[i]:idx_list_k[i + 1]] for i
                                        in range(len(idx_list_k) - 1)]

            elif set_type == 1:
                # In this approach, two k values must be obtained:
                # k1: The list is divided in n parts, and k1 is the top integer of length(chunk) /
                #     limit size. For instance, if the list has 50 elements to be distributed into
                #     10 cores, k1 is the division of the biggest 5-element chunk into limit size.
                # k2: The size of each element in the list is taken, and k2 is the division of the
                #     biggest element by the limit size.

                # Divide the array by length of rows.
                idx_list = [int(i) for i in np.linspace(0, len(scatter_object), size + 1)]

                k2 = _return_k2(scatter_object, size_limit)

                if k2 == 1:
                    k1, idx_list_k1 = _return_idx_list_k1(idx_list, scatter_object, size, size_limit)
                else:
                    k1, idx_list_k1 = 1, idx_list

                k = [k1, k2]

                scatter_list_objects = _cut_in_k_parts(scatter_object, k, size, idx_list_k1)

            else:
                raise TypeError("The object types ({}) are not allowed so far.".format(set_types))
        if type(k) != list: k = [k, 1] # with k2 = 1 we will skip the step of using k2


    else:
        k, scatter_list_objects, idx_list = None, None, None

    # After all the preparations, the scattering is done. For that, first k is
    # scattered across all cores and, then, scatter_list_objects is scattered accordingly.
    k = comm.scatter([k] * comm.size, root=root)  # Distribute k for all processors
    k1, k2 = k[0], k[1]
    is_vable = _is_vable(optimize, scatter_object)
    # Some processors since there is None it will be True, but in the root processor it might be
    # False
    is_vable = np.all(comm.allgather(is_vable))


    # In order to do the scatter, a list where all the chunks and subchunks are going to be dumped
    # is necessary. This list will be deleted later on, and the final objects will be combined later
    # on too.

    # If k1 = 3, for instance, the variable would be [[], [], []]


    if k2 > 1:

        if rank == root:  # We prepare the k_ith subchunks for all the processors and gather them into a list
            # If K2 == 5 (for k1 = 1):
            #      [[[A11, A12, A13, A14, A15], [A21, A22, A23, A24, A25]],
            #        [[A61, A62, A63, A64, A65], [A71, A72, A73, A74, A75]]]

            # For objects:
            #       [A11, A21]

            if is_vable:
                pass
            else:
                table_list_k_i = [scatter_list_objects[i] for i in
                                  range(0, k1 * size, k1)]

        else:  # Again, we generate a dummy variable for the rest of processors,
            # which will be replaced by comm.scatter()
            table_list_k_i = None

        # Up to this point, If K2 == 5 (for k1 = 1):
        #    table_list_k_i =  [[[A11, A12, A13, A14, A15], [A21, A22, A23, A24, A25]],
        #                       [[A61, A62, A63, A64, A65], [A71, A72, A73, A74, A75]]]

        merge_table_k_i_j = []

        for k_2 in range(k2):
            if rank == root:
                table_k_i_j = []

                for z in table_list_k_i:

                    i_j_z = []

                    for l in range(len(z)):
                        i_j_z.append(z[l][k_2])

                    table_k_i_j.append(i_j_z)

            #      i_j_z = [A11, A21]  CPU 1 <--//--> CPU 2 [A61, A71]
            #      table_k_i_j = [[A11, A21], [A61, A71]]

            else:
                table_k_i_j = None

            if scatter_method == 'scatter':
                table_k_i_j = comm.scatter(table_k_i_j, root=root)
            elif scatter_method == 'sendrecv':
                if rank == root:
                    comm.send(table_k_i_j[0], dest=dest, tag=tag)
                if rank == dest:
                    table_k_i_j = comm.recv(source=root, tag=tag)

            # After the scatter,
            #      table_k_i_j = [A11, A21]  CPU 1 <--//--> CPU 2 [A61, A71]

            merge_table_k_i_j.append(table_k_i_j)

            # After all the runs on k2, merge_table_k_i_j is (k1 = 1):
            # [[A11, A21], [A12, A22], [A13, A23], [A14, A24], [A15, A25]]  CPU1
            # [[A61, A71], [A62, A72], [A63, A73], [A64, A74], [A65, A75]]  CPU1

        if scatter_method == 'sendrecv':
            object_return = [] if comm.rank == dest else None

            # Merge table kij ->
            # [[A11, A21, A31], [A12, A22, A32], [A13, A23, A33], [A14, A24, A34]]
            if rank == dest:
                for l in range(len(merge_table_k_i_j[0])):
                    object_return.append(_merge_objects(
                        [merge_table_k_i_j[k][l] for k in range(len(merge_table_k_i_j))]
                    ))
                return object_return

            else:
                return None

        elif scatter_method == 'scatter':
            object_return_not_merged = [[[] for y in range(0)] for x in
                                        range(len(merge_table_k_i_j[0]))]


            for l in range(len(merge_table_k_i_j[0])):
                object_return_not_merged[l] = [_merge_objects(
                    [merge_table_k_i_j[k_2][l] for k_2 in range(len(merge_table_k_i_j))]
                )]

            # In this step, we merge the dataframes/arrays of type A1x, A2x, ...

            # for the first iteration,a nd CPU 1, the array should look like this:
            # object_return_not_merged = [[A1, A2], [], []]
            # After the last iteration, the list is  [[A1, A2], [A3, A4], [A5]]

    else:
        if scatter_method == 'scatter':
            object_return_not_merged = [[[] for y in range(0)] for x in range(k1)]
        elif scatter_method == 'sendrecv':
            object_return_not_merged = [[[] for y in range(0)] for x in range(k1)] if \
                rank == dest else None

        for k_i in range(k1):
            # From the previous example, let's recall the lists where K2 = 1 or K2 > 1:

            # If K2 == 1: (n = 2, k1 = 3)
            #         [[A1, A2], [A3, A4], [A5], [A6, A7], [A8, A9], [A10]]
            #  n,k1      1,1       1,2      1,3    2,1       2,2      2,3

            # If instead of splitting lists, we only have a dataframe or an array A, the list of
            # objects would be [A11, A12, A13, A21, A22, A23]

            if rank == root:  # We prepare the k_ith subchunks for all the processors and gather them into a list

                # If K2 == 1 (for k1 = 1):
                #         [[A1, A2], [A6, A7]]
                #  n,k1      1,1       2,1

                if is_vable & (k[0] == 1):
                    pass
                else:
                    table_list_k_i = [scatter_list_objects[i] for i in range(0, k1 * size, k1)]

            else:    # Again, we generate a dummy variable for the rest of processors,
                     # which will be replaced by comm.scatter()
                table_list_k_i = None


            if scatter_method == 'scatter':
                if is_vable:
                    if k[0] == 1:
                        object_return_not_merged[k_i] = _scatterv(scatter_object, comm, root=root)
                    else:
                        object_return_not_merged[k_i] = _scatterv(table_list_k_i, comm, root=root)
                else:
                    object_return_not_merged[k_i] = comm.scatter(table_list_k_i, root=root)




            elif scatter_method == 'sendrecv':
                if rank == root:
                    comm.send(table_list_k_i[0], dest=dest, tag=tag)
                if rank == dest:
                     object_return_not_merged[k_i] = comm.recv(source=root, tag=tag)

            # At this point, if only one k1 has run, the object_return_not_merged should be:

            # For lists:
            #         [[A1, A2], [], []]  CPU 1 <--//--> CPU 2  [[A6, A7], [], []]
            # For objects:
            #       [A11, [], []] CPU 1 <--//--> CPU 2  [A21, [], []]

            # After running all k1, the object_return_not_merged should be:

            # For lists:
            #         [[A1, A2], [A3, A4], [A5]]  CPU 1 <--//--> CPU 2  [[A6, A7], [A8, A9], [A10]]
            # For objects:
            #       [A11, A12, A13] CPU 1 <--//--> CPU 2  [A21, A22, A23]

            if rank == root:
                # As before, scatter_list_objects has all array information, which can be memory
                # extensive. After each list for k1 has been processed, the original element is deleted
                try:
                    for k_del in reversed(sorted(list(range(0, k1 * size, k1)))):
                        del scatter_list_objects[k_del]
                except:
                    del scatter_list_objects

            k1 -= 1

    # After running all k1, we recall, the object_return_not_merged should be:
    # For lists (regardless of k2, since it has been processed so far):
    #         [[A1, A2], [A3, A4], [A5]]  CPU 1 <--//--> CPU 2  [[A6, A7], [A8, A9], [A10]]
    # For objects:
    #       [A11, A12, A13] CPU 1 <--//--> CPU 2  [A21, A22, A23]


    if is_vable & (k1 == 1):
        object_return = object_return_not_merged[0]
    else:
        object_return = _merge_objects(object_return_not_merged, delete=True)

    # The last object, object return, takes the list of elements, and gathers/concatenates them
    # into one. Therefore, the last object should look like this:
    # For lists:
    #         [A1, A2, A3, A4, A5]  CPU 1 <--//--> CPU 2  [A6, A7, A8, A9, A10]
    # For objects:
    #       A1 CPU 1 <--//--> CPU 2  A2

    return object_return









def _general_gather(gather_object, comm,  size_limit, root, optimize, gather_method):
    '''
    This function is a more generalised form of the comm.gather() function, prepared for arrays
    of any size.

    :param gather_object: Object to be gathered.
    :type gather_object: `pd.DataFrame`, `np.ndarray`, and list of string, ints, floats, or
                          `pd.DataFrame` or `np.ndarray` objects. If a list of objects is passed
                          objects must all of them be [int, float, str] or [pd.DataFrame, np.array].
                          Lists with elements of mixed classes are yet not supported.

    :param comm: MPI4PY's MPI.COMM_WORLD object.

    :param size_limit: maximum byte size allowed for each divisible object. If the size exceeds the
                       size limit, the chunk will be divided in `k`subchunks.
    :type size_limit: int

    :gather_method: ['gather' | 'allgather']. If `gather`, returns the object to the "root"
                    processor. If `allgather`, all processors receive a copy of the gathered object.
    :type gather_method: str

    :param root: if `gather`, processor that will receive the gathered object.
    :type root: int

    :return: object from gathered subobjects.
    :type return: `pd.DataFrame`, `np.ndarray`, and list of string, ints, floats, or
                  `pd.DataFrame` or `np.ndarray` objects.
    '''

    rank, size = comm.rank, comm.size

    size_limit = size_limit / size

    if size == 1:
        return gather_object


    # Different to the scatter part, in the gather we first must know the common k values in advance
    # in order to divide the list into the k (k1,k2) parameters. This parameter must be known in
    # all processors independently and, afterwards, the biggest values are distributed across
    # all processors.

    if (type(gather_object) == list) & (_return_set_type(gather_object) == 1):
        k2 = _return_k2(gather_object, size_limit)
    else:
        k2 = 1

    if k2 == 1:
        k1, idx_list_k1 = _return_idx_list_k1([0, len(gather_object)], gather_object, size, size_limit)
    else:
        k1 = 1

    k1 = max(comm.allgather(k1))
    k2 = max(comm.allgather(k2))

    if k2 > 1:
        k1 = 1
    else: # We have to readjust the idx for the new k value
        idx_list_k1 = [int(z) for z in np.linspace(0, len(gather_object), k1+1)]

    # The gather function differs from the scatter one in the sense that, instead of dividing the
    # object into n, or n*k types, we gather n objects, or n*k subobjects. Therefore, the division
    # of objects in scatter is different to the one in gather, since the "n" factor is not divisive.

    # Let's imagine the case of an array or a list of arrays. Originally, the object has been
    # divided into n parts:

    # A -> A1, A2, ..., An
    # [A1, A2, A3..., A2n] -> [A1, A2], [A3, A4], ..., [A2n-1, A2n]

    # --------> Gather of Arrays/DataFrames, simple lists (k2 = 1).
    # If Ai and k1 = 1, then A = comm.gather(Ai, root). Then, we merge the list of objects.
    # If Ai and k1 > 1:
    # First, in each processor, we divide Ai in k parts:
    # [A11, A12, ..., A1k] CPU1 <-//-> CPU2 [A21, A22, ..., A2k] // ... //-> CPUn [An1, ..., Ank]

    # In order to save the final matrix, we do a k*n empty matrix, and for each k,
    #  we gather the lists:
    # [A11, A21, A31, ..., An1], [A12, A22, A32, ..., An2], ..., [A1k, A2k, ..., Ank]
    # Thus, for each k, we will insert the element from that list into the i % n element of the
    # gather list.

    # After all the loops, we merge the list of subarrays into its final form

    # --------> Gather of Lists when k2 > 1.
    # In this case we are going to divide each element of the list into k2 subelements, and,
    # item by item on the list. Let's put an example of n = 2, k2 = 5,
    # and the original list had 7 elements.

    # The original list would look like this:
    # [A1, A2, A3, A4]  CPU1 <--//--> CPU2  [A5, A6, A7]

    # First, the second list if "filled" with one empty element:
    # [A1, A2, A3, A4] CPU1 <--//--> CPU2  [A5, A6, A7, []]

    # We create a list with Nones:  [None, None, None, None, None, None, None, None]

    # Second, and for each object, the corresponding element is cut in k2 parts:
    # i = 1  ->   [A11, A12, A13, A14, A15] <--//-->  [A51, A52, A53, A54, A55]
    # i = 4  ->   [A41, [], A42, A43, []] <--//-->  [[], [], [], [], []]
    # A4 has only 3 divisible elements, so the rest are filled with empty objects.
    # for each j in range k2:
    # j = 1 -> [A11] // [A51]  -- comm.gather --> [A11, A51]
    # j = 5 -> [A15] // [A55]  -- comm.gather --> [A15, A55]
    # --- make a list with individual elements and merge it ---->
    # [[A11, ..., A15], [A51, ..., A55]] --> [A1, A5]
    # The list looks like this: [A1, None, None, None, A5, None, None, None]
    #
    # For the fourth iteration, the process would be like this:
    # j = 1 -> [A41] // []  -- comm.gather --> [A41, []]
    # j = 2 -> [] // []  -- comm.gather --> [[], []]
    # --- make a list with individual elements and merge it ---->
    # [[A41, [], A42, A43, []], [[], [], [], [], []] --> [A4, []]
    # The list looks like this: [A1, A2, A3, A4, A5, A6, A7, []]


    # We are going to broadcast the length of the array, get the maximum one, and create a list with
    # Nones

    if (k1 == 1) & (k2 == 1):
        object_return = _gather_or_allgather(gather_object, comm, root, gather_method, optimize=optimize)

    elif (k1 > 1):
        object_return = [None] * (k1 * size) if rank == root else None

        for k_i in range(k1):


            object_return_k_i = _gather_or_allgather(gather_object[idx_list_k1[k_i]:idx_list_k1[k_i+1]],
                                   comm, root, gather_method, k1_val = k1, optimize=optimize)
            # If the command is gather, then for CPUS != root, the returning object is None, which
            # is not indexable.

            if rank == root:
                for i in range(size):
                    object_return[k_i + i*(k1)] = object_return_k_i[i]


    elif (k2 > 1):
        # First, we get the maximum size of all objects, and "complete" the length of each object
        # to match the maximum one. This is so we can easily iterate for each object in the list.
        max_size_list = max(comm.allgather(len(gather_object)))

        if len(gather_object) == 0:
            gather_object += [[]] * (max_size_list - len(gather_object))
        else:
            gather_object += [dict_emptythings[type(gather_object[0])]] * (max_size_list -
                                                                       len(gather_object))

        object_return = [None] * (max_size_list * size) if rank == root else None


        for size_i in range(max_size_list):
            list_return_object_i = [] if rank == root else None

            # We establish the cutting points of the object.
            object_cut_k2 = [int(x) for x in np.linspace(0, len(gather_object[size_i]), k2+1)]

            for k_i in range(k2):
                object_return_k_i = _gather_or_allgather(gather_object[size_i][object_cut_k2[k_i]:
                                                                              object_cut_k2[k_i+1]],
                                       comm, root, gather_method, optimize=False)
                #
                if rank == root: list_return_object_i.append(object_return_k_i)

            if rank == root:
                for n_i in range(size):
                    merged_i_k = _merge_objects([list_return_object_i[k_i][n_i] for k_i in range(k2)])
                    if len(merged_i_k) > 0:
                        object_return[size_i +  n_i*max_size_list] = merged_i_k


            del list_return_object_i

        if rank == root:
            object_return = list(filter(None.__ne__, object_return))
        return object_return


    if isinstance(object_return, list):
        object_return = list(filter(None.__ne__, object_return))
        if len(object_return) > 0:
            object_return = _merge_objects(object_return)
        else:
            object_return = None

    return object_return

def bcast(bcast_object, comm, size_limit=50000000, root=0):
    '''
    This function communicates an object to the rest of cores, but this time it communicates the
    whole object to all cores. Thus, at the end of the broadcasting, each core will have an
    exact copy of the object.

    :param bcast_object: Object to be communicated.
    :type bcast_object: `pd.DataFrame`, `np.ndarray`, and list of string, ints, floats, or
                          `pd.DataFrame` or `np.ndarray` objects. If a list of objects is passed
                          objects must all of them be [int, float, str] or [pd.DataFrame, np.array].
                          Lists with elements of mixed classes are yet not supported.

    :param comm: MPI4PY's MPI.COMM_WORLD object.


    :param size_limit: maximum byte size allowed for each divisible object. If the size exceeds the
                       size limit, the chunk will be divided in `k`subchunks.
    :type size_limit: int

    :param root: processor from which the object has been created.
    :type root: int

    :return: i-th subtable for processor i, already parallelized.
    :type return: `pd.DataFrame`, `np.ndarray`, and list of string, ints, floats, or
                  `pd.DataFrame` or `np.ndarray` objects.
    '''

    # This function will discern two cases:
    # 1) There is enough memory to perform the broadcast by doing n copies of the scatter object,
    #    and by scattering the list ob scatter_objects directly.
    # 2) If there is not enough memory, the broadcast will be done in two steps:
    #    a) We create a list with the j-th element (k is derived from a loop) being the
    #       scatter_object, and the rest of elements are empty.
    #    b) The list is broadcasted. If j is the cpu number, then scatter_object is set to be the
    #       j-th element from the list. That is, n-1 times the received object will be empty, and
    #       one time it will be the scatter_object. In that time, scatter_object is set and, after
    #       all loops are run, scatter_object is returned.

    # First, we get the available memory size and broadcast it to all computers. This value will
    # vary a little accross computers if we don't scatter the number from root and, instead, we
    # directly call for the function. Although this variation should be insignificant, it is
    # important to share the same value accross CPUs.


    if comm.rank == root:
        mem = virtual_memory().available
        size_scatter_object = _get_size_object(bcast_object)
    else:
        mem, size_scatter_object = None, None

    mem = comm.scatter([mem] * comm.size)
    size_scatter_object = comm.scatter([size_scatter_object] * comm.size)
    scatter_object_type = comm.scatter([type(bcast_object)] * comm.size)

    if size_scatter_object * comm.size > mem:
        raise MemoryError('The size of the object is too big to be broadcasted for this number'
                           'of processors.')

    # xxx = 1
    # # if size_scatter_object * comm.size < 0.85 * mem: # <-- 0.7 is arbitrary
    # if xxx == 1:
    #     if comm.rank == 0: print('TIME EFFICIENT')
    #     if comm.rank == root:
    #         if isinstance(bcast_object, list):
    #             # If the object is a list, instead of having [[A1, A2], [A1, A2], [A1, A2]],
    #             # which cannot be divided by k2, we are going to create [A1, A2, A1, A2, A1, A2]
    #             # scatter it, and recover the final object as a list.
    #             scatter_object = bcast_object * comm.size
    #         else:
    #             scatter_object = [bcast_object] * comm.size
    #     else:
    #         scatter_object = None
    #
    #
    #
    #     # Since we are scattering a list, the scatter object will also be a list, [scatter_object],
    #     # regardless of type. Since we are interested in scatter_object and not [scatter_object],
    #     # we get the first value from scatter_object. This is not a fail from the function,
    #     # since the return of the function is of the same type as the input.
    #     if scatter_object_type == list:
    #         return_object =  _general_scatter(scatter_object, comm, by=[], dest=0, size_limit=size_limit,
    #                                 root=root, scatter_method='scatter', optimize=False)
    #     else:
    #         return_object =  _general_scatter(scatter_object, comm, by=[], dest=0, size_limit=size_limit,
    #                                 root=root, scatter_method='scatter', optimize=False)[0]
    #
    # else:

    return_object = None
    for CPU in range(comm.size):
        if root == CPU:
            return_object = bcast_object
        else:
            if comm.rank == root: # WARNING: This part is not optimized for lists, so it may yield OverflowError
                scatter_list = [dict_emptythings[type(bcast_object)]] * comm.size
                scatter_list[CPU] = bcast_object
            else:
                scatter_list = None


            scatter_list_object = _general_scatter(scatter_list, comm, size_limit=size_limit,
                                                   root=root, by = [], dest = 0, optimize=False,
                                                   scatter_method='scatter')

            if comm.rank == CPU:
                return_object = scatter_list_object[0]


    return return_object


def scatter(scatter_object, comm, by=[], size_limit=500000000, root=0, optimize = True):
    '''
    This function divides an object into `n` parts, and distributes it into all the cores.

    :param scatter_object: Object to be communicated.
    :type scatter_object: `pd.DataFrame`, `np.ndarray`, and list of string, ints, floats, or
                          `pd.DataFrame` or `np.ndarray` objects. If a list of objects is passed
                          objects must all of them be [int, float, str] or [pd.DataFrame, np.array].
                          Lists with elements of mixed classes are yet not supported.

    :param comm: MPI4PY's MPI.COMM_WORLD object.

    :param by: If the table cannot be directly divided by rows and, instead, there are some
               categorical variables that are stored within a column/s in the
               `pd.DataFrame`/`np.ndarray` object, `scatter` can perform the subdivision based
               on this variable.  For instance, it the column has 1000 genes (several rows per
               gene), and the # of processors is 10, each processor will have 100 genes. So far,
               only one `by` variable can be attributed. The table must be sorted by this
    :type by: int (`np.ndarray`) or str (`pd.Dataframe`).

    :param size_limit: maximum byte size allowed for each divisible object. If the size exceeds the
                       size limit, the chunk will be divided in `k`subchunks.
    :type size_limit: int

    :param root: processor from which the object has been created.
    :type root: int

    :param optimize: If `True`, applies a vectorized parallelization of the object, given the object
                     supports that parallelization.
    :type optimize: bool

    :return: i-th subtable for processor i, already parallelized.
    :type return: `pd.DataFrame`, `np.ndarray`, and list of string, ints, floats, or
                  `pd.DataFrame` or `np.ndarray` objects.
    '''
    return _general_scatter(scatter_object, comm, by, dest=0, size_limit=size_limit, root=root,
                            optimize=optimize, scatter_method='scatter')

def gather(gather_object, comm, optimize = True, size_limit=1500000000, root=0):
    '''
    This function communicates individual objects, each one in a different core, to a
    destination core.

    :param gather_object: Object to be communicated.
    :type gather_object: `pd.DataFrame`, `np.ndarray`, and list of string, ints, floats, or
                          `pd.DataFrame` or `np.ndarray` objects. If a list of objects is passed
                          objects must all of them be [int, float, str] or [pd.DataFrame, np.array].
                          Lists with elements of mixed classes are yet not supported.

    :param comm: MPI4PY's MPI.COMM_WORLD object.

    :param size_limit: maximum byte size allowed for each divisible object. If the size exceeds the
                       size limit, the chunk will be divided in `k`subchunks.
    :type size_limit: int

    :param root: processor from which the object has been created.
    :type root: int

    :param optimize: If `True`, applies a vectorized parallelization of the object, given the object
                     supports that parallelization.
    :type optimize: bool

    :return: i-th subtable for processor i, already parallelized.
    :type return: `pd.DataFrame`, `np.ndarray`, and list of string, ints, floats, or
                  `pd.DataFrame` or `np.ndarray` objects.
    '''

    return _general_gather(gather_object, comm,  size_limit, root, optimize=optimize, gather_method='gather')

def allgather(allgather_object, comm,  size_limit=1500000000, root=0):
    '''
    This function combines the objects from all the cores and distributes copies of the
    combined object to all the cores.

    :param gather_object: Object to be communicated.
    :type gather_object: `pd.DataFrame`, `np.ndarray`, and list of string, ints, floats, or
                          `pd.DataFrame` or `np.ndarray` objects. If a list of objects is passed
                          objects must all of them be [int, float, str] or [pd.DataFrame, np.array].
                          Lists with elements of mixed classes are yet not supported.

    :param comm: MPI4PY's MPI.COMM_WORLD object.

    :param size_limit: maximum byte size allowed for each divisible object. If the size exceeds the
                       size limit, the chunk will be divided in `k`subchunks.
    :type size_limit: int

    :param root: processor from which the object has been created.
    :type root: int

    :return: i-th subtable for processor i, already parallelized.
    :type return: `pd.DataFrame`, `np.ndarray`, and list of string, ints, floats, or
                  `pd.DataFrame` or `np.ndarray` objects.
    '''
    return _general_gather(allgather_object, comm,  size_limit, root, optimize=False, gather_method='allgather')

def sendrecv(send_object, comm, dest, size_limit=1500000000, root=0):
    '''
    This function sends an object from a source core to a destination node.

        :param send_object: Object to be communicated.
    :type send_object: `pd.DataFrame`, `np.ndarray`, and list of string, ints, floats, or
                          `pd.DataFrame` or `np.ndarray` objects. If a list of objects is passed
                          objects must all of them be [int, float, str] or [pd.DataFrame, np.array].
                          Lists with elements of mixed classes are yet not supported.

    :param comm: MPI4PY's MPI.COMM_WORLD object.

    :param dest: Destination node where the object will be communicated.
    :type dest: int

    :param size_limit: maximum byte size allowed for each divisible object. If the size exceeds the
                       size limit, the chunk will be divided in `k`subchunks.
    :type size_limit: int

    :param root: processor from which the object has been created.
    :type root: int

    :return: i-th subtable for processor i, already parallelized.
    :type return: `pd.DataFrame`, `np.ndarray`, and list of string, ints, floats, or
                  `pd.DataFrame` or `np.ndarray` objects.
    '''


    return _general_scatter(send_object, comm, by=[], dest = dest, size_limit=size_limit, root=root, optimize=False,
                            scatter_method='sendrecv')


# Profiler example to use
# lp = LineProfiler()
# lp_wrapper = lp(_general_scatter)
# lp_wrapper(scatter_object, comm, by, dest = 0, size_limit=size_limit, root=root, optimize=optimize, scatter_method='scatter')
# if comm.rank == 1:
#     lp.print_stats()