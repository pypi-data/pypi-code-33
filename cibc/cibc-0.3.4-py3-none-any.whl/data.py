import os
import requests
import datetime
import re

# holds particular account details
class Details():
    def __init__(self, liabilityType=None, businessCardHolderRole=None, spendLimitSet=None, accessLevel=None,
                 cardHolderType=None, familyCardEnabled=None):
        self.liabilityType = liabilityType
        self.businessCardHolderRole = businessCardHolderRole
        self.spendLimitSet = spendLimitSet
        self.accessLevel = accessLevel
        self.cardHolderType = cardHolderType
        self.familyCardEnabled = familyCardEnabled

    def set(self,details_json):
        self.liabilityType = details_json.get('liabilityType','')
        self.businessCardHolderRole = details_json.get('businessCardHolderRole','')
        self.spendLimitSet = details_json.get('spendLimitSet','')
        self.accessLevel = details_json.get('accessLevel','')
        self.cardHolderType = details_json.get('cardHolderType','')
        self.familyCardEnabled = details_json.get('familyCardEnabled','')

# holds particular account information
class Account():
    def __init__(self, id=None, capabilities=None, external=None, transit=None, taxPlan=None, extraSubCategory=None,
                 category=None, subCategory=None, holding=None, instance=None, availableFunds=None, currency=None,
                 _type=None, number=None, details=None, balance=None, status=None, nickname=None, X_auth_token=None,
                 cookies=None):
        self.id = id
        self.capabilities = capabilities
        self.external = external
        self.transit = transit
        self.taxPlan = taxPlan
        self.extraSubCategory = extraSubCategory
        self.category = category
        self.subCategory = subCategory
        self.holding = holding
        self.instance = instance
        self.availableFunds = availableFunds
        self.currency = currency
        self._type = _type
        self.number = number
        self.details = details
        self.balance = balance
        self.status = status
        self.nickname = nickname

        # transaction related variables
        self.X_auth_token = X_auth_token
        self.cookies = cookies
        self.transactions = []

    # takes json from CIBC API and maps to instance
    def set(self,account_json):
        self.capabilities = account_json.get('capabilities','')
        self.external = account_json.get('external','')
        self.transit = account_json.get('transit','')
        self.taxPlan = account_json.get('categorization',{}).get('taxPlan','')
        self.extraSubCategory = account_json.get('categorization',{}).get('extraSubCategory','')
        self.category = account_json.get('categorization',{}).get('category','')
        self.subCategory = account_json.get('categorization',{}).get('subCategory','')
        self.holding = account_json.get('categorization',{}).get('holding','')
        self.instance = account_json.get('categorization',{}).get('instance','')
        self.availableFunds = account_json.get('availableFunds','')
        self.id = account_json['id']
        self.status = account_json.get('status','')
        self.nickname = account_json.get('nickname','')
        self.currency = account_json.get('currency','')
        self._type = account_json.get('_type','')
        self.number = account_json.get('number','')
        if account_json.get('details'):
            self.details = Details(**account_json.get('details'))
        else:
            self.details = Details()
        self.balance = account_json.get('balance','')

    # pass session cookies and X_auth_token
    def pass_connection(self, X_auth_token, cookies):
        self.X_Auth_Token = X_auth_token
        self.cookies = cookies

    # takes start and end dates and interval.  Produces list of times spanning interval from the start to the end date.
    # returns date generator.  For list, simply return list of elements instead
    def dateTimeLine(self, startDate, endDate, interval=datetime.timedelta(days=60)):
        while startDate < endDate:
            yield [startDate, startDate + interval - datetime.timedelta(days=1)]
            startDate = startDate + interval

    # get the credits/debits since datefrom until dateuntil.  use the existing X auth Token and cookies provided
    # max can get 250 charges per call, if you do more, timeplit should be lower, if you do less, timesplit should be higher
    def aquireTransactions(self, dateFrom=None,dateUntil=None, timesplit=120):
        account_id = self.id
        if not dateFrom:
            dateFrom = datetime.datetime(day=1,month=1,year=2013)
        if not dateUntil:
            dateUntil=datetime.datetime.now()
        times = self.dateTimeLine(startDate=dateFrom, endDate=dateUntil, interval=datetime.timedelta(timesplit))
        transactions = []
        for time in times:
            dateFrom = time[0]
            dateUntil = time[1]
            print(dateFrom, dateUntil)
            url = "https://www.cibconline.cibc.com/ebm-ai/api/v1/json/transactions?accountId={}&filterBy=range&fromDate={}&lastFilterBy=range&limit=250&lowerLimitAmount=&offset=0&sortAsc=true&sortByField=date&toDate={}&transactionLocation=&transactionType=&upperLimitAmount=".format(
                    account_id,
                    dateFrom.strftime("%Y-%m-%d"),
                    dateUntil.strftime("%Y-%m-%d")
                )
            t_request = requests.get(
                url=url,
                headers={
                    "Host": "www.cibconline.cibc.com",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
                    "Accept": "application/vnd.api+json",
                    "Accept-Language": "en",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Referer": "https://www.cibconline.cibc.com/ebm-resources/public/banking/cibc/client/web/index.html",
                    "Content-Type": "application/vnd.api+json",
                    "Client-Type": "default_web",
                    "brand": "cibc",
                    "X-Auth-Token": self.X_Auth_Token,
                    "X-Requested-With": "XMLHttpRequest",
                    "Connection": "keep-alive",
                },
                cookies=self.cookies
            )
            try:
                transactions += t_request.json()['transactions']
            except:
                continue
            print(len(t_request.json()['transactions']))
        for transaction in transactions:
            self.transactions.append(Transaction(**transaction))
        return self

    # send one account's data to a CSV file
    def tocsv(self, filename):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_dir = os.path.join(script_dir, filename)
        headers = ['id','customCategoryId','merchantCategoryId','transactionLocation','pendingIndicator','postedDate',
                  'runningBalance', 'debit', 'fitId', 'transactionDescription','date', 'billableIndicator',
                   'paymentMethod', 'transactionType', 'transactionTypeDescription','units', 'credit', 'unitPrice',
                   'showChequeImage', 'showRunningBalance']
        with open(file_dir, 'w') as file:
            file.write(','.join(headers) + '\n')
            for transaction in self.transactions:
                attributes = [str(transaction.__getattribute__(attr)) for attr in headers]
                file.write(','.join(attributes) + '\n')


