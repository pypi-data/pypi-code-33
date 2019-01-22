# Copyright (C) 2018  Sean Z <sean.z.ealous@gmail.com>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess
import socket

import logger

def run(args):
    logger.debug(args)
    popen = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    popen.wait()

    return popen

def run_cmd(args):
    logger.debug(args)
    p = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = []
    while True:
        line = p.stdout.readline()
        logger.debug(line)
        out.append(line)
        if line == '' and p.poll() != None:
            break
    
    return ''.join(out)

