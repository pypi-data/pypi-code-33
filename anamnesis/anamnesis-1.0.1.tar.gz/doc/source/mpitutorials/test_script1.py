#!/usr/bin/python3

from anamnesis import MPIHandler

from test_mpiclasses import ComplexPerson, ComplexPlace, ComplexTrain

# All nodes must perform this
m = MPIHandler(use_mpi=True)

if m.rank == 0:
    # We are the master node
    print("Master node")

    # Create a person, place and train to broadcast
    s_person = ComplexPerson('Fred', 42)
    s_place = ComplexPlace('York')
    s_train = ComplexTrain('Disastersville')

    print("Master: Person: {} {}".format(s_person.name, s_person.age))
    print("Master: Place: {}".format(s_place.location))
    print("Master: Train to: {}".format(s_train.destination))

    m.bcast(s_person)
    m.bcast(s_place)
    m.bcast(s_train)

else:
    # We are a slave node
    print("Slave node {}".format(m.rank))

    # Wait for our objects to be ready
    s_person = m.bcast()
    s_place = m.bcast()
    s_train = m.bcast()

    print("Slave node {}: Person: {} {}".format(m.rank, s_person.name, s_person.age))
    print("Slave node {}: Place: {}".format(m.rank, s_place.location))
    print("Slave node {}: Train: {}".format(m.rank, s_train.destination))

# We need to make sure that we finalise MPI otherwise
# we will get an error on exit
m.done()
