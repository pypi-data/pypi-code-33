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


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit initialize storage')
    parser.add_argument('-f', action='store', required=True, dest='file', help='HomeKit pairing data file')
    return parser.parse_args()


if __name__ == '__main__':
    args = setup_args_parser()
