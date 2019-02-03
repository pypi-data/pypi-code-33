import os
import requests
import datetime
import re
import warnings
import json

# holds particular account details
class Details():
    def __init__(self, liabilityType=None, businessCardHolderRole=None, spendLimitSet=None, accessLevel=None,
                 cardHolderType=None, familyCardEnabled=None, creditCardStatus=None, **kwargs):
        # locals
        self.liabilityType = liabilityType
        self.businessCardHolderRole = businessCardHolderRole
        self.spendLimitSet = spendLimitSet
        self.accessLevel = accessLevel
        self.cardHolderType = cardHolderType
        self.familyCardEnabled = familyCardEnabled
        self.creditCardStatus = creditCardStatus

        # information
        self.information = {
            'liabilityType':self.liabilityType,
            'businessCardHolderRole': self.businessCardHolderRole,
            'spendLimitSet': self.spendLimitSet,
            'accessLevel': self.accessLevel,
            'cardHolderType': self.cardHolderType,
            'familyCardEnabled': self.familyCardEnabled,
            'creditCardStatus': self.creditCardStatus
        }

    def set(self,details_json):
        self.liabilityType = details_json.get('liabilityType','')
        self.businessCardHolderRole = details_json.get('businessCardHolderRole','')
        self.spendLimitSet = details_json.get('spendLimitSet','')
        self.accessLevel = details_json.get('accessLevel','')
        self.cardHolderType = details_json.get('cardHolderType','')
        self.familyCardEnabled = details_json.get('familyCardEnabled','')

        # information
        self.information = {
            'liabilityType':self.liabilityType,
            'businessCardHolderRole': self.businessCardHolderRole,
            'spendLimitSet': self.spendLimitSet,
            'accessLevel': self.accessLevel,
            'cardHolderType': self.cardHolderType,
            'familyCardEnabled': self.familyCardEnabled
        }

# holds particular account information
class Account():
    def __init__(self, id=None, capabilities=None, external=None, transit=None, taxPlan=None, extraSubCategory=None,
                 category=None, subCategory=None, holding=None, instance=None, availableFunds=None, currency=None,
                 _type=None, number=None, details=None, balance=None, status=None, nickname=None, X_auth_token=None,
                 cookies=None, session=None):
        # details
        if details:
            self.details = Details(**account_json.get('details'))
        else:
            self.details = Details()

        # locals
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
        self.balance = balance
        self.status = status
        self.nickname = nickname

        # transaction related variables
        self.X_auth_token = X_auth_token
        self.cookies = cookies
        self.session= session
        self.transactions = []

        # local infromation data
        self.information = {
            'id':self.id,
            'capabilities':self.capabilities,
            'external':self.external,
            'transit':self.transit,
            'taxPlan':self.taxPlan,
            'extraSubCategory':self.extraSubCategory,
            'category':self.category,
            'subCategory':self.subCategory,
            'holding':self.holding,
            'instance':self.instance,
            'availableFunds':self.availableFunds,
            'currency':self.currency,
            '_type':self._type,
            'number':self.number,
            'balance': self.balance,
            'status': self.status,
            'nickname': self.nickname,
            'details': self.details.information,
        }

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
        self.availableFunds = account_json.get('availableFunds') or 0
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
        self.balance = account_json.get('balance') or 0
        self.information = {
            'id':self.id,
            'capabilities':self.capabilities,
            'external':self.external,
            'transit':self.transit,
            'taxPlan':self.taxPlan,
            'extraSubCategory':self.extraSubCategory,
            'category':self.category,
            'subCategory':self.subCategory,
            'holding':self.holding,
            'instance':self.instance,
            'availableFunds':self.availableFunds,
            'currency':self.currency,
            '_type':self._type,
            'number':self.number,
            'balance': self.balance,
            'status': self.status,
            'nickname': self.nickname,
            'details': self.details.information,
        }

    def __repr__(self):
        return "{}_{}".format(self.subCategory, self.currency)

    def __str__(self):
        return "{}_{}".format(self.subCategory, self.currency)

    # if we aren't adding another account, return itself
    def __radd__(self, other):
        return self

    def __rsub__(self, other):
        return self

    # if we are adding another account, return an Account() of both accounts transactions,
    # change account metadata to represent account type "combination"
    def __add__(self, other):
        if self.currency != other.currency:
            warnings.warn("Invalid Account Addition between different currencies! Addition will result in base Account")
            return self
        newAccount = Account(id=-1,
                             category='Combination',
                             subCategory='Combination',
                             currency=self.currency,
                             availableFunds = self.availableFunds + other.availableFunds,
                             balance= self.balance + other.balance)
        newAccount.pass_connection(self.X_auth_token, self.cookies, self.session)
        newAccount.transactions = self.transactions + other.transactions
        return newAccount

    # subtracts account balances from each other.
    def __sub__(self, other):
        if self.currency != other.currency:
            warnings.warn("Invalid Account Subtraction between different currencies! Subtraction will result in base Account")
            return self
        newAccount = Account(id=-1,
                             category='Combination',
                             subCategory='Combination',
                             currency=self.currency,
                             availableFunds = self.availableFunds - other.availableFunds,
                             balance= self.balance - other.balance)
        newAccount.pass_connection(self.X_auth_token, self.cookies, self.session)
        newAccount.transactions = list(set(self.transactions) - set(other.transactions))
        return newAccount

    # pass session cookies and X_auth_token
    def pass_connection(self, X_auth_token, cookies, session):
        self.X_Auth_Token = X_auth_token
        self.cookies = cookies
        self.session = session

    # takes start and end dates and interval.  Produces list of times spanning interval from the start to the end date.
    # returns date generator.  For list, simply return list of elements instead
    def dateTimeLine(self, startDate, endDate, interval=datetime.timedelta(days=60)):
        while startDate < endDate:
            yield [startDate, startDate + interval - datetime.timedelta(days=1)]
            startDate = startDate + interval

    # get the credits/debits since datefrom until dateuntil.  use the existing X auth Token and cookies provided
    # max can get 250 charges per call, if you do more, timesplit should be lower, if you do less, timesplit should be higher
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
            url = "https://www.cibconline.cibc.com/ebm-ai/api/v1/json/transactions?accountId={}&filterBy=range&fromDate={}&lastFilterBy=range&limit=250&lowerLimitAmount=&offset=0&sortAsc=true&sortByField=date&toDate={}&transactionLocation=&transactionType=&upperLimitAmount=".format(
                    account_id,
                    dateFrom.strftime("%Y-%m-%d"),
                    dateUntil.strftime("%Y-%m-%d")
                )
            t_request = self.session.get(
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
                }
            )
            try:
                transactions += t_request.json()['transactions']
            except Exception as e:
                continue
        for transaction in transactions:
            self.transactions.append(Transaction(**transaction))
        return [ele.information for ele in self.transactions]

    # send one account's data to a CSV file
    def tocsv(self, filepath):
        headers = ['id','customCategoryId','merchantCategoryId','transactionLocation','pendingIndicator','postedDate',
                  'runningBalance', 'debit', 'fitId', 'transactionDescription','date', 'billableIndicator',
                   'paymentMethod', 'transactionType', 'transactionTypeDescription','units', 'credit', 'unitPrice',
                   'showChequeImage', 'showRunningBalance']
        with open(filepath, 'w') as file:
            file.write(','.join(headers) + '\n')
            for transaction in self.transactions:
                attributes = [str(transaction.__getattribute__(attr)) for attr in headers]
                file.write(','.join(attributes) + '\n')

    # remove any (exactly 2) transactions that are one credit and one debit of the same amount
    # O(nlogn)
    def diff(self):
        trcs = list(sorted(self.transactions, key=lambda x: (x.debit if x.debit else 0) + (x.credit if x.credit else 0)))
        i = 1 # we don't need to check the first element of the list
        trcs_len = len(trcs)
        while i < trcs_len:
            if trcs[i].transactionType == "Debit" and trcs[i-1].transactionType == "Credit":
                if trcs[i].debit == trcs[i-1].credit:
                    trcs.pop(i)
                    trcs.pop(i-1)
                    trcs_len -= 2
                    i -= 1
            if trcs[i].transactionType == "Credit" and trcs[i - 1].transactionType == "Debit":
                if trcs[i].credit == trcs[i-1].debit:
                    trcs.pop(i)
                    trcs.pop(i - 1)
                    trcs_len -= 2
                    i -= 1
            i+=1
        return [ele.information for ele in trcs]

    # send one account's data to a list of dict's
    def tolist(self):
        return [ele.information for ele in self.transactions]

