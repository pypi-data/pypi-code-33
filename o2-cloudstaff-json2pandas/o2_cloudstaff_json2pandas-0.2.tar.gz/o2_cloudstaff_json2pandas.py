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


# In[30]:


def create_dataframe_from_json(json_lines):
    line_df = pd.DataFrame(lines)
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


# In[ ]:
