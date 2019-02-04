from datetime import date

import re
import requests
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta


def get_filename(session, link):
    rf = session.head(link)
    assert rf.ok, "HEAD failed when reading filename"
    filename = (
        rf.headers["Content-Disposition"]
        .encode("latin-1")
        .decode("utf-8")
        .replace("attachment; filename=", "")
    )
    return filename


class CongstarDocDownloader:
    def __init__(self):
        self._session = requests.session()
        self._logged_in = False

    def login(self, username, password):
        r_login = self._session.post(
            "https://www.congstar.de/api/auth/login",
            data={
                "defaultRedirectUrl": "/meincongstar",
                "username": username,
                "password": password,
                "targetPageUrlOrId": None,
            },
        )
        assert r_login.ok

        self._logged_in = True

    def list(self):
        r = self._session.get("https://www.congstar.de/meincongstar/meine-rechnungen/")
        assert r.ok

        german_months = {
            "Januar": 1,
            "Februar": 2,
            "März": 3,
            "April": 4,
            "Mai": 5,
            "Juni": 6,
            "Juli": 7,
            "August": 8,
            "September": 9,
            "Oktober": 10,
            "November": 11,
            "Dezember": 12,
        }

        soup = BeautifulSoup(r.content, "lxml")
        docs = [
            {
                "filename": get_filename(
                    self._session, "https://www.congstar.de/" + l.attrs["href"]
                ),
                "link": "https://www.congstar.de/" + l.attrs["href"],
                "date": date(
                    int(re.findall(r"\w+ (\d+)", tr.find("td").text)[0]),
                    german_months[re.findall("(\w+) \d+", tr.find("td").text)[0]],
                    25,
                )
                + relativedelta(
                    months=1
                ),  # Lastschrift kommt meist so um den 25ten rum
            }
            for tr in soup.find("div", {"id": "usageData"})
            .find("table")
            .find_all("tr")[1:]
            for l in tr.find_all("a")
        ]
        return docs

    def download(self, doc):
        assert self._logged_in, "not logged in"
        r = self._session.get(doc["link"])
        assert r.ok, "download failed"
        return r.content
