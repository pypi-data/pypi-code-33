###############################################################################
# (c) Copyright 2016 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Command line client that interfaces to the Installer class

:author: Stefan-Gabriel CHITIC
'''
from datetime import datetime


class LogCreator:

    def __init__(self, logFilename):
        self.filename = logFilename

    def write(self, line, id, status):
        # Format message for both file and rabbitmq
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if id == 0:
            file_line = '[%s] [%s] %s' % (date_now, status, line)
        else:
            file_line = '[%s] [%s-%s] %s' % (date_now, status, id, line)
        # Append \n for file if there isn't any
        if file_line[-1] != '\n':
            file_line = "%s\n" % file_line

        # We need to open the file each time because this is the only file
        # that may be used by 2 concurrent processes (e.g another manager tying
        # to start and fails due to the missing lock, but we still want to
        # write the time when this tentative happened.
        self.file = open(self.filename, 'a+')
        self.file.write(file_line)
        self.file.close()

    def close(self):
        if self.file:
            self.file.close()
