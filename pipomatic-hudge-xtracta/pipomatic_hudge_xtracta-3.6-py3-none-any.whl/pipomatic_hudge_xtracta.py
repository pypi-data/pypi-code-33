#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Union  # From mypy library
import datetime

import numpy as np
import pandas as pd
import requests
import xmltodict  # type: ignore
from dotenv import find_dotenv, load_dotenv
from jinja2 import Template
from PIL import Image, ImageSequence  # type: ignore
from fuzzywuzzy import fuzz

from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_integer_dtype,
    is_object_dtype,
    is_string_dtype,
)


# ## Set up test environment

# In[3]:


load_dotenv(find_dotenv())

api_key = os.getenv("XTRACTA_API_KEY")
database_id = os.getenv("XTRACTA_DATABASE_ID")
header_workflow = os.getenv("XTRACTA_HEADER_ID")
line_workflow = os.getenv("XTRACTA_LINE_ID")


# ## Functions for interacting with Xtracta's API

# ### Upload file
#
# Uploads a PDf or image file for extraction. The classifier field is used if you want to assign a specific classifier to the document rather than letting Xtracta make its own classification decision

# In[33]:


def upload_file(api_key, workflow_id, filename, field_data=""):
    upload_url = "https://api-app.xtracta.com/v1/documents/upload"
    file = {"userfile": open(filename, mode="rb")}
    data = {"api_key": api_key, "workflow_id": workflow_id, "field_data": field_data}
    r = requests.post(upload_url, data=data, files=file)
    if r.status_code != 200:
        print(r.status_code)
        return r.text
    else:
        response = xmltodict.parse(r.text)
        return response["xml"]["document_id"]


# In[5]:


def get_document(api_key: str, document_id: str):

    """retrieves the full xml document from Xtracta and converts it to a dict"""

    documents_url = "https://api-app.xtracta.com/v1/documents"
    data = {"api_key": api_key, "document_id": document_id}
    try:
        r = requests.post(documents_url, data=data)
        response = xmltodict.parse(r.text)
        return response
    except Exception as e:
        return e.args


# In[12]:


def get_xtracta_status(
    api_key: str,
    workflow_id: str,
    status: str,
    api_download_status: str = "active",
    detailed: int = 0,
    documents_order: str = "asc",
) -> list:
    """Returns a list of all Xtracta documents with a particular status"""
    documents_url = "https://api-app.xtracta.com/v1/documents"
    data = {
        "api_key": api_key,
        "workflow_id": workflow_id,
        "document_status": status,
        "api_download_status": api_download_status,
        "items_per_page": 1000,
        "detailed": detailed,
        "documents_order": documents_order,
    }
    try:
        r = requests.post(documents_url, data=data)
        response = xmltodict.parse(r.text)
    except Exception as e:
        return [e.__str__]

    try:
        response_content = response["documents_response"]["document"]
        if type(response_content) == list:
            return response_content
        else:
            return [response_content]
    except Exception as e:
        if type(e).__name__ == "KeyError":
            return [f"No {status} documents in queue"]
        else:
            return [e]


# ## Build the output dictionary from Xtracta data

# In[51]:


def create_output(document: Dict[Any, Any]) -> Dict[Any, Any]:
    """Returns a dictionary with document_id, status and version as top level values 
    and remaining fields as key value pairs in a header section"""
    output = {}
    header_dict = document["documents_response"]["document"]["field_data"]["field"]
    header = transform_dict(header_dict)
    output["document_id"] = document["documents_response"]["document"]["document_id"]
    output["status"] = document["documents_response"]["document"]["document_status"]
    output["version"] = document["documents_response"]["document"]["@revision"]
    output["header"] = header
    if output["status"] in ["qa", "reject", "output"]:
        output = build_out_output(document, output)
    return output


def transform_dict(start_dict):
    end_dict = {}
    for item in start_dict:
        end_dict[item["field_name"]] = item["field_value"]
    return end_dict


def build_out_output(document, output):
    try:
        output["stem"] = output["header"]["filename"].split(".")[0]
    except:
        output["stem"] = output["header"]["filename"]
    output[
        "new_filename"
    ] = f"{output['header']['supplier_id']}-{output['header']['invoice_number']}"
    try:
        output["header"]["email_date"]
    except:
        current_date = datetime.datetime.today().strftime("%Y-%m-%d")
        output["header"]["email_date"] = current_date
    output["document_url"] = document["documents_response"]["document"]["document_url"]
    output["image_urls"] = get_image_urls(
        document["documents_response"]["document"]["image_url"]
    )
    return output


def get_image_urls(image_urls):
    if type(image_urls) != list:
        image_urls = [image_urls]
    return image_urls


# In[20]:


def open_document_ui(api_key: str, document_id: str) -> str:
    """Opens the Xtracta UI to fix and train documents"""
    documents_url = "https://api-app.xtracta.com/v1/documents/ui"
    data = {
        "api_key": api_key,
        "document_id": int(document_id),
        "buttons": "output,archive",
        "no_lockout": 1,
        "expire": 86400,
    }
    r = requests.post(documents_url, data=data)
    response = xmltodict.parse(r.text)
    return response["documents_response"]["url"]


# In[24]:


def open_dashboard_ui(api_key: str, workflow_id: str) -> str:
    """Opens the Xtracta UI to fix and train documents"""
    documents_url = "https://app.mybusinessautomated.net/v1/documents/ui"
    data = {
        "api_key": api_key,
        "workflow_id": int(line_workflow),
        "buttons": "output,archive",
        "no_lockout": 1,
        "expire": 86400,
    }
    r = requests.post(documents_url, data=data)
    response = xmltodict.parse(r.text)
    return response["documents_response"]["url"]


# In[27]:


def update_document(
    api_key: str, document_id: str, delete: int = 0, api_download_status: str = "active"
) -> Dict[str, str]:
    """Updates document on Xtracta"""
    documents_url = "https://api-app.xtracta.com/v1/documents/update"
    data = {
        "api_key": api_key,
        "document_id": int(document_id),
        "delete": delete,
        "api_download_status": api_download_status,
    }
    r = requests.post(documents_url, data=data)
    response = xmltodict.parse(r.text)
    return response["documents_response"]


# In[58]:


def get_lines(document):
    try:
        lines_dict = document["documents_response"]["document"]["field_data"][
            "field_set"
        ]["row"]
    except:
        lines_dict = document["documents_response"]["document"]["field_data"]["field"]
    lines = []
    for line_dict in lines_dict:
        line = transform_dict(line_dict["field"])
        if line["line_net"]:
            lines.append(line)
    return lines


# ## Build output once in output status

# In[34]:


# ## Pull company name and location from filename

# In[36]:


def add_company_location(output):
    company_extract = re.compile(r".*\[<<(.*)>>\].*")
    company_location = company_extract.match(output["header"]["email_subject"])[1]
    try:
        output["company"], output["location"] = company_location.split("-")
    except:
        output["company"] = company_location
        output["location"] = "NA"
    return output


# ## Prepare email text for upload into Xtracta

# In[76]:


def email_to_dict(filename):
    email_json = json.loads(filename.read_text())
    email_json["BodyText"] = email_json["BodyText"].replace("-", " ")
    email_json["BodyText"].replace(" \n", "\n")
    email_json["Subject"] = email_json["Subject"].replace("-", " ")
    return email_json


def get_email_xml(email_dict):
    fields = {
        "field": [
            {"@name": "email_date", "#text": email_dict["Date"]},
            {"@name": "email_from", "#text": email_dict["From"]},
            {"@name": "email_subject", "#text": email_dict["Subject"]},
            {"@name": "email_body", "#text": email_dict["BodyText"]},
        ]
    }
    field_data = {"field_data": fields}
    field_xml = xmltodict.unparse(field_data, pretty=True)
    rows = field_xml.split("\n")
    modified_xml = ("\n").join(rows[1:])
    return modified_xml


# ## Write JSON files, create TIFs and move PDFs

# In[38]:


def write_json_simple(filename, output):
    filename = filename.with_suffix(".json")
    with open(f"{filename}", "w") as f:
        f.write(json.dumps(output, indent=4))
    return filename


# In[40]:


