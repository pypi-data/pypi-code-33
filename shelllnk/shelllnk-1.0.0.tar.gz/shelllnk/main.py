import shelllnk.parser
import sys


def main():
    with open(sys.argv[1], "rb") as fd:
        sl = shelllnk.parser.ShellLnk.parse(fd)
        print(sl)


if __name__ == "__main__":
    main()
