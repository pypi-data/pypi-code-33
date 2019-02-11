#!/usr/bin/python3

"""
 script for scraping organization information off of Maize Pages
 Written by Kevin Yang

"""

import requests
import csv
import re
import sys
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://maizepages.umich.edu"
ORG_API_PATH = "api/discovery/search/organizations"
NUM_ORGS = 2000


class UserSession(object):
    """Class that authenticates a user for access to Maize Pages, and provides
    methods for parsing and writing data to csv.

    Attributes:
      session: requests session to persist cookies/authentication things
    """

    def __init__(self, username=None, password=None):
        self.session = requests.Session()

        if (username):
            # Get cookie
            response = self.session.get(
                "https://maizepages.umich.edu/account/logon")

            # Get input fields and create payload with username/password
            payload = {}
            soup = BeautifulSoup(response.text, 'html.parser')
            for input in soup.find_all("input"):
                payload[input.get("name")] = input.get("value")
            payload['login'] = username
            payload['password'] = password

            # Post to weblogin and subsequently go through all authentication
            # steps
            try:
                print("Logging in...")
                self.send_post(
                    "https://weblogin.umich.edu/cosign-bin/cosign.cgi", payload)
            except ValueError:
                print("Error logging in with credentials")
                sys.exit()

            try:
                self.check_auth()
            except ValueError as e:
                print(e)
                sys.exit()

    # Description: Checks that authentication worked by searching for "Sign in"
    # in the HTTP response
    def check_auth(self):
        response = self.session.get("https://maizepages.umich.edu")
        if('Sign in' not in response.text):
            print("Logged in successfully")
        else:
            raise ValueError

    # Description: Recursive function for jumping through all the
    # authentication steps
    def send_post(self, url, payload):
        # Send HTTP POST request
        response = self.session.post(url, data=payload)
        response.raise_for_status()

        # Base case for returning after the appropriate post requests have been
        # entered
        if response.url == BASE_URL + '/':
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        # Construct the next url to recurse into
        relative_url = soup.find('form').get('action')
        absolute_url = urljoin(response.url, relative_url)
        # Checks that recursion doesn't enter infinite loop
        if absolute_url == url:
            raise ValueError

        # Gather input fields into payload
        payload.clear()
        for input in soup.find_all("input"):
            payload[input.get("name")] = input.get("value")

        self.send_post(absolute_url, payload)

    # Description: Takes in an organization's page url and
    # returns a tuple containing (name, shortName, firstName, lastName, email)
    def parse_for_name_and_email(self, org_page_url):
        res = self.session.get(org_page_url)
        res.raise_for_status()
        p = re.compile(r"=\s(\{.+\})")
        for match in p.finditer(res.text):
            json_obj = json.loads(match.groups()[0])
            org = json_obj["preFetchedData"]["organization"]

            name = org.get("name")
            shortName = org.get("shortName")

            primaryContact = org.get("primaryContact")
            firstName = primaryContact.get("firstName")
            lastName = primaryContact.get("lastName")
            email = primaryContact.get("primaryEmailAddress")

            return (name, shortName, firstName, lastName, email)

    # Description: Visits each organization page on maizepages and calls
    # parse_for_name_and_email on each. Takes the results and outputs them to
    # a csv file.
    def run_all(self):
        csvfile = open('org_data.csv', 'w')
        writer = csv.writer(csvfile)

        # Get list of all orgs
        payload = {"top": NUM_ORGS}
        res = self.session.get(urljoin(BASE_URL, ORG_API_PATH), params=payload)
        res.raise_for_status()
        res_json = res.json()

        numOrgs = len(res_json["value"])
        completed = 0

        for org in res_json["value"]:
            website_key = org["WebsiteKey"]
            tup = self.parse_for_name_and_email(
                urljoin(BASE_URL, "organization/" + website_key))
            writer.writerow(tup)

            completed += 1
            if (completed % 10 == 0):
                sys.stdout.write('\r')
                sys.stdout.write(
                    "Completed {} / {}".format(completed, numOrgs))
                sys.stdout.flush()


def main():
    maize = UserSession()
    maize.run_all()


if __name__ == "__main__":
    main()
