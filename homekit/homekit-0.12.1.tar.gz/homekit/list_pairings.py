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

from homekit.controller import Controller


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit list pairings app')
    parser.add_argument('-f', action='store', required=True, dest='file', help='File with the pairing data')
    parser.add_argument('-a', action='store', required=True, dest='alias', help='alias for the pairing')
    return parser.parse_args()


if __name__ == '__main__':
    args = setup_args_parser()
    controller = Controller()
    controller.load_data(args.file)
    if args.alias not in controller.get_pairings():
        print('"{a}" is no known alias'.format(a=args.alias))
        exit(-1)

    pairing = controller.get_pairings()[args.alias]
    pairings = pairing.list_pairings()

    for pairing in pairings:
        print('Pairing Id: {id}'.format(id=pairing['pairingId']))
        print('\tPublic Key: 0x{key}'.format(key=pairing['publicKey']))
        print('\tPermissions: {perm} ({type})'.format(perm=pairing['permissions'],
                                                      type=pairing['controllerType']))
