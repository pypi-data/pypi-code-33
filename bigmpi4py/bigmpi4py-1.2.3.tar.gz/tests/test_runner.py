
import sys
import os

from mpi4py import MPI
import numpy as np
import pandas as pd

thereispath = False

pd.set_option('display.max_rows', 10)
pd.set_option('display.max_columns', 10)

comm = MPI.COMM_WORLD
size, rank = comm.Get_size(), comm.Get_rank()

import bigmpi4py as BM



print('Hi! This is core number %s out of %s' %(comm.rank, comm.size-1))
# Now we will isolate the task for one processor
if rank == 0:
    print('I am core %s printing this alone!' %(comm.rank))


if rank == 0:
    print('''////////////  RUNNING TEST 1  ////////////''')

array = None
if rank == 0:
    array = np.random.rand(2*size , 3)

sc_array = BM.scatter(array, comm)


if rank == 0:
    print('''+++++++++++  TEST 1 RUN SUCCESSFULLY  +++++++++++''')





if rank == 0:
    print('''////////////  RUNNING TEST 2  ////////////''')

array = None
if rank == 0:
    array = pd.DataFrame(np.random.rand(2 * size, 3))

sc_array = BM.scatter(array, comm)

if rank == 0:
    print('''+++++++++++  TEST 2 RUN SUCCESSFULLY  +++++++++++''')




if rank == 0:
    print('''////////////  RUNNING TEST 3  ////////////''')

array = None
if rank == 0:
    array = sorted([i for i in range(size)] + [i for i in range(size)] + [i for i in range(size)])

sc_array = BM.scatter(array, comm)

if rank == 0:
    print('''+++++++++++  TEST 3 RUN SUCCESSFULLY  +++++++++++''')



if rank == 0:
    print('''////////////  RUNNING TEST 4  ////////////''')

array = np.random.rand(2 * size, 3)
sc_array = BM.gather(array, comm)

if rank == 0:
    print('''+++++++++++  TEST 4 RUN SUCCESSFULLY  +++++++++++''')

if rank == 0:
    print('''////////////  RUNNING TEST 5  ////////////''')


array = pd.DataFrame(np.random.rand(2 * size, 3))
sc_array = BM.gather(array, comm)

if rank == 0:
    print('''+++++++++++  TEST 5 RUN SUCCESSFULLY  +++++++++++''')

if rank == 0:
    print('''////////////  RUNNING TEST 6  ////////////''')


array = sorted([i for i in range(size)] + [i for i in range(size)] + [i for i in range(size)])
sc_array = BM.gather(array, comm)

if rank == 0:
    print('''+++++++++++  TEST 6 RUN SUCCESSFULLY  +++++++++++''')


if rank == 0:
    print('''////////////  RUNNING TEST 7  ////////////''')

array = None
if rank == 0:
    array = list([i for i in range(size)] + [i for i in range(size)] + [i for i in range(size)])


sc_array = BM.scatter(array, comm)
gt_array = BM.gather(sc_array, comm)

if not np.all(array == gt_array):
    raise("Error on test 7")

if rank == 0:
    print('''+++++++++++  TEST 7 RUN SUCCESSFULLY  +++++++++++''')



if rank == 0:
    print('''////////////  RUNNING TEST 8  ////////////''')

array = None
if rank == 0:
    array = pd.DataFrame(np.random.rand(200, 100))


bc_array = BM.bcast(array, comm)
gt_array = BM.allgather(bc_array, comm)


if not len(gt_array) == (len(bc_array) * comm.size):
    raise("Error on test 8")

if rank == 0:
    print('''+++++++++++  TEST 8 RUN SUCCESSFULLY  +++++++++++''')