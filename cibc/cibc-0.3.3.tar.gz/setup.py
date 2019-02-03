from setuptools import setup

long_description = '''
# CIBC API Client Wrapper

This package provides a client wrapper around CIBC's API.  CIBC uses one API to handle requests from their web platform and app, specifically the API passes information about accounts, and transactions in those accounts.  This Wrapper makes it easy to gather that data in python, given the primary account card number and password.  Essentially, online banking through python.

## Getting Started

### Prerequisites

built for python 3.0 +, any operating system

```
pip install cibc
```

## Basic Usage

Start with logging into a CIBC account by calling the cibc.CIBC method using your username and login

```python
import cibc
c = cibc.CIBC('username (usually card number)', 'password')
```

Next, grab the accounts associated with this username and password (this is required, for any account specific information)

```python
c.Accounts()
accounts = c.accounts
```
The accounts, which is a list of account class', is now storing all the account specific information.  I'm no entirely sure what all of it is, but the account class variables are listed below.
To get the transactions:

```python
c.gTransactions(dateFrom=datetime.datetime(year=2018, month=9,day=1),dateUntil= datetime.datetime(year=2018, month=9, day=17))	
```
the gTransactions method gets all the transactions for all the accounts in the instance.  It is also easy to get them one by one using the aquireTransactions method as follows:

```python
for account in accounts:
	print(account.aquireTransactions())
```

which will return a list of transactions, each transaction being a dictionary of details.

Finally, there's an easy built in way to send the account transaction details to a csv file, or simply get a list of dictionaries without re-acquiring every transaction using the .tocsv() and .tolist() methods:

```python
for account in accounts:
    account.tocsv('C:\\Users\\louis\\Desktop\\{}.csv'.format(account))
    print(account.tolist())
```

## Summing and Subtracting Accounts

For your convenience, there's an easy way to combine accounts for looking at all transactions at once.  The addition and subtraction methods are well defined for account classes and can be used like this:

```python
omniAccount = sum(c.accounts) # all the account transactions in one account.  Account specific variables are lost
nomniAccount = c.accounts[0] - c.accounts[1]
```

Account subtraction returns an account instance with a balance of the first account balance minus the other account balance.  It also holds the list of transactions excluding ones in account 1 that are also in account 2.
	

## Contributing

thanks CIBC, for the API as well as being big enough for this to be relevant.

## Versioning

We use (http://semver.org/) for versioning. For the versions available, see the (https://github.com/louismillette/CIBC). 

## Authors

* **Louis Millette**

## License

This project is licensed under the MIT License

## Acknowledgments

* CIBC.  It's a good bank.

## Notice

I have been informed that useing this repository is a violation of the terms of service for CIBC's online banking agreement.
'''

setup(name='cibc',
      version='0.3.3',
      description='Client library to support the Canadian Imperial Bank of Canadas API',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/louismillette/CIBC',
      author='Louis Millette',
      author_email='louismillette1@gmail.com',
      license='MIT',
      packages=['cibc'],
        install_requires=[
          'requests',
      ],
      include_package_data=True,
      zip_safe=False)
