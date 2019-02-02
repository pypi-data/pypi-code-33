import argparse
from typing import Callable


class TestConnectionResult(object):

    def __init__(self, is_success: bool, is_timeout: bool, error_message: str) -> None:
        self.is_success = is_success
        self.is_timeout = is_timeout
        self.error_message = error_message

    @staticmethod
    def error(message: str) -> 'TestConnectionResult':
        return TestConnectionResult(False, False, message)

    @staticmethod
    def success() -> 'TestConnectionResult':
        return TestConnectionResult(True, False, "")

    @staticmethod
    def timeout() -> 'TestConnectionResult':
        return TestConnectionResult(False, True, "")


def wait_for_connection(test_func: Callable[[], TestConnectionResult], message: str, n_retries: int,
                        verbose: bool = True) -> bool:
    if verbose:
        print(message + " ", end="", flush=True)

    for _ in range(n_retries):
        res = test_func()
        if res.is_success:
            if verbose:
                print("\nConnection is opened!!", flush=True)
            return True
        elif res.is_timeout:
            print(".", end="", flush=True)
        else:
            print(f"\nError: {res.error_message}", flush=True)
            return False

    if verbose:
        print("\nTimeout! Cannot connect.")

    return False


def str2bool(v: str) -> bool:
    assert v.lower() in {"true", "false"}
    return v.lower() == "true"


def get_argparser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description)
    parser.register("type", "boolean", str2bool)
    return parser
