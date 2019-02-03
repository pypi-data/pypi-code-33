# Copyright (c) 2019 Monolix
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import sys
from .daemon import DMOTD

if len(sys.argv) != 3:
    print("Unexpected arguments: dmotd <file> <port>")
    sys.exit(1)

daemon = DMOTD(str(sys.argv[1]))

daemon.run(port=int(sys.argv[2]))
