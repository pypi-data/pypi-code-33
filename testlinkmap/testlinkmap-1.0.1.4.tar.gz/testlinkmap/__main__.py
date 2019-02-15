#! /usr/local/bin/python3

import sys
from testlinkmap.find_macho_linkmap import main as entry

if __name__ == '__main__':
	entry(sys.argv[1:])


# def do_exec():
#     return entry(sys.argv[1:])

# if __name__ == "__main__":
#     sys.exit(do_exec())