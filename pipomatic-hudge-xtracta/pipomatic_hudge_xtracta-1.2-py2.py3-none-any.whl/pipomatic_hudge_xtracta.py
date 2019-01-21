"Xtracta package"

__version__ = "1.2"

#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Union  # From mypy library

import numpy as np
import pandas as pd
import requests
import xmltodict  # type: ignore
from dotenv import find_dotenv, load_dotenv
from jinja2 import Template
from PIL import Image, ImageSequence  # type: ignore

from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_integer_dtype,
    is_object_dtype,
    is_string_dtype,
)


# ## Set up test environment

# In[2]:


number_of_rows = 100

load_dotenv(find_dotenv())

api_key = os.getenv("XTRACTA_API_KEY")
database_id = os.getenv("XTRACTA_DATABASE_ID")
header_workflow = os.getenv("XTRACTA_HEADER_ID")
line_workflow = os.getenv("XTRACTA_LINE_ID")


def delete_files(folder):
    file_generator = folder.glob("**/*")
    file_list = list(file_generator)
    for file in file_list:
        file.unlink()
    return list(file_list)


def move_files(samples_folder, file_to_copy, destination_folder):
    (destination_folder / file_to_copy).write_bytes(
        (samples_folder / file_to_copy).read_bytes()
    )
    return file_to_copy


def convert_to_numeric_and_date(df, dayfirst=True):
    for column in df.columns:
        if is_object_dtype(df[column]) or is_string_dtype(df[column]):
            try:
                df[column] = pd.to_numeric(df[column], downcast="integer")
            except:
                try:
                    df[column] = df[column].str.replace("$", "")
                    df[column] = df[column].str.replace(",", "")
                    df[column] = pd.to_numeric(df[column])
                except:
                    try:
                        df[column] = pd.to_datetime(df[column], dayfirst=dayfirst)
                    except:
                        pass
    return df


def random_dates(start, end, seed=1, replace=True, number_of_rows=100):
    dates = pd.date_range(start, end).to_series()
    return dates.sample(number_of_rows, replace=replace, random_state=seed).index


def dataframe_obfuscator(df, number_of_rows=100):
    for column in df.columns:
        if is_datetime64_any_dtype(df[column]):
            df[column] = random_dates(min(df[column]), max(df[column]), seed=1)
        elif is_integer_dtype(df[column]):
            df[column] = df[column].fillna(0)
            if min(df[column]) < max(df[column]):
                df[column] = np.random.randint(
                    min(df[column]), max(df[column]), size=(number_of_rows)
                )
            else:
                df[column] = min(df[column])
        elif is_numeric_dtype(df[column]):
            df[column] = df[column].fillna(0)
            df[column] = np.random.uniform(
                min(df[column]), max(df[column]), size=(number_of_rows)
            )
        else:
            df[column] = "random text"
    return df


def obfuscate_csv(data_file, dayfirst=True, number_of_rows=100):
    df = pd.read_csv(data_file, nrows=number_of_rows)
    df = convert_to_numeric_and_date(df)
    df = dataframe_obfuscator(df)
    df.to_csv(data_file, header=True, index=False)
    return df


def obfuscate_excel(data_file, dayfirst=True, number_of_rows=100):
    df = pd.read_excel(data_file, nrows=number_of_rows)
    display(df.head())
    df = convert_to_numeric_and_date(df)
    df = dataframe_obfuscator(df)
    df.to_excel(data_file, header=True, index=False)
    return df


# ## Functions for interacting with Xtracta's API

# ### Upload file
#
# Uploads a PDf or image file for extraction. The classifier field is used if you want to assign a specific classifier to the document rather than letting Xtracta make its own classification decision

# In[8]:


