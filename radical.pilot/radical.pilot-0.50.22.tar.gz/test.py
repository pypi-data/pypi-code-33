#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2014, http://radical.rutgers.edu'
__license__   = 'MIT'

import os
import sys
import time

import radical.pilot as rp
import radical.utils as ru



# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    session = rp.Session()
    try:
        pmgr    = rp.PilotManager(session=session)
        pd_init = {'resource'      : 'debug.summit',
                   'runtime'       : 60,  
                   'exit_on_error' : True,
                   'cores'         : 42 * 5
                  }
        pdesc = rp.ComputePilotDescription(pd_init)
        pilot = pmgr.submit_pilots(pdesc)
        umgr  = rp.UnitManager(session=session)
        umgr.add_pilots(pilot)

        n = 1
        cuds = list()
        for i in range(0, n):

            cud = rp.ComputeUnitDescription()
            cud.executable       = '/bin/date'
            cud.gpu_processes    = 1
            cud.cpu_processes    = 4 
            cud.cpu_threads      = 4
            cud.cpu_process_type = rp.POSIX
            cud.cpu_thread_type  = rp.POSIX
            cuds.append(cud)

        umgr.submit_units(cuds)
        umgr.wait_units()


    finally:
        # always clean up the session, no matter if we caught an exception or
        # not.  This will kill all remaining pilots.
        session.close(download=True)



# ------------------------------------------------------------------------------

