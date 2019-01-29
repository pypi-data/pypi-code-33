#!/usr/bin/env python3
"""
Display security details: holding accounts, quantity, value, last price w/ date, asset class.
Calculate:
    - Return of Capital
    - Yield
argparse can effectively replace click for building CLIs.
"""
import argparse
import logging

#from piecash import Commodity, Account
from pricedb import PriceDbApplication, SecuritySymbol
from gnucash_portfolio import BookAggregate
from gnucash_portfolio.reports.security_info import SecurityInfoReport
from gnucash_portfolio.model.stock_model import SecurityDetailsViewModel


def read_parameters():
    """ Read parameters from the command line """
    parser = argparse.ArgumentParser(description='read symbol from command line')
    parser.add_argument('symbol', type=str, help='security symbol')
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    return args


def display(model: SecurityDetailsViewModel):
    """ Format and display the results """
    # header
    #print("    security            quantity  ")
    #print("-------------------------------------------------------")
    print(f"{model.security.fullname}")

    #shares = agg.get_num_shares()

    print(f"{model.security.namespace}:{model.security.mnemonic}, shares: {model.quantity:,.2f}")

    # todo add all the info from the security details page in web ui,
    # prices, etc.
    # avg_price = agg.get_avg_price()
    #currency = agg.get_currency()
    currency = model.currency
    print(f"Average price: {model.average_price:.2f} {currency}")

    # last price
    prices_app = PriceDbApplication()
    sec_symbol = SecuritySymbol("", "")
    sec_symbol.parse(model.symbol)
    latest_price = prices_app.get_latest_price(sec_symbol)
    latest_price_date = latest_price.datum.to_iso_date_string()
    logging.debug(latest_price)
    print(f"Latest price: {latest_price.value:.2f} {latest_price.currency} on {latest_price_date}")

    print("")

    # Income
    print("Income")
    print(f"Total: {model.income:,.2f} {model.currency}, {model.income_perc:.2f}%")
    print(f"Last 12m: {model.income_last_12m:,.2f} {model.currency}, {model.income_perc_last_12m:.2f}%")

    # Return of Capital.
    if model.return_of_capital:
        print(f"Return of capital: {model.return_of_capital:,.2f}")

    print("")

    print("Holding Accounts:")
    print("-----------------")

    for account in model.accounts:
        balance = account.get_balance()
        if balance == 0:
            # Skip empty accounts
            continue
        value = balance * latest_price.value
        print(f"{account.fullname}, {balance:,.2f} units, {value:,.2f} {latest_price.currency}")


def run(args):
    """ Call this method if running from another module which parses arguments """
    symbol = args.symbol
    symbol = symbol.upper()

    book = BookAggregate()

    agg = book.securities.get_aggregate_for_symbol(symbol)
    security = agg.security

    report = SecurityInfoReport(book)
    model = report.run(symbol)

    # Display
    if security is None:
        print(f"No securities found for {symbol}.")
        exit

    display(model)


def main():
    args = read_parameters()

    run(args)

if __name__ == "__main__":
    main()
