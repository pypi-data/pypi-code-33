#!/usr/bin/env python3
import argparse
import os
import os.path
import pickle
from collections import OrderedDict

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang1', default='cpp', help='source language')
    parser.add_argument('--lang2', default='swap', help='swapped language')
    parser.add_argument('id', nargs='+', help='id to swap')
    opt = parser.parse_args()
    print(opt)
    maps = {}
    maps1 = {}
    maps1_filename = 'maps.%s.pkl' % opt.lang1
    if os.path.exists(maps1_filename):
       with open(maps1_filename, 'rb') as f:
            maps1 = pickle.load(f)
    OrderedDict(sorted(maps1.items(), key=lambda t: t[0]))

    maps2 = {}
    for (k,v) in maps1.items():
            maps2[k] = v
    n = len(opt.id)
    for i in range(0, n-1):
            i1 = int(opt.id[i])
            for (k, v) in maps1.items():
                    if int(v) == i1:
                            maps2[k] = opt.id[i+1]
    i1 = int(opt.id[n-1])
    for (k, v) in maps1.items():
            if int(v) == i1:
                    maps2[k] = opt.id[0]

    maps2_filename = 'maps.%s.pkl' % opt.lang2
    with open(maps2_filename, 'wb') as f:
            pickle.dump(maps2, f)

if __name__ == "__main__":
    main()
