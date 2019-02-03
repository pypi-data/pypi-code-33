import requests
from bs4 import BeautifulSoup
from datetime import datetime
from os import path


def _coba_req(session, form_url, form_id, params):
    r = session.get(form_url)
    assert r.ok
    soup = BeautifulSoup(r.content, "lxml")
    form = soup.find("form", {"id": form_id})
    action = form.attrs["action"]
    post_params = {
        e.attrs["name"]: e.attrs["value"] if "value" in e.attrs else ""
        for e in form.find_all("input")
        if "name" in e.attrs
    }
    post_params.update(params)
    r_post = session.post("https://kunde.comdirect.de" + action, data=post_params)
    assert r_post.ok
    assert "Zugangsnummer" not in str(r_post.content), "not logged in"
    return r_post


class CobaDocDownloader:
    def __init__(self):
        self._session = requests.session()
        self._logged_in = False

    def login(self, username, password):
        _coba_req(
            self._session,
            "https://kunde.comdirect.de/",
            "login",
            {
                "param1": username,
                "param3": password,
                "direktzu": "PersoenlicherBereich",
                "loginAction": "loginAction",
            },
        )
        self._logged_in = True

    def list(self):
        assert self._logged_in, "not logged in"

        # postbox
        p = _coba_req(
            self._session,
            "https://kunde.comdirect.de/itx/posteingangsuche",
            "f1",
            {
                "f1-sucheStarten": "f1-sucheStarten",
                "f1-zeitraumInput_pb": "GESAMTER_ZEITRAUM",
                "f1-docTyp": 0,
            },
        )

        soup = BeautifulSoup(p.content, "lxml")

        docs = [
            {
                "date": datetime.strptime(
                    tr.find_all("td")[2].find("span", {"class": "output-text"}).text,
                    "%d.%m.%Y",
                ).date(),
                "filename": path.basename(tr.find("a").attrs["href"]),
                "link": "https://kunde.comdirect.de" + tr.find("a").attrs["href"],
            }
            for tr in soup.find("table", {"id": "f1-posteingangDokumente"}).find_all(
                "tr"
            )
        ]

        return docs

    def download(self, doc):
        assert self._logged_in, "not logged in"
        r = self._session.get(doc["link"])
        assert r.ok, "download failed"
        return r.content
