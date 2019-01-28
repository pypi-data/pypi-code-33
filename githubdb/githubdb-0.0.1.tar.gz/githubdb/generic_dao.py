import os
import requests
import json
import hashlib
import time

from github import Github
from collections import defaultdict

class GenericDAO(object):
    def __init__(self, stash):
        self.stash = defaultdict(str)
        self.stash["db"] = Github(stash["token"]).get_repo(stash["path"])
        self.stash["uuid"] = stash["uuid"]

    def read(self, key):
        return requests.get(self.stash["db"].get_contents(key).download_url).text

    def create(self, key, value):
        self.stash["db"].create_file(key, ("uuid : %s, time : %s") % (self.stash["uuid"], str(time.time())), str(value))

    def update(self, key, value):
        self.stash["db"].update_file(key, ("uuid : %s, time : %s") % (self.stash["uuid"], str(time.time())), str(value), self.stash["db"].get_contents(key).sha)

    def create_or_update(self, key, value):
        try:
            read_response = self.stash["db"].get_contents(key)
            self.stash["db"].update_file(key, ("uuid : %s, time : %s") % (self.stash["uuid"], str(time.time())), str(value), read_response.sha)
        except:
            self.create(key, value)

    def delete(self, key):
        read_response = self.stash["db"].get_contents(key)
        self.stash["db"].delete_file(key, ("uuid : %s, time : %s") % (self.stash["uuid"], str(time.time())), read_response.sha)

if __name__ == "__main__":
    generic_dao = GenericDAO({"token":os.getenv("GIT_TOKEN"),"path":os.getenv("GIT_PATH")})
    print(generic_dao.read("test"))