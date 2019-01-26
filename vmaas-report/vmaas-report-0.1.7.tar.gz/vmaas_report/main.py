#!/usr/bin/env python
import argparse

from vmaas_report.evaluator import Evaluator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--status", action="store_true", help="show status of configured VMaaS server")
    args = parser.parse_args()

    evaluator = Evaluator()

    if args.status:
        evaluator.print_status()
    else:
        evaluator.evaluate_updates()

if __name__ == "__main__":
    main()
