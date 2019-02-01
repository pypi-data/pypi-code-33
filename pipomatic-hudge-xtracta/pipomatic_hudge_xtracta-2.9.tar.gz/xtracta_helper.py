import json

import re
import requests
import xmltodict # type: ignore
from jinja2 import Template
from PIL import Image, ImageSequence # type: ignore

from typing import List, Dict, Union, Any # From mypy library

# https://www.pythonlikeyoumeanit.com/Module5_OddsAndEnds/Modules_and_Packages.html

company_extract = re.compile(r'.*\[<<(.*)>>\].*')

def get_last_file(folder):
    time, filepath = max((f.stat().st_mtime, f) for f in folder.iterdir())
    return filepath
    

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
        return "Upload failed"
    else:
        response = xmltodict.parse(r.text)
        return response["xml"]["document_id"]


def get_document(api_key: str, document_id: str):
    """Retrieves a full document from Xtracta"""
    documents_url = "https://api-app.xtracta.com/v1/documents"
    data = {"api_key": api_key, "document_id": document_id}
    try:
        r = requests.post(documents_url, data=data)
        response = xmltodict.parse(r.text)
        return response
    except Exception as e:
        return e.args


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


def get_field_ids(document):
    field_ids = {}
    fields = document["documents_response"]["document"]["field_data"]["field"]
    for field in fields:
        field_ids[field["field_id"]] = field["field_name"]
    return field_ids


def get_email_date(filename):
    year = filename.stem[:4]
    month = filename.stem[4:6]
    day = filename.stem[6:8]
    return f"{year}-{month}-{day}"


def transform_dict(start_dict):
    end_dict = {}
    for item in start_dict:
        end_dict[item["field_name"]] = item["field_value"]
    return end_dict


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
            return ["No rejected documents in queue"]
        else:
            return [e]


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


def get_image_urls(image_urls):
    if type(image_urls) != list:
        image_urls = [image_urls]
    return image_urls


# def create_tif_image(image_urls):
#     images = []
#     for i, url in enumerate(image_urls):
#         r = requests.get(url, stream=True)
#         if i == 0:
#             im = Image.open(r.raw)
#         else:
#             images.append(Image.open(r.raw))
#     return im, images


# def save_tif(old_name, new_name, image_urls):
#     old_name = old_name.with_suffix('.tif')
#     new_name = new_name.with_suffix('.tif')
#     im, images = create_tif_image(image_urls)
#     im.save(f'{new_name}', save_all=True, append_images=images)
#     return im, images


def write_json_simple(filename, output):
    with open(f"{filename}", "w") as f:
        f.write(json.dumps(output, indent=4))


def write_json(old_name, new_name, dp, output):
    print(old_name, new_name, dp)
    duplicate_name = dp / new_name.name
    if new_name.exists():
        with open(f"{duplicate_name}", "w") as f:
            f.write(json.dumps(output, indent=4))
    else:
        with open(f"{new_name}", "w") as f:
            f.write(json.dumps(output, indent=4))
    if new_name.exists():
        old_name.unlink()
        return new_name
    else:
        return "File not saved!"


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
    image_url = get_image_urls(document["documents_response"]["document"]["image_url"])[
        0
    ]
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


def add_company_location(output):
    company_location = company_extract.match(output['header']['email_subject'])[1]
    try:
        output['company'], output['location'] = company_location.split('-')
    except:
        output['company'] = company_location
        output['location'] = 'NA'
    return output


def get_lines(document):
    lines_dict = document['documents_response']['document']['field_data']['field_set']['row']
    lines = []
    if len(lines_dict) > 1:
        for line_dict in lines_dict:
            line = transform_dict(line_dict['field'])
            lines.append(line)
    else:
        line = transform_dict(lines_dict['field'])
        lines.append(line)
    return lines
    

# def build_out_reject_queue(api_key, queue):
#     all_output = []
#     if type(queue) == list:
#         for item in queue:
#             row = {}
#             messages = []
#             document_id = item['document_id']
#             document = get_document(api_key, document_id)
#             output = create_output(document)
#             field_ids = get_field_ids(document)
#             if type(item['rejection']['reason']) != list:
#                 field_id = item['rejection']['reason']['linked_field']['field_id']
#                 message = item['rejection']['reason']['message']
#                 messages.append({'field': field_ids[field_id], 'message': message})
#             else:
#                 for sub_item in item['rejection']['reason']:
#                     field_id = sub_item['linked_field']['field_id']
#                     message = sub_item['message']
#                     messages.append({'field': field_ids[field_id], 'message': message})
#             row['status'] = output['status']
#             try:
#                 row['stem'] = output['header']['filename'].replace('.pdf', '')
#             except:
#                 row['stem'] = 'Click to review'
#             row['messages'] = messages
#             row['review_url'] = open_document_ui(api_key, document_id)
#             row['image_url'] = get_image_urls(document['documents_response']['document']['image_url'])[0]
#             all_output.append(row)
#     return all_output


# def build_out_processing_queue(api_key, queue):
#     all_output = []
#     if type(queue) == list:
#         for item in queue:
#             row = {}
#             messages = []
#             document_id = item['document_id']
#             document = get_document(api_key, document_id)
#             output = create_output(document)
#             row['status'] = output['status']
#             try:
#                 row['stem'] = output['header']['filename'].replace('.pdf', '')
#             except:
#                 row['stem'] = 'Click to review'
#             row['messages'] = messages
#             all_output.append(row)
#     return all_output


# def build_output_queue(api_key, queue):
#     all_output = []
#     if type(queue) == list:
#         for item in queue:
#             row = {}
#             document_id = item['document_id']
#             document = get_document(api_key, document_id)
#             output = create_output(document)
#             row['status'] = output['status']
#             try:
#                 row['stem'] = output['header']['filename'].replace('.pdf', '')
#             except:
#                 row['stem'] = 'Click to review'
#             row['output'] = output
#             row['image_url'] = get_image_urls(document['documents_response']['document']['image_url'])[0]
#             all_output.append(row)
#     return all_output
