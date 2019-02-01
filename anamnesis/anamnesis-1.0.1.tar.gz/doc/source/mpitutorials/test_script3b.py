#!/usr/bin/python3

import sys

from anamnesis import MPIHandler

# All nodes must perform this
m = MPIHandler(use_mpi=True)

# We need at least three nodes for this
if m.size < 3:
    print("Error: This example needs at least three MPI nodes")
    m.done()
    sys.exit(1)

# Create a list of data for scattering
# Pretend that we have 300 points of data which we want to scatter
num_pts = 300

if m.rank == 0:
    # We are the master node
    print("Master node")

    data = [str(x) for x in range(num_pts)]

    print("Master node: Full data array: len: {}".format(len(data)))

    # Scatter using scatter_list
    m1_data = m.scatter_list(data)

    print("Master node M1: m1_data len: {}".format(len(m1_data)))

    # Gather list back together again
    all_ret_data = m.gather_list(m1_data, num_pts, return_all=True)

    print("Master node: gathered list len: {}".format(len(all_ret_data)))

    print("all_ret_data 0:10: ", all_ret_data[0:10])
    print("all_ret_data 100:110: ", all_ret_data[100:110])
    print("all_ret_data 200:210: ", all_ret_data[200:210])

else:
    # We are a slave node
    print("Slave node {}".format(m.rank))

    # Scatter using scatter_list
    m1_data = m.scatter_list(None)

    print("Slave node {}: data len: {}".format(m.rank, len(m1_data)))

    # Gather using the gather_list function
    m.gather_list(m1_data, num_pts)

# We need to make sure that we finalise MPI otherwise
# we will get an error on exit
m.done()
