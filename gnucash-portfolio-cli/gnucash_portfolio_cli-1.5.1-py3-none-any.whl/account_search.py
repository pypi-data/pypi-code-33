#!/usr/bin/env python3
""" search for an account """
import argparse
from gnucash_portfolio import BookAggregate

def read_parameters():
    """ Read parameters from the command line """
    parser = argparse.ArgumentParser(description='read input from command line')

    parser.add_argument('search_term', type=str, help='The term to search for in account name or description')

    args = parser.parse_args()
    return args

def main():
    """ Main entry point. Useful for unit testing """
    # Get parameter from command line
    args = read_parameters()

    book = BookAggregate()
    accounts = book.accounts.find_by_name(args.search_term)
    accounts = sorted(accounts, key=lambda account: account.fullname)

    for account in accounts:
        print(f"{account.fullname} {account.description}, {account.guid}")

if __name__ == "__main__":
    main()
