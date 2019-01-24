from __future__ import print_function

import argparse
import fileinput
import time
from threading import Event
from concurrent.futures import ThreadPoolExecutor


EOL = Event()  # End of line
EOF = Event()  # End of file


def get_parser():
    parser = argparse.ArgumentParser(
        prog="fluidicat",
        description=(
            "Intermittent cat command. Watch stdin or catenate a set of files "
            "and output to stdout for every N lines"
        ),
    )
    parser.add_argument(
        "-e", "--every", type=int, default=5, help="Print every N line"
    )
    parser.add_argument(
        "-w",
        "--wait",
        type=float,
        default=10,
        help="Wait time before displaying a message",
    )
    parser.add_argument(
        "files",
        metavar="FILE",
        nargs="*",
        help="Files to read, if empty, stdin is used",
    )
    return parser


def getline(iterator):
    try:
        line = next(iterator)
    except StopIteration:
        return None
    else:
        return line


def stream_wait(args, future):
    """Checks if waiting for stream_input to complete, and poll a waiting message
    on stdout once every args.wait seconds.

    """
    waiting_since = time.time()

    while not EOL.is_set():
        EOL.wait(args.wait)
        if future.done():
            # print("Exited {}".format(future))
            break
        else:
            print(
                "Waiting for output: {:.1f}s".format(time.time() - waiting_since)
            )

    EOL.clear()
    return True


def stream_input(args, it, future=None):
    """Read every line from stdin and once every N line print it to stdout and
    stop waiting. Also upon print try to cancel the wait thread.

    """
    for i in range(args.every):
        line = getline(it)
        if line is None:
            break

    if line is None:
        EOF.set()
    else:
        print(line, end="")

    if future is not None:
        # Kill wait thread
        EOL.set()
        future.cancel()

    return line


def main(args=None):
    if args is None:
        parser = get_parser()
        args = parser.parse_args()

    with ThreadPoolExecutor(max_workers=2) as ex:
        it = fileinput.input(args.files)

        # First run
        f_input = ex.submit(stream_input, args, it)
        f_wait = ex.submit(stream_wait, args, f_input)
        while not EOF.is_set():
            if not f_wait.done() and not f_input.done():
                time.sleep(0.1)
            else:
                f_input = ex.submit(stream_input, args, it, f_wait)
                f_wait = ex.submit(stream_wait, args, f_input)

        it.close()


if __name__ == "__main__":
    main()
