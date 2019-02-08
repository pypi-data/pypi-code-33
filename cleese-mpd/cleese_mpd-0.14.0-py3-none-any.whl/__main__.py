#!/usr/bin/env python
import sys

from asyncio import run

from .commands import main


def run_main():
    run(main.run_async(sys.argv[1:]))


if __name__ == '__main__':
    run_main()
