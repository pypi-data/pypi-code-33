#!/usr/bin/env python3
"""
Trying to put the whole CLI in here.
It will allow listing all the available commands with options and parameters (if any).
The commands will invoke their respective modules.

Example: `gp-cli test me -w yo -y`
"""
import argparse


def setup_portfolio_value_command(subparsers):
    """ Set up the parser for the portfolio value command """
    from gnucash_portfolio_cli import portfolio_value

    subparser: argparse.ArgumentParser = subparsers.add_parser("pvalue")
    subparser.set_defaults(func=portfolio_value.main)

def setup_parser():
    """ Set up all the commands with parameters and arguments """
    from gnucash_portfolio_cli import (security_info, upcoming_scheduled_transactions,
        favourite_accounts)

    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version='0.0.1')
    parser.set_defaults()

    subparsers = parser.add_subparsers()
    parser_test: argparse.ArgumentParser = subparsers.add_parser("test")

    # argument (required)
    parser_test.add_argument("what", type=str, help="test what?")
    # option
    parser_test.add_argument("-w", "--why", default="because!")
    # flag
    parser_test.add_argument("-y", "--yes", action="store_true")
    parser_test.set_defaults(func=show)

    # Security Info
    parser_secinfo: argparse.ArgumentParser = subparsers.add_parser("secinfo")
    parser_secinfo.add_argument("symbol", type=str, help="Security symbol to provide the information for")
    parser_secinfo.set_defaults(func=security_info.run)

    # Scheduled Transactions
    parser_scheduled: argparse.ArgumentParser = subparsers.add_parser("sched")
    parser_scheduled.set_defaults(func=upcoming_scheduled_transactions.main)

    setup_portfolio_value_command(subparsers)

    # Favourite Accounts
    fav_accounts: argparse.ArgumentParser = subparsers.add_parser("fav")
    fav_accounts.set_defaults(func=favourite_accounts.main)

    return parser

def show(args):
    print(f"yo args: what={args.what}, why={args.why}, yes={args.yes}")

def main(params = None):
    """ this code is in a function so that it can be declared an entry point in setup.py """
    import sys

    parser = setup_parser()

    args = parser.parse_args(params)

    # Handle empty arguments from the console.
    if len(sys.argv) == 1:
        params = ["-h"]
        # For debugging:
        #params = parser.parse_args(["secinfo", "vym"])
        #params = parser.parse_args(["test", "me"])
        #params = ["scheduled"]
        args = parser.parse_args(params)

    args.func(args)


if __name__ == "__main__":
    main()
