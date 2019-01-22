#!/usr/bin/env python3
import argparse
import os
import os.path
import pickle
from collections import OrderedDict

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', default='cpp', help='language')
    opt = parser.parse_args()
    print(opt)
    maps = {}
    map_filename = 'maps.%s.pkl' % opt.lang
    if os.path.exists(map_filename):
       with open(map_filename, 'rb') as f:
            maps = pickle.load(f)
    OrderedDict(sorted(maps.items(), key=lambda t: t[0]))
    for key, value in maps.items() :
        print("%s<=%s" % (value, key))

if __name__ == "__main__":
    main()

