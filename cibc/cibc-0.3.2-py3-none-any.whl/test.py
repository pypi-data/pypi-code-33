from banking import CIBC
import datetime
import os

# dirr = os.path.abspath(os.path.filename(__file__))


if __name__ == '__main__':
    c = CIBC('4506445726410994', 'cIV820s42')
    c.Accounts() # grab the accounts associated with this username and login
    c.gTransactions(dateFrom=datetime.datetime(year=2018, month=9,day=1),dateUntil= datetime.datetime(year=2018, month=9, day=17)) # for each account, get all the transactions in this range
    accounts = c.accounts
    for account in accounts:
        account.tocsv('C:\\Users\\louis\\Desktop\\{}.csv'.format(account))
        print(account.tolist())

    this_year = 2018
    start = datetime.datetime(year=this_year, month=1, day=1)
    end = datetime.datetime(year=this_year, month=12, day=31)

    c.Accounts()  # get the accounts
    c.gTransactions(dateFrom=start, dateUntil=end)  # for each account, get all the transactions in this range
    CHEQUING_CAD, SAVINGS_CAD, SAVINGS_USD, CREDIT_CARD_CAD = tuple(
        [sorted(account.tolist(), key=lambda x: x.get('date')) for account in
         c.accounts])  # grab each account seperately
    transactions = c.sumAccounts().tolist()  # all accounts together
    transactions = sorted(transactions, key=lambda x: x.get('date'))

    # print(account)
    # print(len(account.diff()))
    # print(len(account.tolist()))