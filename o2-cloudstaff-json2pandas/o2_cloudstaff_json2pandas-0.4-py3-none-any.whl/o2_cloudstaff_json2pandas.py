#!/usr/bin/env python
# coding: utf-8

# In[18]:


import json
import pandas as pd
from money2float import money
from pathlib import Path


# In[19]:


def get_json_data(json_filename):
    if json_filename.exists():
        print("Exists")
        with open(json_filename) as json_data:
            data = json.load(json_data)
    return data


# In[35]:


def create_dataframe_from_json(json_data):
    json_lines = json_data["content"]["test_line_items"]
    line_df = pd.DataFrame(json_lines)
    line_df["group"] = (
        line_df["description"]
        .apply(lambda x: x if "***" in x else None)
        .fillna(method="ffill")
    )
    line_df["group"] = line_df["group"].apply(lambda x: x.strip("***"))
    line_df = line_df.set_index(["group"])
    line_df["qty"] = line_df["qty"].apply(lambda x: money(f"{x}"))
    line_df["unit_price"] = line_df["unit_price"].apply(lambda x: money(f"{x}"))
    line_df["line_total"] = line_df["line_total"].apply(lambda x: money(f"{x}"))
    return line_df


# In[38]:


def get_resources_from_lines(line_df):
    resources_df = line_df.loc["One month salary for different services"]
    resources_df = resources_df.reset_index()
    resources_df = resources_df.drop("group", axis=1)
    resources_df["full_name"] = (
        resources_df["description"]
        .apply(lambda x: x if "Resource:" in x else None)
        .fillna(method="ffill")
    )
    resources_df["full_name"] = resources_df["full_name"].apply(
        lambda x: f"{x}".strip("Resource: ")
    )
    resources_df["description"] = resources_df["description"].apply(
        lambda x: "Employee Salary and Direct Cost" if "Resource:" in x else x
    )
    return resources_df
