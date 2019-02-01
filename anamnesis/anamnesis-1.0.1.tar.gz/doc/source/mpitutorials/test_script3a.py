#!/usr/bin/python3

import sys

import numpy as np

from anamnesis import MPIHandler

# All nodes must perform this
m = MPIHandler(use_mpi=True)

# We need at least three nodes for this
if m.size < 3:
    print("Error: This example needs at least three MPI nodes")
    m.done()
    sys.exit(1)

# Create a matrix of data for scattering
# Pretend that we have 300 points of data which we want to scatter,
# each of which is a vector of dimension 20

# This creates a matrix containing 0-19 in row 1,
# 100-119 in row 2, etc
data_dim = 20
num_pts = 300

if m.rank == 0:
    # We are the master node
    print("Master node")

    data = np.tile(np.arange((num_pts)) * 100, (data_dim, 1)).T + np.arange(data_dim)[None, :]

    print("Master node: Full data array: ({}, {})".format(*data.shape))

    # 1. Scatter using scatter_array
    m1_data = m.scatter_array(data)

    print("Master node M1: m1_data shape: ({}, {})".format(*m1_data.shape))

    # 2. Scatter manually, using indices

    # Send the data to all nodes
    m.bcast(data)

    # Calculate which indices each node should work on and send them around
    scatter_indices = m.get_scatter_indices(data.shape[0])
    m.bcast(scatter_indices)

    indices = range(*scatter_indices[m.rank])

    m2_data = data[indices, :]

    print("Master node M2: m2_data shape: ({}, {})".format(*m2_data.shape))

    # 3. Gather using the gather function

    # Create some fake data to gather
    ret_data = (np.arange(m2_data.shape[0]) + m.rank * 100)[:, None]

    print("Master node: data to gather shape: ({}, {})".format(*ret_data.shape))
    print("Master node: first 10 elements: ", ret_data[0:10, 0])

    all_ret_data = m.gather(ret_data)

    print("Master node: gathered data shape: ({}, {})".format(*all_ret_data.shape))

    print("all_ret_data 0:10: ", all_ret_data[0:10, 0])
    print("all_ret_data 100:110: ", all_ret_data[100:110, 0])
    print("all_ret_data 200:210: ", all_ret_data[200:210, 0])

else:
    # We are a slave node
    print("Slave node {}".format(m.rank))

    # 1. Scatter using scatter_array
    m1_data = m.scatter_array(None)

    print("Slave node {} M1: data shape: ({}, {})".format(m.rank, *m1_data.shape))

    # 2. Scatter manually, using indices
    # Recieve the full dataset
    data = m.bcast()

    # Get our indices
    scatter_indices = m.bcast()

    # Extract our data to work on
    indices = range(*scatter_indices[m.rank])

    m2_data = data[indices, :]

    print("Slave node {} M2: data shape: ({}, {})".format(m.rank, *m2_data.shape))

    # 3. Gather using the gather function

    # Create some fake data to gather
    ret_data = (np.arange(m2_data.shape[0]) + m.rank * 100)[:, None]

    print("Slave node {}: data to gather shape: ({}, {})".format(m.rank, *ret_data.shape))
    print("Slave node {}: first 10 elements: ".format(m.rank), ret_data[0:10, 0])

    m.gather(ret_data)

# We need to make sure that we finalise MPI otherwise
# we will get an error on exit
m.done()
