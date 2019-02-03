import csv
import hashlib
import itertools
import re
from datetime import datetime, timedelta
from decimal import Decimal
from os import path

from beancount.core import data, amount
from beancount.core.number import D
from beancount.ingest import importer


def read_transactions(filename):
    with open(filename, encoding="utf-8") as f:
        reader = csv.DictReader(
            itertools.islice(f, 6, None), delimiter=";", quotechar='"'
        )
        for x in reader:
            yield {
                "date": datetime.strptime(x["Wertstellung"], "%d.%m.%Y").date(),
                "date_receipt": datetime.strptime(x["Belegdatum"], "%d.%m.%Y").date(),
                "amount": Decimal(x["Betrag (EUR)"].replace(",", ".")),
                "partner": x["Beschreibung"],
            }


def read_balance(filename):
    with open(filename, encoding="utf-8") as f:
        reader = csv.reader(itertools.islice(f, 3, None), delimiter=";", quotechar='"')
        saldo = reader.__next__()[1].replace(" EUR", "")
        datum = datetime.strptime(reader.__next__()[1], "%d.%m.%Y").date()
    return saldo, datum


def find_link(existing_entries, account_name, link):
    if existing_entries is None:
        return False

    for e in existing_entries:
        if isinstance(e, data.Transaction):
            for p in e.postings:
                if p.account == account_name:
                    if link in e.links:
                        return True

    return False


def md5(some_dict):
    hash_id = hashlib.md5()
    hash_id.update(repr(some_dict).encode("utf-8"))
    return hash_id.hexdigest()


class Importer(importer.ImporterProtocol):
    def __init__(
        self,
        account_name,
        min_import_date=None,
        expense_account="Expenses:AAAAAUNCLASSIFIED",
        income_account="Income:AAAAAUNCLASSIFIED",
    ):
        self.min_import_date = min_import_date
        self.expense_account = expense_account
        self.income_account = income_account
        self.account_name = account_name

    def file_account(self, file):
        return self.account_name

    def identify(self, file):
        return re.match(r".* DKBVISA .*", path.basename(file.name))

    def extract(self, file, existing_entries=None):
        entries = []
        meta = data.new_metadata(file.name, 0)

        for t in read_transactions(file.name):
            if self.min_import_date is not None and t["date"] < self.min_import_date:
                continue

            other_name = (
                self.expense_account if t["amount"] < 0 else self.income_account
            )

            link = md5(t)

            if find_link(existing_entries, self.account_name, link):
                continue

            entries.append(
                data.Transaction(
                    meta,
                    t["date"],
                    self.FLAG,
                    t["partner"],
                    None,
                    data.EMPTY_SET,
                    {link},
                    [
                        data.Posting(
                            self.account_name,
                            amount.Amount(D(t["amount"]), "EUR"),
                            None,
                            None,
                            None,
                            None,
                        ),
                        data.Posting(other_name, None, None, None, None, None),
                    ],
                )
            )

        saldo, datum = read_balance(file.name)

        entries.append(
            data.Balance(
                meta,
                datum
                + timedelta(days=1),  # beancount considers start of day for the balance
                self.account_name,
                amount.Amount(D(saldo), "EUR"),
                None,
                None,
            )
        )

        return entries
