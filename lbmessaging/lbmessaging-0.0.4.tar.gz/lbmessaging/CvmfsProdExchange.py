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

from lbmessaging.CommandExchange import CommandExchange

__author__ = 'Ben Couturier <ben.couturier@cern.ch>'


CVMFSPROD_EXCHANGE = "cvmfsprod.action"
CVMFSPROD_ERRORS_EXCHANGE = "cvmfsprod.action.error"

class CvmfsProdExchange(CommandExchange):
    """ Customized exchange for the cvmfsdev startum-0 server """

    def __init__(self, connection):
        """ Constructor that fixes the names of the exchanges """
        super(CvmfsProdExchange, self).__init__(connection,
                                               CVMFSPROD_EXCHANGE,
                                               CVMFSPROD_ERRORS_EXCHANGE)
