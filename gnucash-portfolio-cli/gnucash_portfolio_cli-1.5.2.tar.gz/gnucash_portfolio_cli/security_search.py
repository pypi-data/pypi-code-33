#!/usr/bin/env python3
""" search for security """
import argparse
from gnucash_portfolio import BookAggregate

def read_parameters():
    """ Read parameters from the command line """
    parser = argparse.ArgumentParser(description='read symbol from command line')

    parser.add_argument('search_term', type=str, help='The term to search for in security description or symbol')

    args = parser.parse_args()
    return args

def main():
    """ Main method, for unit testing """
    # Get parameter from command line
    args = read_parameters()

    book = BookAggregate()
    securities = book.securities.find(args.search_term)
    securities = sorted(securities, key=lambda security: security.namespace + ":" + security.mnemonic)

    for security in securities:
        print(f"{security.namespace}:{security.mnemonic} {security.fullname}")

if __name__ == "__main__":
    main()
