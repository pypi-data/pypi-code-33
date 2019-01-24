####
# bomail.cli.send
#
# Send drafts.
####

import os
import sys
import mimetypes
import subprocess, email
import smtplib

from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage

import bomail.config.config as config
import bomail.cli.mailfile as mailfile
import bomail.util.addr as addr

usage_str = """
Reads filename(s) from stdin one per line and sends them.
send.py -h to print this help.
"""


# adapted from python library example: https://docs.python.org/3/library/email-examples.html
def add_attachments(msg, attach_list):
  for filename in attach_list:
    if not os.path.exists(filename):
      raise Exception("Did not send. Could not attach (does not exist): " + filename)
    if not os.path.isfile(filename):
      raise Exception("Did not send. Could not attach (is not a file): " + filename)
    ctype, encoding = mimetypes.guess_type(filename)
    if ctype is None or encoding is not None:
      ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)
    if maintype == 'text':
      with open(filename) as fp:
        sub_msg = MIMEText(fp.read(), _subtype=subtype)
    elif maintype == 'image':
      with open(filename, 'rb') as fp:
        sub_msg = MIMEImage(fp.read(), _subtype=subtype)
    elif maintype == 'audio':
      with open(filename, 'rb') as fp:
        sub_msg = MIMEAudio(fp.read(), _subtype=subtype)
    else:
      with open(filename, 'rb') as fp:
        sub_msg = MIMEBase(maintype, subtype)
        sub_msg.set_payload(fp.read())
      encoders.encode_base64(sub_msg)
    sub_msg.add_header('Content-Disposition', 'attachment', filename=os.path.split(filename)[1])
    msg.attach(sub_msg)


def file_to_msg(filename, mgr):
  data = mgr.get_all(filename)
  attach_list = mgr.get_attachlist(filename)
  if len(attach_list) == 0:  # no attachments
    msg = MIMEText(data[mailfile.BODY_L], 'plain')
  else:
    msg = MIMEMultipart()
    msg.attach(MIMEText(data[mailfile.BODY_L], 'plain'))
    add_attachments(msg, attach_list)
  msg['Subject'] = data[mailfile.SUBJ_L]
  msg['From'] = data[mailfile.FROM_L]
  msg['To'] = data[mailfile.TO_L]
  msg['Date'] = email.utils.formatdate()
  msg['Message-ID'] = data[mailfile.MSG_ID_L]
  if len(data[mailfile.CC_L]) > 0:
    msg['CC'] = data[mailfile.CC_L]
  refs = data[mailfile.REFS_L]
  if len(data[mailfile.REPLY_L]) > 0:
    msg['Reply-To'] = data[mailfile.REPLY_L]
  if len(refs) > 0:
    msg['In-Reply-To'] = refs.split(", ")[-1]
    msg['References'] = refs

  recip_lists = data[mailfile.TO_L].split(", ")
  if len(data[mailfile.CC_L]) > 0:
    recip_lists += data[mailfile.CC_L].split(", ")
  if len(data[mailfile.BCC_L]) > 0:
    recip_lists += data[mailfile.BCC_L].split(", ")
  recip_addrs = [addr.str_to_pair(a)[1] for a in recip_lists]
  return recip_addrs, msg


def connect_and_send(email_addr, filelist, mgr):
  try:
    user_ind = config.email_addrs.index(email_addr)
  except:
    return 0, "Error sending from " + email_addr + " (not one of my addresses)"

  try:
    if config.smtp_servernames[user_ind] == "localhost":
      serv = smtplib.SMTP("localhost")
    else:
      serv = smtplib.SMTP(config.smtp_servernames[user_ind], config.smtp_ports[user_ind])
      serv.ehlo()
      serv.starttls()
      serv.ehlo()
      serv.login(config.smtp_usernames[user_ind], config.smtp_passwords[user_ind])
  except Exception as e:
    with open(config.error_log_file, "a") as errf:
      errf.write("-----------------\n" + repr(e) + "\n")
    return 0, "Error connecting to server: " + str(e)

  for i, filename in enumerate(filelist):
    recip_addrs, msg = file_to_msg(filename, mgr)
    try:
      serv.sendmail(email_addr, recip_addrs, msg.as_string())
      if config.smtp_servernames[user_ind] == "localhost": # save the sent mail
        newfilename = mailfile.get_mailfilepath(mgr.get_all(filename))[1]
        newfilepath = os.path.join(config.save_sent_dir, newfilename)
        with open(newfilepath, "w") as savef:
          savef.write(msg.as_string())
    except Exception as e:
      serv.quit()
      with open(config.error_log_file, "a") as errf:
        errf.write("-----------------\n" + repr(e) + "\n")
      return i, "Error sending message #" + str(i) + " [" + filename + "]: " + str(e)

  serv.quit()
  return len(filelist), ""

 

# return num_successes, err_msg
def main(filelist, mgr):
  # sort them into different "from" addresses and connect to each server once
  fromaddr_to_fnames = {}
  for fname in filelist:
    fromline = mgr.get(fname, mailfile.FROM_L)
    frompr = addr.str_to_pair(fromline)
    fromaddr = frompr[1]
    if fromaddr not in fromaddr_to_fnames:
      fromaddr_to_fnames[fromaddr] = [fname]
    else:
      from_addr_to_fnames[fromaddr].append(fname)

  total_sent = 0
  for fromaddr,fnames in fromaddr_to_fnames.items():
    num, msg = connect_and_send(fromaddr, fnames, mgr)
    total_sent += num
    if len(msg) > 0:
      return total_sent, msg
  return total_sent, ""



def main_cli():
  if len(sys.argv) >= 2:
    print(usage_str)
    exit(0)

  filelist = [f.strip() for f in sys.stdin.readlines()]
  res, err = main(filelist, mailfile.MailMgr())
  print("Sent " + str(res) + "/" + str(len(filelist)) + " messages.")
  if res < len(filelist):
    print(err)


if __name__ == "__main__":
  main_cli()


