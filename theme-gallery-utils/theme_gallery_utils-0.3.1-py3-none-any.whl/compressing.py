# -*- coding: utf-8 -*-

"""
Lossless multi-threaded compression of png files.
"""

from functools import partial
import os
import subprocess
from threading import Thread
from queue import Queue

WORKER_COUNT = 4


def optipng_args(screenshot, compressed):
    """Return the optipng args."""
    return [
        "optipng",
        "-o7",
        "-clobber",
        "-preserve",
        "-strip",
        "all",
        screenshot,
        "-out",
        compressed,
    ]


def worker(main_queue, verbose=True):
    """Individual task to be process by the queue."""
    kwargs = {}
    if not verbose:
        kwargs.update(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    while True:
        item = main_queue.get()
        if not item:
            break

        subprocess.run(optipng_args(*item), **kwargs)
        main_queue.task_done()


def compress_images(uncompressed_dir, compressed_dir, verbose=True):
    """Call optipng to compress every image in the directory."""

    # ensure compressed dir exists
    if not os.path.isdir(compressed_dir):
        os.makedirs(compressed_dir, exist_ok=True)

    main_queue = Queue()

    threads = []
    for i in range(WORKER_COUNT):
        thread = Thread(target=partial(worker, main_queue, verbose=verbose))
        thread.start()
        threads.append(thread)

    for file_name in os.listdir(uncompressed_dir):
        input_path = os.path.join(uncompressed_dir, file_name)
        output_path = os.path.join(compressed_dir, file_name)
        main_queue.put((input_path, output_path))

    # block until all tasks are done
    main_queue.join()

    # stop workers
    for i in range(WORKER_COUNT):
        main_queue.put(None)
    for thread in threads:
        thread.join()


def install_dependencies(verbose=True):
    """Install optipng as a dependency."""

    args = [
        "sudo",
        "apt-get",
        "install",
        "optipng",
    ]
    kwargs = {"check": True}
    if not verbose:
        kwargs.update(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return subprocess.run(args, **kwargs).returncode
