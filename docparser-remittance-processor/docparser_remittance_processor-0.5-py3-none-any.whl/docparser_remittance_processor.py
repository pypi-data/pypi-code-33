#!/usr/bin/env python
# coding: utf-8

# In[351]:


from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import requests
import json
import pandas as pd
import re

load_dotenv(find_dotenv())


# In[386]:


def get_content(download_url, auth_key):
    res = requests.get(download_url, auth=(auth_key, ""), timeout=5)
    try:
        content = res.json()
    except:
        content = {}
    return content


# In[354]:


def download_pdf(filename, url):
    response = requests.get(url)
    filename.write_bytes(response.content)


# In[355]:


def make_text_file_ready(text):
    strings_to_delete = ["ltd", "pty"]
    text = re.sub("[^A-Za-z0-9\-\. ]+", "", text).lower()
    text_list = text.split()
    good_text = []
    for item in text_list:
        if item not in strings_to_delete:
            good_text.append(item)
    text = "_".join(good_text)
    return text


# In[356]:


def make_file_name(remittance, remittance_date):
    file_name_list = [
        remittance.get("insurer", "missing_insurer_name"),
        remittance.get("broker", "missing_broker_name"),
        remittance_date,
        remittance.get("file_name", "missing_filename"),
    ]
    for i, item in enumerate(file_name_list):
        try:
            file_name_list[i] = make_text_file_ready(item)
        except:
            file_name_list[i] = "missing"
    return "_".join(file_name_list)


# In[357]:


def make_header(remittance):
    try:
        remittance_date = remittance["remittance_date"]["formatted"]
    except:
        try:
            remittance_date = remittance["remittance_date"]
        except:
            remittance_date = "2019-02-14"
    header = {}
    header["file_name"] = make_file_name(remittance, remittance_date)
    header["insurer"] = remittance.get("insurer", "missing_insurer_name")
    header["broker"] = remittance.get("broker", "missing_broker_name")
    header["broker_abn"] = remittance.get("broker_abn", "missing_broker_abn")
    header["remittance_date"] = remittance_date
    header["remittance_total"] = remittance.get(
        "remittance_total", "missing_remittance_total"
    )
    return header


# In[358]:


aub_group_columns = [
    "remittance_date",
    "insurer",
    "broker",
    "insured_name",
    "policy_number",
    "type",
    "effective_date",
    "invoice_number",
    "premium_ex_gst",
    "levies",
    "gst_premium",
    "broker_commission",
    "gst_broker_commission",
    "line_net",
    "remittance_total",
]


def process_aub_group_rows(header, rows):
    fee_mapping = {
        "P": "premium_ex_gst",
        "U": "underwriting_fee",
        "G": "gst_premium",
        "S": "levies",
        "B": "broker_commission",
        "N": "gst_broker_commission",
    }
    transformed_rows = []
    for row in rows:
        fee_group = row["fee_group"].split(" ")
        for fee in fee_group:
            if len(fee) > 1:
                row[fee_mapping.get(fee[0], "line_net")] = fee[1:]
        final = {**header, **row}
        final.pop("fee_group", None)
        transformed_rows.append(final)
    df = pd.DataFrame(transformed_rows)
    try:
        df = df[aub_group_columns]
    except:
        pass
    return df


# In[378]:


portrait_columns = [
    "remittance_date",
    "insurer",
    "broker",
    "broker_reference",
    "insured_name",
    "policy_number",
    "risk_type",
    "type",
    "effective_date",
    "invoice_number",
    "premium_inc_commission_inc_gst",
    "broker_commission",
    "gst_broker_commission",
    "line_net",
    "remittance_total",
]


def process_portrait_rows(header, rows):
    transformed_rows = []
    for row in rows:
        final = {**header, **row}
        transformed_rows.append(final)
    df = pd.DataFrame(transformed_rows)
    try:
        df = df[portrait_columns]
    except:
        pass
    return df


# In[379]:


brokerplus_columns = [
    "remittance_date",
    "insurer",
    "broker",
    "insured_name",
    "policy_number",
    "type",
    "effective_date",
    "invoice_number",
    "premium_ex_gst",
    "levies_01",
    "gst_premium",
    "levies_02",
    "broker_commission",
    "gst_broker_commission",
    "gross_premium_ex_commission",
    "earlier_paid",
    "line_net",
    "remittance_total",
]


def process_brokerplus_rows(header, rows):
    transformed_rows = []
    for row in rows:
        final = {**header, **row}
        transformed_rows.append(final)
    df = pd.DataFrame(transformed_rows)
    try:
        df = df[brokerplus_columns]
    except:
        pass
    return df


# In[380]:


brokers_advantage_columns = [
    "remittance_date",
    "branch",
    "insurer",
    "broker",
    "broker_reference",
    "insured_name",
    "policy_number",
    "type",
    "effective_date",
    "invoice_number",
    "premium_ex_gst",
    "underwriting_fee",
    "levies_01",
    "levies_02",
    "levies_03",
    "broker_commission",
    "net_premium_ex_commission",
    "gst_premium_ex_commission",
    "line_net",
    "remittance_total",
]


def process_brokers_advantage_rows(header, rows):
    transformed_rows = []
    for row in rows:
        final = {**header, **row}
        transformed_rows.append(final)
    df = pd.DataFrame(transformed_rows)
    try:
        df = df[brokers_advantage_columns]
    except:
        pass
    return df


# In[381]:


def save_remittance_output(folder, remittance, df, file_list):
    pdf_filename = Path.cwd() / folder / remittance["file_name"]
    json_remittance_filename = (
        Path.cwd() / folder / remittance["file_name"]
    ).with_suffix(".json")
    csv_filename = (Path.cwd() / folder / remittance["file_name"]).with_suffix(".csv")
    if "pdf" in file_list:
        download_pdf(pdf_filename, remittance["media_link"])
    if "json" in file_list:
        json_remittance_filename.write_text(json.dumps(remittance, indent=4))
    if "csv" in file_list:
        df.to_csv(csv_filename, index=False)


# In[ ]:


# In[ ]:
