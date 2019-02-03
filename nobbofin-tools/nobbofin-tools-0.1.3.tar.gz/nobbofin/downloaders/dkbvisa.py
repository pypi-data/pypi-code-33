from bs4 import BeautifulSoup
from datetime import datetime
import requests


def read_dkbvisa(username, password):
    session = requests.session()
    r = session.get("https://www.dkb.de/-")
    r_soup = BeautifulSoup(r.content, "lxml")
    data = {
        i.attrs["name"]: i.attrs["value"] if "value" in i.attrs else ""
        for i in r_soup.find("form", {"id": "login"}).find_all("input")
    }
    data["j_username"] = username
    data["j_password"] = password
    res = session.post("https://www.dkb.de/banking", data=data)

    # check login success
    assert (
        res.url
        == "https://www.dkb.de/DkbTransactionBanking/content/banking/financialstatus/FinancialComposite/FinancialStatus.xhtml?$event=init"
    )

    # query last 90 days
    res2 = session.post(
        "https://www.dkb.de/banking/finanzstatus/kreditkartenumsaetze",
        data={
            "slAllAccounts": "1",
            "slTransactionStatus": "0",
            "filterType": "PERIOD",
            "slSearchPeriod": "3",
            "postingDate": "",
            "toPostingDate": "",
            "$event": "search",
        },
    )
    res2_soup = BeautifulSoup(res2.content, "lxml")
    balance_date = datetime.strptime(
        res2_soup.find("div", {"class": "accountBalance"})
        .find("span")
        .text.strip()[10:],
        "%d.%m.%Y",
    ).date()

    # read CSV content
    res3 = session.get(
        "https://www.dkb.de/banking/finanzstatus/kreditkartenumsaetze?$event=csvExport"
    )
    csv_data = res3.text
    return balance_date, csv_data
