from .bluewolf import run
import sys
import argparse
import re
import subprocess

VERSION = '0.0.7.3'

def hwaddr(s, pat=re.compile(r"[a-f0-9A-F]{2}:[a-f0-9A-F]{2}:[a-f0-9A-F]{2}:[a-f0-9A-F]{2}:[a-f0-9A-F]{2}:[a-f0-9A-F]{2}")):
    if not pat.match(s):
        raise argparse.ArgumentTypeError
    return s

def hw_avail():
    return subprocess.check_output("hcitool dev | wc -l", shell=True).strip() != "1"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--interface", required=False, help="Specify bluetooth interface, defaults to hci0")
    ap.add_argument("targets", type=hwaddr, nargs="+", help="Target devices")
    ap.add_argument("--version", action='version', version='%(prog)s {version}'.format(version=VERSION))
    args = ap.parse_args()
    if not hw_avail():
        print("No bluetooth devices enabled!\nTurn on bluetooth device to continue...")
        sys.exit()
    run(args.targets)
