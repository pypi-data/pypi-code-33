###############################################################################
# (c) Copyright 2017 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Module in charge of dealing with sending and receiving commands for the
/cvmfs/lhcbdev.cern.ch
'''

from CommandExchange import CommandExchange

__author__ = 'Ben Couturier <ben.couturier@cern.ch>'


CVMFSCONDB_EXCHANGE = "cvmfscondb_actions"
CVMFSCONDB_ERRORS_EXCHANGE = "cvmfscondb_actions_errors"

class CvmfsConDBExchange(CommandExchange):
    """ Customized exchange for the cvmfs-condb startum-0 server """

    def __init__(self, connection):
        """ Constructor that fixes the names of the exchanges """
        super(CvmfsConDBExchange, self).__init__(connection,
                                                 CVMFSCONDB_EXCHANGE,
                                                 CVMFSCONDB_ERRORS_EXCHANGE)
