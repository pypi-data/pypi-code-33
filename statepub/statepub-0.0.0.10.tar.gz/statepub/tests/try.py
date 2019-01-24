# Std library imports
import time

# Third party imports
import psutil

# In-package imports
from statepub.state import ComputingState
from statepub.state import NetworkState

from statepub.publish import StatePublisher


def try_computing_state():
    cs = ComputingState()
    cs.acquire()
    print('THE CPU USAGE "{}"\nTHE RAM USAGE "{}"\nCPU TEMP "{}"'.format(cs.cpu, cs.ram, cs.temp))


def try_network_state():
    ns = NetworkState()
    ns.acquire()
    print('BYTES SENT "{}"\nBYTES RECEIVED "{}"'.format(ns.bytes_sent, ns.bytes_recv))


def try_publisher():

    sp1 = StatePublisher('jonas', '192.168.0.250')
    sp2 = StatePublisher('test2', '192.168.0.250')

    print('ID OF THE FIRST PUBLISHER "{}"\nID OF THE SECOND PUBLISHER "{}"'.format(sp1.id, sp2.id))

    cs = ComputingState()
    ns = NetworkState()

    for i in range(0, 10):
        sp1.publish(cs, ns, topic='status')
        time.sleep(5)


#try_computing_state()
#try_network_state()
try_publisher()