# holds particular Transaction information
class Transaction():
    def __init__(self,id=None, customCategoryId=None, merchantCategoryId=None, transactionLocation=None, pendingIndicator=None,
                 postedDate = None, runningBalance=None, accountId=None, creditCardNumber=None, debit=None, fitId=None,
                 transactionDescription=None, date=None, billableIndicator=None, paymentMethod=None, transactionType=None,
                 transactionTypeDescription=None, units=None, credit=None, unitPrice=None, showChequeImage=None, showRunningBalance=None):
        self.id = id
        self.customCategoryId = customCategoryId
        self.merchantCategoryId = merchantCategoryId
        self.transactionLocation = transactionLocation
        self.pendingIndicator = pendingIndicator
        self.postedDate = postedDate
        self.runningBalance = runningBalance
        self.accountId = accountId
        self.creditCardNumber = creditCardNumber
        self.debit = debit
        self.fitId = fitId
        self.transactionDescription = transactionDescription
        self.date = date
        self.billableIndicator = billableIndicator
        self.paymentMethod = paymentMethod
        self.transactionType = transactionType
        self.transactionTypeDescription = transactionTypeDescription
        self.units=units
        self.credit = credit
        self.unitPrice = unitPrice
        self.showChequeImage = showChequeImage
        self.showRunningBalance = showRunningBalance
        # clean data a little
        self.type_indicator()

    def type_indicator(self):
        if self.credit:
            self.transactionType = "Credit"
        elif self.debit:
            self.transactionType = "Debit"

    def __getattrs__(self, *args):
        for arg in args:
            return self.__getattribute__()

# pull data from CIBC API and format it
class CIBC():
    def __init__(self):
        self.accounts = []

    def auth(self, cardnumber, password):
        authenticate_request = requests.post(
            url="https://www.cibconline.cibc.com/ebm-anp/api/v1/json/sessions",
            json={"card": {"value": "{}".format(cardnumber), "description": "", "encrypted": False, "encrypt": True},
                  "password": "{}".format(password)},
            headers={
                "Host": "www.cibconline.cibc.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
                "Accept": "application/vnd.api+json",
                "Accept-Language": "en",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.cibconline.cibc.com/ebm-resources/public/banking/cibc/client/web/index.html",
                "Content-Type": "application/vnd.api+json",
                "Client-Type": "default_web",
                "X-Auth-Token": "",
                "brand": "cibc",
                "WWW-Authenticate": "CardAndPassword",
                "X-Requested-With": "XMLHttpRequest",
                "Content-Length": "112",
                "Connection": "keep-alive",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache"
            }
        )
        cookies = dict(authenticate_request.cookies)
        self.cookies = cookies
        authenticate_response_headers = authenticate_request.headers
        X_Auth_Token = authenticate_response_headers['X-Auth-Token']
        self.X_Auth_Token = X_Auth_Token
        return cookies,X_Auth_Token

    # returns generator of accounts
    def Accounts(self):
        login_request = requests.get(
            url="https://www.cibconline.cibc.com/ebm-ai/api/v2/json/accounts",
            headers={
                "Host": "www.cibconline.cibc.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
                "Accept": "application/vnd.api+json",
                "Accept-Language": "en",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.cibconline.cibc.com/ebm-resources/public/banking/cibc/client/web/index.html",
                "Content-Type": "application/vnd.api+json",
                "Client-Type": "default_web",
                "brand": "cibc",
                "X-Auth-Token": self.X_Auth_Token,
                "X-Requested-With": "XMLHttpRequest",
                "Connection": "keep-alive",
            },
            cookies=self.cookies
        )
        login_request_response = login_request.json()
        accounts_json = login_request_response['accounts']
        for acc in accounts_json:
            account_instance = Account()
            account_instance.set(acc)
            account_instance.pass_connection(self.X_Auth_Token, self.cookies)
            acc_title = "{}_{}".format(account_instance.subCategory, account_instance.currency)
            self.__setattr__(acc_title, account_instance)
            self.accounts.append(acc_title)

    # If an amount if both credited and debited, that amount is removed from our consideration.
    def removeRepeats(self):
        transaction = list(self.transactions)
        Credits = list(filter(lambda x: x['transaction'] == 'Credit',transaction))
        Debits = list(filter(lambda x: x['transaction'] == 'Debit',transaction))
        DebitPool = [ele['amount'] for ele in Debits]
        CreditPool = [ele['amount'] for ele in Credits]
        properDebits = list(filter(lambda x: x['amount'] not in CreditPool,Debits))
        properCredits = list(filter(lambda x: x['amount'] not in DebitPool, Credits))
        return properCredits + properDebits
