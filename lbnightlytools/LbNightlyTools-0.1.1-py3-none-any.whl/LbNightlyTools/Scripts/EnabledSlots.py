###############################################################################
# (c) Copyright 2013 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Simple script to extract slot who need to be compile
Create one file for each slot. Each file contains parameters for the next job.
Now we only have the slot name in parameter in files
'''
__author__ = 'Colas Pomies <colas.pomies@cern.ch>'

import os
import sys
from LbNightlyTools.Utils import JobParams, Dashboard
from LbNightlyTools.Configuration import loadConfig
from LbNightlyTools.Scripts.Common import PlainScript


class Script(PlainScript):
    '''
    Script to create one file for all enable slots or for slots in parameters
    This file contain the slot name and the slot build id
    The slot build id is extract with the function get_ids
    '''
    __usage__ = '%prog [options] flavour output_file.txt'
    __version__ = ''

    def defineOpts(self):
        self.parser.add_option('--config-dir',
                               help='Directory where to find configurations '
                                    'files [default: %default]')
        self.parser.add_option('--flavour',
                               help='nightly builds flavour '
                                    '[default: %default]')
        self.parser.add_option('--output',
                               help='template for output file name, it must '
                                    'contain a "{name}" that will be replaced '
                                    'by the slot name '
                                    '[default: %default]')
        self.parser.add_option('--slots',
                               help='do not look for active slots, but use the '
                                    'provided space or comma separated list')

        self.parser.set_defaults(config_dir='configs',
                                 flavour='nightly',
                                 output='slot-params-{name}.txt',
                                 slots=None)

    def write_files(self, slots, flavour, output_file):
        from couchdb import ResourceConflict

        d = Dashboard(flavour=flavour)
        slot_ids = dict((slot, d.lastBuildId(slot) + 1) for slot in slots)

        for slot in slots:
            output_file_name = output_file.format(name=slot)
            slot_build_id = slot_ids[slot]
            while True:
                try:
                    # reserve the build id by creating a place holder in the
                    # dashboard DB
                    d.db['{0}.{1}'.format(slot, slot_build_id)] = {
                        'type': 'slot-info',
                        'slot': slot,
                        'build_id': slot_build_id
                    }
                    break
                except ResourceConflict:
                    # if the place holder with that name alredy exists, bump
                    # the build id
                    slot_build_id += 1
            open(output_file_name, 'w') \
                .write(str(JobParams(slot=slot,
                                     slot_build_id=slot_build_id
                                     )) + '\n')
            self.log.info('%s written for slot %s with build id %s',
                          output_file_name,
                          slot,
                          slot_build_id)

        self.log.info('%s slots to start', len(slots))

    def main(self):
        if self.args:
            self.parser.error('unexpected arguments')

        if not self.options.slots:
            self.log.info('Starting extraction of all enable slot')
            slots = [slot.name
                     for slot in list(loadConfig(self.options.config_dir).values())
                     if slot.enabled]
        else:
            slots = self.options.slots.replace(',', ' ').split()

        # Create a file that contain JobParams for each slot
        self.write_files(slots, self.options.flavour, self.options.output)

        self.log.info('End of extraction of all enable slot')

        return 0
