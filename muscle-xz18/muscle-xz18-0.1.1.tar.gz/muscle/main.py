import sys
from pathlib import Path

sys.path.append(str(Path().resolve()))

from muscle.view.cli import cli


def main():
    cli(sys.argv[1:])


if __name__ == '__main__':
    main()
