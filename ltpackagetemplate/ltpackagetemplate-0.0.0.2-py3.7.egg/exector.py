#! /usr/local/bin/python3
# encoding: utf-8
# Author: LiTing

import os
import sys
import getopt
from .utils import *


def print_help():
    print('\n Usage:'
          '\n\t python3 exector.py [-s <string>]'
          '\n\t '
          '\n e.g.'
          '\n\t python3 exector.py'
          '\n\t python3 exector.py -s helloworld'
          '\n'
          )


def main(argv):
    try:
        opts, args = getopt.getopt(argv, 's:h', ['string', 'help'])
    except getopt.GetoptError:
        print('python3 exector.py [-s <string>]')
        sys.exit(2)

    global out_put

    for opt, arg in opts:
        if opt in {'-s', '--string'}:
            out_put = arg
        elif opt in {'-h', '--help'}:
            print_help()
            return

    __do_exec()


out_put = 'hello world'


def __do_exec():
    PrintWithColor.black('').fore_green().style_underline().apply(f'{out_put}', end='\n\n')


if __name__ == '__main__':
    main(sys.argv[1:])
