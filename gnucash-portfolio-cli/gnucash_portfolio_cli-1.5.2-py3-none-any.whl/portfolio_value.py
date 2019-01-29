#!/usr/bin/env python3
""" Portfolio Value report """

def main(args):
    """ Main entry point. Useful for calling from cli script or unit tests """
    from pydatum import Datum
    from gnucash_portfolio.reports import portfolio_value
    #from gnucash_portfolio.model.stock_model import StockViewModel
    from gnucash_portfolio.reports.portfolio_models import PortfolioValueInputModel
    #, PortfolioValueViewModel

    parameters = PortfolioValueInputModel()
    today = Datum()
    today.today()
    parameters.as_of_date = today.value
    model = portfolio_value.run(parameters)

    # Display
    print_row("security", "cost", "balance", "gain/loss", "%", "income", "inc.12m", "%")
    print("-" * 120)

    rows = sorted(model.stock_rows, key=lambda row: f"{row.exchange}:{row.symbol}")

    for row in rows:
        col1 = f"{row.exchange}:{row.symbol}"
        col2 = f"{row.shares_num:,} @ {row.avg_price:,.2f} {row.currency} = {row.cost:>7,.2f}"
        col3 = f"@ {row.price:,.2f} = {row.balance:>9,.2f}"
        col4 = f"{row.gain_loss:,.2f}"
        col5 = f"{row.gain_loss_perc:,.2f}%"
        col6 = f"{row.income:,.2f}"
        col7 = f"{row.income_last_12m:,.2f}"
        col8 = f"{row.income_last_12m_perc:,.2f}"

        print_row(col1, col2, col3, col4, col5, col6, col7, col8)


def print_row(col1, col2, col3, col4, col5, col6, col7, col8):
    """ Print the values in one row """
    line = f"{col1:<15} {col2:>32} {col3:>20} {col4:>10} {col5:>8} {col6:>8} {col7:>8} {col8:>5}"
    print(line)


if __name__ == "__main__":
    main(None)
