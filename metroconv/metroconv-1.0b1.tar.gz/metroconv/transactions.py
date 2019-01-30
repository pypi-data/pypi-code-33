
from decimal import Decimal


class TransactionRecord(object):

    _date = None
    _amount = None
    _description = None

    def __repr__(self):
        return '<TransactionRecord: [{}] [{}] [{}]>'.format(
            self._date,
            self._amount,
            self._description
        )

    def __init__(self, date, amount, description):
        self._date = date
        self._amount = amount
        self._description = description

    @property
    def date(self):
        return self._date

    @property
    def description(self):
        return self._description

    @property
    def amount(self):
        return self._amount


class Transactions(object):

    _records = None

    def __init__(self):
        self._records = []

    def __repr__(self):
        return '<Transactions: {} items>'.format(len(self._records))

    def append(self, record):
        self._records.append(record)

    def __iter__(self):
        for item in self._records:
            yield item

    @classmethod
    def from_records(cls, iterable):
        obj = cls()
        for item in iterable:
            obj.append(item)
        return obj


class FromMetroAdapter(object):

    _csv = None

    def __init__(self, csv_object):
        self._csv = csv_object

    def __iter__(self):
        for item in self._csv.contents:
            record = TransactionRecord(
                date=item['Date'],
                amount=Decimal(item['Money In']) - Decimal(item[' Money Out']),
                description=item['Reference']
            )
            yield record


class ToFreeAgentAdapter(object):

    _transactions = None

    def __init__(self, transactions_object):
        assert isinstance(transactions_object, Transactions)
        self._transactions = transactions_object

    def __iter__(self):
        for item in self._transactions:
            assert isinstance(item, TransactionRecord)
            line = (item.date, item.amount, item.description)
            yield line
