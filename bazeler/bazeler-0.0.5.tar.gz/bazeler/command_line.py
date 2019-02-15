import argparse
import sys
import bazeler 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root')
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--search_paths', default='')
    parser.add_argument('--permissive', action='store_true')
    parser.add_argument('--use_precompiled', action='store_true')
    parser.add_argument('--verbose', action='store_true')
    sys.exit(bazeler.execute(**vars(parser.parse_args())))