def upload_file(api_key, workflow_id, filename, classifier=""):
    classifier_xml = (
        f'<field_data><field name="Classifier">{classifier}</field></field_data>'
    )
    upload_url = "https://api-app.xtracta.com/v1/documents/upload"
    file = {"userfile": open(filename, mode="rb")}
    data = {
        "api_key": api_key,
        "workflow_id": workflow_id,
        "field_data": classifier_xml,
    }
    r = requests.post(upload_url, data=data, files=file)
    if r.status_code != 200:
        print(r.status_code)
        return t.text
    else:
        response = xmltodict.parse(r.text)
        return response["xml"]["document_id"]


# In[10]:


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


# In[14]:


def find_documents_to_skip(api_key, header_workflow):

    """You only want to process documents that have data in the document body. 
    This function finds documents that are not in this state"""

    status_to_skip = ["reject", "preprocessing", "output-in-progress"]
    items_to_skip = []
    for status in status_to_skip:
        queue = get_xtracta_status(api_key, header_workflow, status)
        for item in queue:
            if item != f"No {status} documents in queue":
                items_to_skip.append(item["document_id"])
    return items_to_skip


# ## Build the output dictionary from Xtracta data

# In[16]:


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
    return output


def transform_dict(start_dict):
    end_dict = {}
    for item in start_dict:
        end_dict[item["field_name"]] = item["field_value"]
    return end_dict


# In[18]:


def get_documents_wo_json(folder):
    json_files = []
    pdfs = []
    json_list = list(folder.glob("*.json"))
    pdf_list = list(folder.glob("*.pdf"))
    for file in json_list:
        json_files.append(file.stem)
    for pdf in pdf_list:
        pdfs.append(pdf.stem)
    new_documents = list(set(pdfs) - set(json_files))
    return new_documents


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


# In[22]:


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


# In[24]:


def get_lines(document):
    lines_dict = document["documents_response"]["document"]["field_data"]["field_set"][
        "row"
    ]
    lines = []
    if len(lines_dict) > 1:
        for line_dict in lines_dict:
            line = transform_dict(line_dict["field"])
            lines.append(line)
    else:
        line = transform_dict(lines_dict["field"])
        lines.append(line)
    return lines


# ## Build output once in output status

# In[26]:


def build_out_output(document, output):
    output["stem"] = output["header"]["filename"].split(".")[0]
    output[
        "new_filename"
    ] = f"{output['header']['supplier_id']}-{output['header']['invoice_number']}"
    output["header"]["emaildate"] = get_email_date(output["stem"])
    output["document_url"] = document["documents_response"]["document"]["document_url"]
    output["image_urls"] = get_image_urls(
        document["documents_response"]["document"]["image_url"]
    )
    return output


def get_email_date(stem):
    year = stem[:4]
    month = stem[4:6]
    day = stem[6:8]
    return f"{year}-{month}-{day}"


def get_image_urls(image_urls):
    if type(image_urls) != list:
        image_urls = [image_urls]
    return image_urls


# ## Pull company name and location from filename

# In[46]:


def add_company_location(output):
    company_extract = re.compile(r".*\[<<(.*)>>\].*")
    company_location = company_extract.match(output["header"]["email_subject"])[1]
    try:
        output["company"], output["location"] = company_location.split("-")
    except:
        output["company"] = company_location
        output["location"] = "NA"
    return output


# ## Write JSON files, create TIFs and move PDFs

# In[48]:


def write_json_simple(filename, output):
    filename = filename.with_suffix(".json")
    with open(f"{filename}", "w") as f:
        f.write(json.dumps(output, indent=4))
    return filename


# In[50]:


def move_from_input(api_key, document, ip, lp, op):
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
        if json_destination.exists():
            json_source.unlink()
            pdf_source.unlink()
        return "File moved to output / lines"
    elif document["documents_response"]["document"]["document_status"] == "qa":
        json_destination = (jp / output["header"]["filename"]).with_suffix(".json")
        json_source.replace(json_destination)
        if json_destination.exists():
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


# ## Moving files in the file system

# ## Formatting XML for upload into Xtracta's database
#
# Take a list of dicts and format it for uploading to Xtracta's database API

# In[54]:


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


# In[55]:


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


# ## Build HTML file for handling rejections

# In[56]:


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


# In[57]:


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
