import argparse

import dlc_gui

parser = argparse.ArgumentParser()
parser.add_argument("config", help="Abs path to config.yaml", nargs="?")
args = parser.parse_args()
config = args.config

dlc_gui.show(config)