def move_from_input(api_key, document, ip, lp, op, jp):
    output = create_output(document)
    json_source = (ip / output["header"]["filename"]).with_suffix(".json")
    pdf_source = (ip / output["header"]["filename"]).with_suffix(".pdf")
    if document["documents_response"]["document"]["document_status"] == "output":
        output = build_out_output(document, output)
        json_destination = json_destination = (op / output["new_filename"]).with_suffix(
            ".json"
        )
        if not output["header"]["line_count"]:
            output["header"]["line_count"] = 1
        if float(output["header"]["line_count"]) > 1:
            json_destination = (lp / output["new_filename"]).with_suffix(".json")
            pdf_destination = (lp / output["new_filename"]).with_suffix(".pdf")
            if pdf_source.exists():
                pdf_destination.write_bytes(pdf_source.read_bytes())
        with open(f"{json_destination}", "w") as f:
            f.write(json.dumps(output, indent=4))
        save_tif(output, op)
        if json_destination.exists() and json_source.exists():
            json_source.unlink()
            if pdf_source.exists():
                pdf_source.unlink()
        return "File moved to output / lines"
    elif document["documents_response"]["document"]["document_status"] == "qa":
        json_destination = (jp / output["header"]["filename"]).with_suffix(".json")
        json_source.replace(json_destination)
        if json_destination.exists() and json_source.exists():
            json_source.unlink()
            if pdf_source.exists():
                pdf_source.unlink()
            return "File moved to junk"
    else:
        return "File not moved"


def create_tif_image(image_urls):
    images = []
    for i, url in enumerate(image_urls):
        r = requests.get(url, stream=True)
        if i == 0:
            im = Image.open(r.raw)
        else:
            images.append(Image.open(r.raw))
    return im, images


def save_tif(output, op):
    new_name = (op / output["new_filename"]).with_suffix(".tif")
    im, images = create_tif_image(output["image_urls"])
    im.save(f"{new_name}", save_all=True, append_images=images)
    return im, images


# ## Formatting XML for upload into Xtracta's database
#
# Take a list of dicts and format it for uploading to Xtracta's database API

# In[44]:


def update_database_data(api_key, database_id, out, refresh):
    documents_url = "https://api-app.xtracta.com/v1/databases/data_add"
    data = {
        "api_key": api_key,
        "database_id": int(database_id),
        "data": out,
        "refresh": refresh,
    }
    r = requests.post(documents_url, data=data)
    response = xmltodict.parse(r.text)
    return response


# In[45]:


def build_xml_data(supplier_data_dict):
    xml_rows = []
    for row in supplier_data_dict:
        po = {
            "column": [
                {"@id": "55261", "#text": f"{row['po_number']}"},
                {"@id": "55264", "#text": f"{row['supplier_number']}"},
                {"@id": "60223", "#text": f"{row['line_number']}"},
                {"@id": "58133", "#text": f"{row['abn']}"},
                {"@id": "58134", "#text": f"{row['bsb']}"},
                {"@id": "58135", "#text": f"{row['bank_account']}"},
                {"@id": "58242", "#text": f"{row['supplier_name']}"},
            ]
        }
        xml_rows.append(po)
    xml_data = {"xml": {"row": xml_rows}}
    return xmltodict.unparse(xml_data, pretty=True)


# ## Put PO line numbers in lines

# In[64]:


def get_best_match(output, po_lines):
    """
    Matches each line in an invoice with the closest match from a PO. The match is first attempted by stock_code.
    If that fails, it attempts a fuzzy match against description.
    
    Parameters
    ----------
    
    output: dict
        The output is a dict of the invoice. It contains a lines element that holds lines. Each line has a po_item 
        that matches the stock_code column in the po_lines dataframe. 
        
    po_lines: dataframe
        po_lines is a dataframe that lists the po_lines from the PO linked to the invoice. The dataframe has a stock_code
        column and a stock_description column that is used to match to the po_item and desciption elements in the lines
        element of the output dictionary.
        
    returns
    -------
    
    Returns the output dictionary with the po_line_number element filled in.
    
    """
    is_po = po_lines["po_number"] == output["header"]["po_number"]
    filtered_pos = po_lines[is_po]
    filtered_pos = filtered_pos[
        ["stock_code", "stock_description", "qty", "line_number"]
    ]
    filtered_pos_list = filtered_pos.to_dict(orient="records")
    filtered_pos = filtered_pos.set_index("stock_code")
    display(filtered_pos.head())
    filtered_pos_dict = filtered_pos.to_dict(orient="index")
    matches = []
    for i, line in enumerate(output["lines"]):
        best_match_line_number = 0
        best_match_result = 0
        if (
            filtered_pos_dict.get(line["po_item"], "") != ""
        ):  # remove +'y' for production
            output["lines"][i]["po_line_number"] = filtered_pos_dict[line["po_item"]][
                "line_number"
            ]
        else:
            #             print(line['description'])
            best_match_line_number = ""
            for j, po_line in enumerate(filtered_pos_list):
                match_result = fuzz.partial_ratio(
                    line["description"], po_line["stock_description"]
                )
                try:
                    if float(line["qty"]) == float(po_line["qty"]):
                        match_result += 10
                except:
                    pass
                #                 print(float(line['qty']), float(po_line['qty']), match_result)
                if match_result > best_match_result and match_result not in matches:
                    best_match_result = match_result
                    best_match_line_number = j + 1
            #                 print(' --', match_result, po_line['stock_description'])
            #             print(best_match_result, best_match_line_number)
            #             print()
            output["lines"][i]["po_line_number"] = best_match_line_number
            matches.append(best_match_line_number)
    #     print(matches)
    return output


