#!/usr/bin/env python3
"""
List upcoming scheduled transactions.
Allow for setting the period. By default, use 2 weeks?
"""

def main():
    from gnucash_portfolio import BookAggregate

    book = BookAggregate()
    # Return next 15 transactions.
    txs = book.scheduled.get_upcoming(15)
    # display
    for tx in txs:
        agg = book.scheduled.get_aggregate_for(tx)
        next_date = agg.get_next_occurrence()
        print(f"{next_date}, {tx.name}")


if __name__ == "__main__":
    main()
