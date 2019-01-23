#!/usr/bin/env python
"""
The main entry point. Invoke as `mold' if installed or `python3 -m mold'.
"""

# TODO then figure out how to deploy to PYPI and start deployin v0.0.1
import os 
import sys

import mold.cli as cli 
from mold.context import MoldContext

def main():
    exit_code = 0
    ctx = MoldContext(sys.argv, os.environ)
    if ctx.MOLD_DEBUG:
        return sys.exit(cli.handle_context(ctx))
    else:
        try:
            exit_code = cli.handle_context(ctx)
        except:
            print('Sorry, there seems to be a mold in mold.')
            print('    You may want to try reinstalling the mold-cli')
            sys.exit(ctx.CRASH)
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
