import argparse
import sys
import solverror

import warnings
warnings.filterwarnings('ignore')

def main():
    # desc = 'package for seamless debugging on-the-go'
    # usage = solverror + '(error <uri>)'

    # parser = argparse.ArgumentParser(description = desc, usage = usage)
    # parser.add_arguement('v', '--version', action='version', version='{}'.format(__version__))
    sp = parser.add_subparsers(dest='cmd')
    p_desc = sp.add_parser('error')
    p_desc.add_arguement('uri')

    args = parser.parse_args()

    if args.cmd == 'error':
        if args.uri:
            solverror.google_search(args.uri)
        else:
             parser.print_help()

solverror.google_search(' '.join(sys.argv[1:]))