# holds particular Transaction information
class Transaction():
    def __init__(self,id=None, customCategoryId=None, merchantCategoryId=None, transactionLocation=None, pendingIndicator=None,
                 postedDate = None, runningBalance=None, accountId=None, creditCardNumber=None, debit=None, fitId=None,
                 transactionDescription=None, date=None, billableIndicator=None, paymentMethod=None, transactionType=None,
                 transactionTypeDescription=None, units=None, credit=None, unitPrice=None, showChequeImage=None, showRunningBalance=None,
                 hasCleansedMerchantInfo=None, descriptionLine1=None, **kwargs):
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
        self.hasCleansedMerchantInfo = hasCleansedMerchantInfo
        self.descriptionLine1 = descriptionLine1

        # clean data a little
        self.type_indicator()

        # information
        self.information = {
            'id': self.id,
            'customCategoryId': self.customCategoryId,
            'merchantCategoryId': self.merchantCategoryId,
            'transactionLocation': self.transactionLocation,
            'pendingIndicator': self.pendingIndicator,
            'postedDate': self.postedDate,
            'runningBalance': self.runningBalance,
            'accountId': self.accountId,
            'creditCardNumber': self.creditCardNumber,
            'debit': self.debit,
            'fitId': self.fitId,
            'transactionDescription': self.transactionDescription,
            'date': self.date,
            'billableIndicator': self.billableIndicator,
            'paymentMethod': self.paymentMethod,
            'transactionType': self.transactionType,
            'transactionTypeDescription': self.transactionTypeDescription,
            'units': self.units,
            'credit': self.credit,
            'unitPrice': self.unitPrice,
            'showChequeImage': self.showChequeImage,
            'showRunningBalance': self.showRunningBalance,
            'hasCleansedMerchantInfo': self.hasCleansedMerchantInfo,
            'descriptionLine1': self.descriptionLine1,
        }

    def type_indicator(self):
        if self.credit:
            self.transactionType = "Credit"
        elif self.debit:
            self.transactionType = "Debit"

    def __repr__(self):
        return 'TRANSACTION_{}'.format(self.id)

    def __str__(self):
        return 'TRANSACTION_{}'.format(self.id)

    def __hash__(self):
        return str(self.accountId) + str(self.id) + str(self.postedDate)

    def __eq__(self, other):
        if str(self.accountId) + str(self.id) + str(self.postedDate) == str(other.accountId) + str(other.id) + str(other.postedDate):
            return True
        else:
            return False

    def todict(self):
        return self.information

