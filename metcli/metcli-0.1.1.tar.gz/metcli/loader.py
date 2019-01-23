#!/usr/bin/env python3
import time


def loader(loading):
    steps = ['🌤', '🌤', '🌦']

    while loading:
        for step in steps:
            print(step + '\r', end='', flush=True)
            time.sleep(0.3)
