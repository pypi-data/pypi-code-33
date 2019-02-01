#!/usr/bin/python3

import sys

from anamnesis import MPIHandler

from test_mpiclasses import ComplexPerson, ComplexPlace, ComplexTrain

# All nodes must perform this
m = MPIHandler(use_mpi=True)

# We need at least three nodes for this
if m.size < 3:
    print("Error: This example needs at least three MPI nodes")
    m.done()
    sys.exit(1)

if m.rank == 0:
    # We are the master node
    print("Master node")

    # Create a person to broadcast
    s_person = ComplexPerson('Fred', 42)

    print("Master: Created Person: {} {}".format(s_person.name, s_person.age))

    m.bcast(s_person)

    s_place = m.bcast(root=1)

    print("Master: Recieved Place: {}".format(s_place.location))

elif m.rank == 1:
    # We are slave node 1
    print("Slave node {}".format(m.rank))

    # Wait for our broadcast object to be ready
    s_person = m.bcast()

    print("Slave node {}: Recieved Person: {} {}".format(m.rank, s_person.name, s_person.age))

    # Now create our own object and broadcast it to the other nodes
    s_place = ComplexPlace('Manchester')

    print("Slave node {}: Created place: {}".format(m.rank, s_place.location))

    m.bcast(s_place, root=1)

    s_train = m.recv(source=2)

    print("Slave node {}: Received Train: {} {}".format(m.rank, s_person.name, s_person.age))

else:
    # We are slave node 2
    print("Slave node {}".format(m.rank))

    # Wait for our first broadcast object to be ready
    s_person = m.bcast()

    print("Slave node {}: Received Person: {} {}".format(m.rank, s_person.name, s_person.age))

    # Wait for our second broadcast object to be ready
    s_place = m.bcast(root=1)

    print("Slave node {}: Received Place: {}".format(m.rank, s_place.location))

    # Create a train and send to node 1 only
    s_train = ComplexTrain('Durham')

    print("Slave node {}: Created train: {}".format(m.rank, s_train.destination))

    m.send(s_train, dest=1)

# We need to make sure that we finalise MPI otherwise
# we will get an error on exit
m.done()
