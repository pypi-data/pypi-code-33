"""
Advans_ERP_Checker will check data from Advans Group ERP
"""
import datetime
import json
import logging
import random
import re

import requests
import urllib3
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from workalendar.europe import France

# pylint: disable=no-member
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# pylint: enable=no-member

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

urllib3.disable_warnings()

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BASE_URL = "https://portail.advans-group.com/"

URLS = {
    "SET_ACTIVITY": f"{BASE_URL}ActivityReport/SetActivity?Length=",
    "GET_ACTIVITY": f"{BASE_URL}ActivityReport/GetActivity?Length=",
    "CLOSE_ACTIVITY": f"{BASE_URL}ActivityReport/CloseMonth?Length=",
    "LOGIN": f"{BASE_URL}Account/Login?ReturnUrl=/ActivityReport",
}


class AdvansERPChecker:
    def __init__(self, login=None, password=None):
        LOGGER.info("Opening session")
        self._length = 0
        self.tasks = []
        self.login = login
        self.password = password

        self._session = None

    def _login_erp_session(self):
        # Open login page and retrievers csrf token
        self._session = requests.sessions.Session()
        home_page = self._session.get(URLS["LOGIN"], verify=False, timeout=30)

        soup = BeautifulSoup(home_page.text, "html.parser")
        token = soup.select("input[name=__RequestVerificationToken]")[0]["value"]

        # Log in
        LOGGER.info("Logging in")

        credentials = None
        if credentials is None:
            credentials = {}

            credentials["login"] = self.login
            credentials["password"] = self.password

        now = datetime.datetime.now()

        res = self._session.post(
            URLS["LOGIN"],
            data={
                "month": now.month,
                "year": now.year,
                "UserName": credentials["login"],
                "Password": credentials["password"],
                "__RequestVerificationToken": token,
            },
        )

        # Extract "Length" attribute (don't know why it's necessary)
        soup = BeautifulSoup(res.text, "html.parser")
        # import pdb
        # pdb.set_trace()
        self._length = re.search(
            r".*\?Length=([0-9]+)$",
            soup.select("form[action*=GetActivity]")[0]["action"],
        ).group(1)
        return res

    def extract_activities(self):
        login_res = self._login_erp_session()

        tasks = list(set(re.findall(r'"affaires":(\[{.*?}\])', login_res.text)))
        if tasks:
            self.tasks = json.loads(tasks[0])
        else:
            LOGGER.warning("Couldn't retrievers tasks from page")
        self._session.close()

    def is_current_day_filled(self):
        workal = France()
        now = datetime.datetime.now()
        if workal.is_working_day(now):
            self._login_erp_session()
            res = self._session.get(
                URLS["GET_ACTIVITY"]
                + str(self._length)
                + "&month="
                + str(now.month - 1)
                + "&year="
                + str(now.year)
                + "&X-Requested-With=XMLHttpRequest&_="
                + str(random.randint(10000, 99999))
            )
            current_activities = res.json()
            existing_activities = {
                (acti["year"], acti["month"], acti["day"]): acti
                for acti in current_activities["data"]
            }
            today = (now.year, now.month, now.day)

            self._session.close()
            if today in existing_activities.keys():
                return True
            return False
        return True

    @staticmethod
    def activity_has_unupdatable_type(activity):
        if "dayParts" not in activity:
            return False

        return any(
            _d["partInfos"]["type"] not in ["CRA", "", None]
            for _d in activity["dayParts"]
        )


if __name__ == "__main__":
    ERP_CHECKER = AdvansERPChecker("HDUPRAS", "WFMKR54QJB1q")
    a = ERP_CHECKER.is_current_day_filled()
    print(a)
    ERP_CHECKER.extract_activities()
    for task in ERP_CHECKER.tasks:
        print(task)