# pull data from CIBC API and format it
class CIBC():
    def __init__(self, cardnumber, password):
        self.initialize()
        self.auth(cardnumber,password)
        self.accounts = []

    def initialize(self):
        '''
        makes an initial request to the cibc banking page index.
        :return:
        '''
        self.session = requests.Session()
        req1 = self.session.get(
            url="https://www.cibconline.cibc.com/",
            headers={
                "Host": "www.cibconline.cibc.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
        )
        req2 = self.session.get(
            url="https://www.cibconline.cibc.com/ebm-resources/public/banking/cibc/client/web/index.html#/signon",
            headers={
                "Host": "www.cibconline.cibc.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "TE": "Trailers"
            }
        )
        req3 = self.session.get(
            url="https://www.cibconline.cibc.com/akam/10/21cb902b",
            headers={
                "Host": "www.cibconline.cibc.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.cibconline.cibc.com/ebm-resources/public/banking/cibc/client/web/index.html",
                "DNT": "1",
                "Connection": "keep-alive",
                "TE": "Trailers"
            }
        )
        # req35 = self.session.post(
        #     url="https://www.cibconline.cibc.com/public/7f31c57c3218b5ab63ab8a0b4633c",
        #     headers={
        #         "Host": "www.cibconline.cibc.com",
        #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
        #         "Accept": "*/*",
        #         "Accept-Language": "en-US,en;q=0.5",
        #         "Accept-Encoding": "gzip, deflate, br",
        #         "Referer": "https://www.cibconline.cibc.com/ebm-resources/public/banking/cibc/client/web/index.html",
        #         "DNT": "1",
        #         "Connection": "keep-alive",
        #         "TE": "Trailers"
        #     },
        #     data=json.dumps({
        #         "sensor_data": "7a74G7m23Vrp0o5c9055411.4-1,2,-94,-100,Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0,uaend,11059,20100101,en-US,Gecko,0,0,0,0,381179,2759398,1920,1080,1920,1080,1922,967,1936,,cpen:0,i1:0,dm:0,cwen:0,non:1,opc:0,fc:1,sc:0,wrc:1,isc:74,vib:1,bat:0,x11:0,x12:1,5555,0.503556164251,774606379698.5,loc:-1,2,-94,-101,do_en,dm_en,t_dis-1,2,-94,-105,-1,2,-94,-102,-1,2,-94,-108,-1,2,-94,-110,-1,2,-94,-117,-1,2,-94,-111,-1,2,-94,-109,-1,2,-94,-114,-1,2,-94,-103,-1,2,-94,-112,https://www.cibconline.cibc.com/ebm-resources/public/banking/cibc/client/web/index.html#/signon-1,2,-94,-115,1,0,0,0,0,0,0,3,0,1549212759397,-999999,16573,0,0,2762,0,0,11,0,0,C566197C6EF78151E0328135624FDC8717D782F6884A0000541C575C05824E56~-1~sojTK8oGy/mWOn6T+czYbPV0CYFRhmgEj4JqzXJXNGw=~-1~-1,8182,-1,-1,25543097-1,2,-94,-106,0,0-1,2,-94,-119,-1-1,2,-94,-122,0,0,0,0,1,0,0-1,2,-94,-123,-1,2,-94,-70,-1-1,2,-94,-80,94-1,2,-94,-116,24834604-1,2,-94,-118,54695-1,2,-94,-121,;10;-1;0"
        #     })
        # )
        ## ignoring post JSON request
        req4 = self.session.get(
            url="https://www.cibconline.cibc.com/ebm-anp/api/v1/json/clientProperties/online",
            headers={
                "Host": "www.cibconline.cibc.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
                "Accept": "application/vnd.api+json",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.cibconline.cibc.com/ebm-resources/public/banking/cibc/client/web/index.html",
                "X-Requested-With": "XMLHttpRequest",
                "DNT": "1",
                "Connection": "keep-alive",
                "TE": "Trailers"
            }
        )
        req5 = self.session.get(
            url="https://www.cibconline.cibc.com/ebm-resources/public/banking/cibc/config/ManageMyCard_Config.json",
            headers={
                "Host": "www.cibconline.cibc.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.cibconline.cibc.com/ebm-resources/public/banking/cibc/client/web/index.html",
                "X-Requested-With": "XMLHttpRequest",
                "DNT": "1",
                "Connection": "keep-alive",
                "TE": "Trailers"
            }
        )
        req6 = self.session.get(
            url="https://www.cibconline.cibc.com/ebm-resources/public/banking/cibc/content/web/views/application?locale=en&brand=cibc&channel=web",
            headers={
                "Host": "www.cibconline.cibc.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.cibconline.cibc.com/ebm-resources/public/banking/cibc/client/web/index.html",
                "X-Requested-With": "XMLHttpRequest",
                "DNT": "1",
                "Connection": "keep-alive",
                "TE": "Trailers"
            }
        )

    def auth(self, cardnumber, password):
        authenticate_request = self.session.post(
            url="https://www.cibconline.cibc.com/ebm-anp/api/v1/json/sessions",
            json={"card": {"value": "{}".format(cardnumber), "description": "", "encrypted": False, "encrypt": True},
                  "password": "{}".format(password)},
            headers={
                "Host": "www.cibconline.cibc.com",
                # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
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

    # returns accounts
    def Accounts(self):
        login_request = self.session.get(
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
            account_instance.pass_connection(self.X_Auth_Token, self.cookies, self.session)
            acc_title = "{}_{}".format(account_instance.subCategory, account_instance.currency)
            self.__setattr__(acc_title, account_instance)
            self.accounts.append(account_instance)
        return self.accounts

    # aquires transactions for all given accounts (takes list of accounts).  If no accounts given, uses self.accounts
    def gTransactions(self, dateFrom, dateUntil, accounts=None):
        if not accounts:
            accounts = self.accounts
            if not self.accounts:
                raise Exception("No accounts to sum")
        for account in accounts:
            account.aquireTransactions(dateUntil=dateUntil, dateFrom=dateFrom)
        return accounts

    # sums accounts (takes list of accounts).  If no accounts are given, sums self.accounts
    def sumAccounts(self,accounts=None):
        if not accounts:
            accounts = self.accounts
            if not self.accounts:
                raise Exception("No accounts to sum")
        return sum(accounts)

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

