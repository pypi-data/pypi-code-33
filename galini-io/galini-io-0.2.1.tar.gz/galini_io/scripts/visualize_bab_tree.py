# Copyright 2018 Francesco Ceccon
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Writes message to the specified file."""
from argparse import ArgumentParser
from galini_io.reader import MessageReader


def main():
    parser = ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    with open(args.filename, 'rb') as f:
        reader = MessageReader(f, stream=False)

        nodes_visited = 0
        for msg in reader:
            which_oneof = msg.WhichOneof('content')

            if which_oneof == 'add_bab_node':
                coordinate = msg.add_bab_node.coordinate
                print('--- ADD: ' + str(coordinate))
                print('Lower Bound: {}'.format(msg.add_bab_node.lower_bound))
                print('Upper Bound: {}'.format(msg.add_bab_node.upper_bound))
                print('Variables:')
                for i, info in enumerate(msg.add_bab_node.variables_information):
                    line = '{}: [{}, {}]'.format(info.variable_name, info.lower_bound, info.upper_bound)
                    print(' {} - {}'.format(i, line))
                print()
            elif which_oneof == 'prune_bab_node':
                coordinate = list(msg.prune_bab_node.coordinate)
                print('--- PRUNE: ' + str(coordinate))
