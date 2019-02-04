from fints.client import FinTS3PinTanClient
from fints.dialog import FinTSDialogError


def _fix_amount(obj):
    return {k: (v.__dict__ if k == "amount" else v) for k, v in obj.items()}


def read_fints(blz, username, password, url, begin, end, tan_mechanism=None):

    try:
        client = FinTS3PinTanClient(blz, username, password, url)
        if tan_mechanism:
            client.set_tan_mechanism(tan_mechanism)
        with client:
            accounts = client.get_sepa_accounts()
            account = accounts[0]  # always use first account

            balance = client.get_balance(account)
            statement = client.get_transactions(account, begin, end)

            return {
                "balance": _fix_amount(balance.__dict__),
                "statement": [_fix_amount(t.data) for t in statement],
            }
    except FinTSDialogError as ex:
        print("error fetching transaction from", url)
        raise ex
