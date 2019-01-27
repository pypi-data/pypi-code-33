from .bluewolf import run
import sys
import argparse
import re
import os

def hwaddr(s, pat=re.compile(r"[a-f0-9A-F]{2}:[a-f0-9A-F]{2}:[a-f0-9A-F]{2}:[a-f0-9A-F]{2}:[a-f0-9A-F]{2}:[a-f0-9A-F]{2}")):
    if not pat.match(s):
        raise argparse.ArgumentTypeError
    return s

def hw_avail():
    return os.system("hcitool dev") != 0   

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--interface", required=False, help="Specify bluetooth interface, defaults to hci0")
    ap.add_argument("targets", type=hwaddr, nargs="+", help="Target devices")
    args = ap.parse_args()
    if not hw_avail():
        print("No bluetooth devices enabled!\nTurn on bluetooth device to continue...")
        sys.exit()
    run(args.targets)
