#!/usr/bin/env python
# coding: utf-8

# In[27]:


from pathlib import Path
import requests
import json
import pandas as pd
import re
from time import sleep


# In[30]:


def make_json_file(filename, json_filename, download_url, parsed_response_id, content):
    data = {
        "filename": "{0}.pdf".format(filename),
        "parsed_response_id": parsed_response_id,
        "download_url": download_url,
        "content": content,
    }
    with open(json_filename, "w") as outfile:
        json.dump(data, outfile, indent=4)
    return data


def get_content(download_url, auth_key):
    res = requests.get(download_url, auth=(auth_key, ""), timeout=5)
    try:
        content = res.json()[0]
    except:
        content = {}
    return content


def get_response(download_url):
    count = 0
    content = {}
    while content == {}:
        content = get_content(download_url)
        if content == {}:
            sleep(10)
            count += 1
            print(count * 10)
    return content


def convert_invoice(filename, auth_key, parser_id):
    upload_url = f"https://api.docparser.com/v1/document/upload/{parser_id}"
    j = Path("json_data")
    json_filename = j / f"{filename}.json"
    if json_filename.exists():
        print("Exists")
        with open(json_filename) as json_data:
            data = json.load(json_data)
    else:
        with open("./invoices/{}.pdf".format(filename), "rb") as f:
            req = requests.post(upload_url, files={"file": f}, auth=(auth_key, ""))
        parsed_response_id = req.json()["id"]
        download_url = "{0}/{1}/{2}".format(
            "https://api.docparser.com/v1/results", parser_id, parsed_response_id
        )
        content = get_response(download_url)
        data = make_json_file(
            filename, json_filename, download_url, parsed_response_id, content
        )
    return data


# In[ ]:
