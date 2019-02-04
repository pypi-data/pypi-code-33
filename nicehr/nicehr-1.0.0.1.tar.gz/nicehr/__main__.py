import argparse

from nicehr import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('hr')
    parser.add_argument('--msg', '-m', help="Optional Message places in the center of the Line", default="")
    parser.add_argument('--color', '-c', help='The Color of the hr.', default="default")
    parser.add_argument('--colorful', action='store_true', default=False)
    args = parser.parse_args()
    print(nice_hr(args.hr, args.msg, args.colorful, args.color))
