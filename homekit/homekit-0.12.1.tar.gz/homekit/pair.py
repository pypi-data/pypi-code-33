#!/usr/bin/env python3

#
# Copyright 2018 Joachim Lusiardi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import argparse
import sys
from homekit.controller import Controller


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit pairing app')
    parser.add_argument('-d', action='store', required=True, dest='device',
                        help='HomeKit Device ID (use discover to get it)')
    parser.add_argument('-p', action='store', required=True, dest='pin', help='HomeKit configuration code')
    parser.add_argument('-f', action='store', required=True, dest='file', help='HomeKit pairing data file')
    parser.add_argument('-a', action='store', required=True, dest='alias', help='alias for the pairing')
    return parser.parse_args()


if __name__ == '__main__':
    args = setup_args_parser()

    controller = Controller()
    try:
        controller.load_data(args.file)
    except Exception as e:
        print(e)
        sys.exit(-1)

    if args.alias in controller.get_pairings():
        print('"{a}" is a already known alias'.format(a=args.alias))
        sys.exit(-1)

    try:
        controller.perform_pairing(args.alias, args.device, args.pin)
        pairing = controller.get_pairings()[args.alias]
        pairing.list_accessories_and_characteristics()
        controller.save_data(args.file)
        print('Pairing for {a} was established.'.format(a=args.alias))
    except Exception as e:
        print(e)
        sys.exit(-1)
