import logging
import sys
from asyncio import run

from .config import Config
from .demo import demo


def main():
    logging.basicConfig(level=logging.INFO)
    config = Config.load(sys.argv[1])
    run(demo(config))


if __name__ == '__main__':
    main()
