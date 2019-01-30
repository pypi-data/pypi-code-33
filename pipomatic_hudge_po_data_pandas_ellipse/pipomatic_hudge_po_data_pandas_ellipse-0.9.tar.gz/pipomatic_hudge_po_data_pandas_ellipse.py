"Helper functions for working with Ellipse PO reports"

__version__ = "0.9"

#!/usr/bin/env python
# coding: utf-8

# # PO Data Pandas
#
# Functions for working with PO data

# In[1]:


import pandas as pd
from pathlib import Path


# ## Set up test data

# ## Set up structure
#
# This notebook helps create two datasets from a report generated from ABB's Ellipse system. The first dataset is a report of PO lines. The second dataset is a report of PO and supplier numbers, along with a column that indicates how many lines the PO has.

# ## Get last updated file

# In[20]:


def get_last_file(folder):

    """helper function that finds the most recently updated file in a directory. 
    You use it to pull the most recent datafile dumped into a folder"""

    time, filepath = max((f.stat().st_mtime, f) for f in folder.iterdir())
    return filepath


# ## Transform Stock PO data
#
# The build_po_lines_dataframe function creates PO lines from stock POs

# In[22]:


def build_po_lines_dataframe(stock_pos, po_column_mapping, po_line_column_names):
    stock_pos = stock_pos.rename(columns=po_column_mapping)
    stock_pos["line_number"] = stock_pos.po_number.apply(lambda x: f"{x}".split("-")[1])
    stock_pos.line_number = pd.to_numeric(stock_pos.line_number)
    stock_pos.po_number = stock_pos.po_number.apply(lambda x: f"{x}".split("-")[0])
    stock_pos.supplier_number = stock_pos.supplier_number.apply(
        lambda x: f"{x}".zfill(6)
    )
    stock_pos.stock_description = stock_pos.stock_description.astype(str).apply(
        lambda x: " ".join(x.split())
    )
    stock_pos.stock_code = stock_pos.stock_code.apply(
        lambda x: "{0:.2f}".format(x).rstrip("0").rstrip(".")
    )
    stock_pos.stock_code = stock_pos.stock_code.astype("str")
    stock_pos.po_date = pd.to_datetime(stock_pos.po_date, dayfirst=True)
    stock_pos = stock_pos.sort_values(
        by=["po_date", "po_number", "line_number"], ascending=[True, True, False]
    )
    stock_pos = stock_pos[po_line_column_names]
    return stock_pos


# Stock PO lines are tranformed into header level POs

# In[45]:


def build_po_header_dataframe(stock_po_lines):
    stock_pos_header = stock_po_lines[["po_number", "supplier_number", "line_number"]]
    stock_pos_header = stock_pos_header.sort_values(
        by=["po_number", "line_number"], ascending=[True, False]
    )
    stock_pos_header = stock_pos_header.drop_duplicates(subset=["po_number"])
    stock_pos_header["line_count"] = stock_pos_header.line_number > 1
    stock_pos_header = stock_pos_header.drop(columns="line_number")
    return stock_pos_header


# Service POs are turned into header level POs and then combined with stock POs

# In[32]:


def build_service_po_header_dataframe(service_pos):
    service_pos = service_pos[["Purchase Order Number", "Supplier Number"]]
    service_pos = service_pos.rename(
        columns={
            "Purchase Order Number": "po_number",
            "Supplier Number": "supplier_number",
        }
    )
    service_pos = service_pos.drop_duplicates(subset=["po_number"])
    service_pos.supplier_number = service_pos.supplier_number.apply(
        lambda x: f"{x}".zfill(6)
    )
    service_pos["line_count"] = False
    return service_pos


# Combine service and stock POs

# In[34]:


def combine_service_and_stock_pos(service_pos, stock_po_headers):
    all_pos = service_pos.append(stock_po_headers)
    all_pos.drop_duplicates(subset=["po_number"])
    return all_pos


# ## Build master data file

# In[36]:


def build_master_vendor_dataframe(supplier_master):
    supplier_master = supplier_master[
        [
            "Supplier Number",
            "Supplier Company Name",
            "ABN Number",
            "Branch Code",
            "Bank Account Number",
        ]
    ]
    supplier_master = supplier_master.rename(
        columns={
            "Supplier Number": "supplier_number",
            "Supplier Company Name": "supplier_name",
            "ABN Number": "abn",
            "Branch Code": "bsb",
            "Bank Account Number": "bank_account",
        }
    )
    supplier_master.supplier_number = supplier_master.supplier_number.apply(
        lambda x: f"{x}".zfill(6)
    )
    supplier_master.abn = supplier_master.abn.apply(lambda x: f"{x}".replace(" ", ""))
    supplier_master.bsb = supplier_master.bsb.apply(lambda x: f"{x}".replace("-", ""))
    return supplier_master


# In[ ]:
