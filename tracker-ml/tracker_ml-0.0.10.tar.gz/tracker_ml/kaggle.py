"""
  _                  _                       _
 | |                | |                     | |
 | |_ _ __ __ _  ___| | _____ _ __ _ __ ___ | |
 | __| '__/ _` |/ __| |/ / _ \ '__| '_ ` _ \| |
 | |_| | | (_| | (__|   <  __/ |_ | | | | | | |
  \__|_|  \__,_|\___|_|\_\___|_(_)|_| |_| |_|_|

Built in Kaggle support for tracker.ml CLI

Copyright 2018, tracker.ml
"""
import os
import requests

import click
import tracker_ml.file_ops as fo
from requests.auth import HTTPBasicAuth


class KaggleAPI:

    def __init__(self, auth=None, ctx=None):
        if auth is None:
            auth = fo.get_kaggle_auth(ctx)
        self.auth = HTTPBasicAuth(auth["username"], auth["key"])

        self.__base_url = "https://www.kaggle.com/api/v1"

    def _format_url(self, path: str) -> str:
        return "{}/{}".format(self.__base_url, path)

    def list_comp_files(self, cid):
        url = self._format_url("competitions/data/list/{}".format(cid))

        r = requests.get(url, auth=self.auth)
        r.raise_for_status()

        print(r.text)
        return r.json()

    def download_file(self, cid, file_data: dict):
        url = self._format_url("competitions/data/download/{}/{}".format(cid, file_data["name"]))

        r = requests.get(url, auth=self.auth)
        r.raise_for_status()

        with open(file_data["name"], 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)


def set_kaggle_dir(kaggle_dir, ctx=None):
    """ manually set kaggle directory that contains API key """
    if not os.path.exists(kaggle_dir):
        click.secho("Error: {} does not exist".format(kaggle_dir), fg="red")
        exit(1)

    if not os.path.isdir(kaggle_dir):
        click.secho("Error: {} is not a directory".format(kaggle_dir), fg="red")
        exit(1)

    config = fo.get_config(ctx)
    config["kaggle_dir"] = kaggle_dir
    fo.set_config(config, ctx=ctx)


def download_competition(ctx=None):
    """ setup files for a competition """


api = KaggleAPI(auth={"username": "sagethomas", "key": "d4093e319a467200c45f09bf4b178af1"})

cid = "house-prices-advanced-regression-techniques"
# api.list_comp_files(cid)
with click.progressbar(api.list_comp_files(cid)) as files:
    for d in files:
        api.download_file(cid, d)