# ## Build HTML file for handling rejections

# In[ ]:


def create_html_section(data, html_template):
    template = Template(html_template)
    html = template.render(data=data)
    return html


reject_queue_html_template = """
    <div class="column is-full">
        <p><strong>Total number of rejects in queue: {{data.reject_count}}</strong></p>
    </div>
    <div class="column is-full">  
        <h2><strong>{{data.output.header.supplier}}</strong></h2>
        <p><strong>Invoice number:</strong> {{data.output.header.invoice_number}}</p>
    </div>
    <div class="column is-two-fifths">
    <section class="section has-text-right">
        <p><strong>Net:</strong> {{"$%.2f"|format(data.output.header.net_total|float)}}</p>
        <p><strong>GST:</strong> {{"$%.2f"|format(data.output.header.gst_total|float)}}</p>
        <p><strong>Total:</strong> {{"$%.2f"|format(data.output.header.gross_total|float)}}</p>
    </section>
    <section class="section">
        <table class="table">
        <thead><tr><th>Field</th><th>Message</th></tr></thead>
        <tbody>
        {% for message in data.messages %}
        <tr>
            <th>{{message.field}}</th>
            <td>{{message.message}}</td>
        </tr>
        {% endfor %}
        </tbody>
        </table>
    </section>
    </div>
    <div class="column is-three-fifths has-text-centered">
        <p><a href="{{data.review_link}}" target="_blank">Review invoice</a></p>
        <p><img src="{{data.invoice_image}}" alt="Invoice Image" width="250"></p>
    </div>
"""


def get_reject_html(api_key, workflow_id, status, html_template):
    queue = get_xtracta_status(api_key, workflow_id, status)
    reject_count = len(queue)
    document_id = queue[0]["document_id"]
    reasons = queue[0]["rejection"]["reason"]
    messages = get_reject_info(api_key, document_id, reasons)
    document = get_document(api_key, document_id)
    image_url = document["documents_response"]["document"]["image_url"][0]
    output = create_output(document)
    review_link = open_document_ui(api_key, document_id)
    data = {
        "output": output,
        "reject_count": reject_count,
        "review_link": review_link,
        "invoice_image": image_url,
        "messages": messages,
    }
    html = create_html_section(data=data, html_template=html_template)
    return html


# In[ ]:


def get_reject_info(api_key, document_id, reasons):
    messages = []
    document = get_document(api_key, document_id)
    field_ids = get_field_ids(document)
    if type(reasons) != list:
        field_id = reasons["linked_field"]["field_id"]
        message = reasons["message"]
        messages.append({"field": field_ids[field_id], "message": message})
    else:
        for sub_item in reasons:
            field_id = sub_item["linked_field"]["field_id"]
            message = sub_item["message"]
            messages.append({"field": field_ids[field_id], "message": message})
    return messages


def get_field_ids(document):
    field_ids = {}
    fields = document["documents_response"]["document"]["field_data"]["field"]
    for field in fields:
        field_ids[field["field_id"]] = field["field_name"]
    return field_ids


# ## Build code
#
# The remaining cells load the code to PIP

# In[ ]:
