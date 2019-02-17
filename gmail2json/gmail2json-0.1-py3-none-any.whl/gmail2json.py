#!/usr/bin/env python
# coding: utf-8

# In[132]:


import base64
import email
import json
import pickle
import os.path
from apiclient import errors
from datetime import datetime, date
from pathlib import Path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# ## Instructions
#
# Follow the instructions on this page to create a credentials.json file:
#
# https://developers.google.com/gmail/api/quickstart/python
#
# Remember to put it into the right project on https://console.developers.google.com

# In[99]:


# If modifying these scopes, delete the file token.pickle.
def establish_service():
    SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
    folder = Path.cwd()
    pf = folder / "token.pickle"
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if pf.exists():
        token = pf.read_bytes()
        creds = pickle.loads(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        pf.write_bytes(pickle.dumps(creds))

    service = build("gmail", "v1", credentials=creds)
    return service


# ## List labels

# In[67]:


def list_labels(service, user_id):
    """Get a list all labels in the user's mailbox.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.

    Returns:
    A list all Labels in the user's mailbox in JSON format.
    """
    try:
        response = service.users().labels().list(userId=user_id).execute()
        labels = response["labels"]
        return labels
    except Exception as e:
        s, r = getattr(e, "message", str(e)), getattr(e, "message", repr(e))
        print("s:", s, "len(s):", len(s))
        print("r:", r, "len(r):", len(r))


# In[174]:


def get_label(service, user_id, label_name):
    labels = list_labels(service, user_id)
    for label in labels:
        if label["name"].lower() == label_name.lower():
            return label["id"]


# In[69]:


def list_messages_matching_query(service, user_id, query=""):
    """List all Messages of the user's mailbox matching the query.

    Args:
    service: Authorized Gmail API service instance.
    user_id: Typically 'me', the authorised user
    query: String used to filter messages returned.
    Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

    Returns:
    List of Messages that match the criteria of the query. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate ID to get the details of a Message.
    """
    try:
        response = service.users().messages().list(userId=user_id, q=query).execute()
        messages = []
        if "messages" in response:
            messages.extend(response["messages"])

        while "nextPageToken" in response:
            page_token = response["nextPageToken"]
            response = (
                service.users()
                .messages()
                .list(userId=user_id, q=query, pageToken=page_token)
                .execute()
            )
            messages.extend(response["messages"])

        return messages
    except Exception as e:
        s, r = getattr(e, "message", str(e)), getattr(e, "message", repr(e))
        print("s:", s, "len(s):", len(s))
        print("r:", r, "len(r):", len(r))


# In[70]:


def list_messages_matching_labels(service, user_id, label_ids=[]):
    """List all Messages of the user's mailbox with label_ids applied.

    Args:
    service: Authorized Gmail API service instance.
    user_id: Typically 'me', the authorised user
    label_ids: Only return Messages with these labelIds applied.

    Returns:
    List of Messages that have all required Labels applied. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate id to get the details of a Message.
    """

    try:
        response = (
            service.users()
            .messages()
            .list(userId=user_id, labelIds=label_ids)
            .execute()
        )
        messages = []
        if "messages" in response:
            messages.extend(response["messages"])

        while "nextPageToken" in response:
            page_token = response["nextPageToken"]
            response = (
                service.users()
                .messages()
                .list(userId=user_id, labelIds=label_ids, pageToken=page_token)
                .execute()
            )
            messages.extend(response["messages"])

        return messages
    except Exception as e:
        s, r = getattr(e, "message", str(e)), getattr(e, "message", repr(e))
        print("s:", s, "len(s):", len(s))
        print("r:", r, "len(r):", len(r))


# In[85]:


def get_message(service, user_id, msg_id):
    """Get a Message and use it to create a MIME Message.

    Args:
    service: Authorized Gmail API service instance.
    user_id: Typically 'me', the authorised user
    msg_id: The ID of the Message required.

    Returns:
    A message.
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        return message
    except Exception as e:
        print(getattr(e, "message", repr(e)))


# In[150]:


def make_parent_folder(message, parent_name):
    folder = date.fromtimestamp(int(message["internalDate"][:10])).isoformat()
    folder_path = Path.cwd() / "mail_archive" / folder / parent_name
    folder_path.mkdir(parents=True, exist_ok=True)
    return folder_path


# In[215]:


def convert_message_to_json(service, user_id, message):
    folder_path = make_parent_folder(message, "messages")
    json_filename = folder_path / f"{message['id']}.json"
    if not json_filename.exists():
        json_filename.write_text(json.dumps(message, indent=4))
        return json_filename
    else:
        return None


# In[212]:


def save_attachments(service, user_id, message):
    folder_path = make_parent_folder(message, "attachments")
    pdf_attachment_list = []
    excel_attachment_list = []
    pdf_count = 0
    excel_count = 0
    for part in message["payload"]["parts"]:
        if part["filename"]:
            if "data" in part["body"]:
                data = part["body"]["data"]
            else:
                att_id = part["body"]["attachmentId"]
                att = (
                    service.users()
                    .messages()
                    .attachments()
                    .get(userId=user_id, messageId=msg_id, id=att_id)
                    .execute()
                )
                data = att["data"]
            file_data = base64.urlsafe_b64decode(data.encode("UTF-8"))
            attachment_name = Path(f"{message['id']}_{part['filename']}")
            attachment_name = attachment_name.with_suffix(
                attachment_name.suffix.lower()
            )
            if "pdf" in attachment_name.suffix:
                pdf_path = folder_path / "pdf"
                pdf_path.mkdir(parents=True, exist_ok=True)
                af = (pdf_path / attachment_name).write_bytes(file_data)
                pdf_attachment_list.append(attachment_name)
                pdf_count += 1
            elif "xls" in attachment_name.suffix:
                excel_path = folder_path / "excel"
                excel_path.mkdir(parents=True, exist_ok=True)
                af = (excel_path / attachment_name).write_bytes(file_data)
                excel_attachment_list.append(attachment_name)
                excel_count += 1
            else:
                print(f"skipped {attachment_name.name}")
    return pdf_attachment_list, pdf_count, excel_attachment_list, excel_count


# In[186]:


def update_labels(service, user_id, msg_id, to_do_label, done_label):
    msg_labels = {"removeLabelIds": [to_do_label], "addLabelIds": [done_label]}
    try:
        message = (
            service.users()
            .messages()
            .modify(userId=user_id, id=msg_id, body=msg_labels)
            .execute()
        )
        return message
    except Exception as e:
        print(getattr(e, "message", repr(e)))


# In[ ]:
