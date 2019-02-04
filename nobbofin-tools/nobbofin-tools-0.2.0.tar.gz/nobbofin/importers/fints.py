import hashlib
import re
from datetime import timedelta
from os import path

from beancount.core import data, amount
from beancount.core.number import D
from beancount.ingest import importer, regression
import simplejson as json
from dateutil.parser import parse


def _parse_transaction_details(details, bank_name):
    """ extract partner and purpose from SEPA-encoded text """
    details = details.replace("\n", "")
    td = {
        x[0]: x[2]
        for x in re.findall(
            "\\?(\\d{2}([A-Z]+\\+)?)([\\w\\- \\.\\/,:]+[\\w\\-\\.\\/,:])", details
        )
    }

    if "24PURP+" in td and "25SVWZ+" in td:
        return (td["25SVWZ+"], td["24PURP+"])

    purp = td["00"] + ": " if "00" in td else ""
    part = ""

    for i in range(20, 30):
        if str(i) in td:
            purp += td[str(i)]

    for i in range(32, 34):
        if str(i) in td:
            part += td[str(i)]

    if part == "":
        part = bank_name

    return part, purp


def _parse_transaction(t_data, bank_name):
    partner = None
    purpose = None

    if "transaction_details" in t_data:
        details = t_data["transaction_details"]
        partner, purpose = _parse_transaction_details(details, bank_name)

    if "applicant_name" in t_data:
        partner = t_data["applicant_name"]

    if "deviate_applicant" in t_data:
        if (
            t_data["deviate_applicant"] is not None
            and t_data["deviate_applicant"] != ""
        ):
            da = t_data["deviate_applicant"].replace(partner, "")

            if len(da) > 0:
                partner += " %s" % da

    if "purpose" in t_data:
        purpose = t_data["purpose"]

    return partner, purpose


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


def find_balance(existing_entries, balance):
    if existing_entries is None:
        return False

    for e in existing_entries:
        if isinstance(e, data.Balance):
            if (
                e.account == balance.account
                and e.date == balance.date
                and e.amount == balance.amount
            ):
                return True
    return False


def _md5(some_dict):
    hash_id = hashlib.md5()
    hash_id.update(repr(some_dict).encode("utf-8"))
    return hash_id.hexdigest()


def get_hash(transaction):
    ignored_fields = ["entry_date"]
    stripped = {k: v for k, v in transaction.items() if k not in ignored_fields}
    return _md5(stripped)


class Importer(importer.ImporterProtocol):
    def __init__(
        self,
        account_name,
        bank_name,
        blz,
        min_import_date=None,
        expense_account="Expenses:AAAAAUNCLASSIFIED",
        income_account="Income:AAAAAUNCLASSIFIED",
    ):
        self.min_import_date = min_import_date
        self.blz = blz
        self.expense_account = expense_account
        self.income_account = income_account
        self.bank_name = bank_name
        self.account_name = account_name

    def name(self):
        return "FinTS Importer BLZ %s" % self.blz

    def file_account(self, file):
        return self.account_name

    def identify(self, file):
        m = re.match(r".*FinTS %s [^\.]+\.json$" % self.blz, file.name)
        return m is not None

    def extract(self, file, existing_entries=None):
        entries = []

        with open(file.name, "r", encoding="utf-8") as f:
            content = json.load(f, use_decimal=True)

        meta = data.new_metadata(file.name, 0)

        for t in content["statement"]:
            t_date = parse(t["date"]).date()
            link = t["extra_details"]

            if link == "":
                link = get_hash(t)

            if self.min_import_date is not None and t_date < self.min_import_date:
                continue

            if find_link(existing_entries, self.account_name, link):
                continue

            partner, purpose = _parse_transaction(t, self.bank_name)

            other_name = (
                self.expense_account
                if t["amount"]["amount"] < 0
                else self.income_account
            )

            entries.append(
                data.Transaction(
                    meta,
                    t_date,
                    self.FLAG,
                    partner,
                    purpose,
                    data.EMPTY_SET,
                    {link},
                    [
                        data.Posting(
                            self.account_name,
                            amount.Amount(
                                D(t["amount"]["amount"]), t["amount"]["currency"]
                            ),
                            None,
                            None,
                            None,
                            None,
                        ),
                        data.Posting(other_name, None, None, None, None, None),
                    ],
                )
            )

        bal = content["balance"]
        balance = data.Balance(
            meta,
            parse(bal["date"]).date()
            + timedelta(days=1),  # beancount considers start of day for the balance
            self.account_name,
            amount.Amount(D(bal["amount"]["amount"]), bal["amount"]["currency"]),
            None,
            None,
        )
        if not find_balance(existing_entries, balance):
            entries.append(balance)

        return entries
