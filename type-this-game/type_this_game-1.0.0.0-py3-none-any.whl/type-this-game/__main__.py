#!/usr/bin/env python3
"""Simple game; you win by typing this source code."""

from time import time

print('Write this script, as fast as possible!')
start = time()

with open(__file__) as f:
    for line in f:
        while input('>? ').replace('\t', '    ') != line.rstrip():
            print('No! Try again! The current line is:\n' + line)

print(f'My time is {time() - start:2f} seconds.')
