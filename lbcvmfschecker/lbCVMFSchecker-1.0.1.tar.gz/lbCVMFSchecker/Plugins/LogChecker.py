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


:author: Stefan-Gabriel CHITIC
'''

from lbCVMFSchecker.LbCVMFSCheckerPluginBase import PluginBase
import subprocess


class LogChecker(PluginBase):

    PROCESS_MAX_TIMES = {
        'Idle': 300,
        'No messages to process': 15,
    }

    def __init__(self):
        super(LogChecker, self).__init__()

    def execute(self):
        command = ["lastCommands", "1"]
        try:
            proc = subprocess.Popen(command, shell=False, bufsize=1,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            output = {}
            while (True):
                line = proc.stdout.readline()
                try:
                    line = line.decode()
                except:
                    line = str(line)
                if line == "":
                    break
                if line.startswith('Error'):
                    continue
                tmp = line.split('\t')
                seconds = tmp[2]
                process = tmp[3].replace('\n', '')
                if not output.get(process, None):
                    output[process] = []
                output[process].append(int(seconds))
            # Check status
            proc.wait()
            for proc in self.PROCESS_MAX_TIMES.keys():
                if not self.PROCESS_MAX_TIMES.get(proc, None):
                    continue
                for inst in output.get(proc, []):
                    if inst > self.PROCESS_MAX_TIMES[proc]:
                        msg = 'Execution time of %s was %s (Limit: %s)' % (
                            proc, inst, self.PROCESS_MAX_TIMES[proc])
                        self.messages.append(msg)
        except Exception as e:
            self.messages.append("Failed to check logs: %s" % e)


