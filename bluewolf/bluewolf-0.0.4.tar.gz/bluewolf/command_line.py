from .bluewolf import run
import sys
import argparse
import re

def hwaddr(s, pat=re.compile(r"[a-f0-9A-F]{2}:[a-f0-9A-F]{2}:[a-f0-9A-F]{2}:[a-f0-9A-F]{2}:[a-f0-9A-F]{2}:[a-f0-9A-F]{2}")):
    if not pat.match(s):
        raise argparse.ArgumentTypeError
    return s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--interface", required=False, help="Specify bluetooth interface, defaults to hci0")
    ap.add_argument("targets", type=hwaddr, nargs="+", help="Target devices")
    args = ap.parse_args()
    print(args.targets)
    run(args.targets)
