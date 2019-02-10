#!/usr/bin/env python
# coding: utf-8

# In[2]:


from pathlib import Path
import requests
import json
import pandas as pd
import re
from time import sleep


# In[5]:


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


def get_content(download_url, api_key):
    res = requests.get(download_url, auth=(api_key, ""), timeout=5)
    try:
        content = res.json()[0]
    except:
        content = {}
    return content


def get_response(download_url, api_key):
    count = 0
    content = {}
    while content == {}:
        content = get_content(download_url, api_key)
        if content == {}:
            sleep(10)
            count += 1
            print(count * 10)
    return content


def convert_invoice(filename, api_key, parser_id):
    upload_url = f"https://api.docparser.com/v1/document/upload/{parser_id}"
    j = Path("json_data")
    json_filename = j / f"{filename}.json"
    if json_filename.exists():
        print("Exists")
        with open(json_filename) as json_data:
            data = json.load(json_data)
    else:
        with open("./invoices/{}.pdf".format(filename), "rb") as f:
            req = requests.post(upload_url, files={"file": f}, auth=(api_key, ""))
        try:
            parsed_response_id = req.json()["id"]
        except:
            print(req.json())
        download_url = (
            f"https://api.docparser.com/v1/results/{parser_id}/{parsed_response_id}"
        )
        content = get_response(download_url, api_key)
        data = make_json_file(
            filename, json_filename, download_url, parsed_response_id, content
        )
    return data


# In[ ]:
