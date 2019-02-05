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
import traceback

from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage

import bomail.config.config as config
import bomail.cli.mailfile as mailfile
import bomail.util.addr as addr
import bomail.util.util as util

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


def file_to_msg(fname, mgr):
  data = mgr.get_all(fname)
  attach_list = mgr.get_attachlist(fname)
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


# given list of relative filenames
# return results, msg
# where results is a list of success/not [True, False, ...]
def connect_and_send(email_addr, flist, mgr):
  results = [False for f in flist]
  try:
    user_ind = config.email_addrs.index(email_addr)
  except:
    return results, "Error sending from " + email_addr + " (not one of your addresses)"

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
    util.err_log("Sending email, error connecting to server.\n" + traceback.format_exc() + "\n")
    return results, "Error connecting to server: " + str(e)

  for i, fname in enumerate(flist):
    recip_addrs, msg = file_to_msg(fname, mgr)
    try:
      serv.sendmail(email_addr, recip_addrs, msg.as_string())
      if config.smtp_servernames[user_ind] == "localhost": # save the sent mail
        os.makedirs(config.new_rawmail_dir, exist_ok=True)
        try:
          rawname = util.mime_to_mailfile.get_msgid(m, fname)
          with open(os.path.join(config.new_rawmail_dir,rawname), "w") as rawfile:
            rawfile.write(msg.as_string())
        except:
          util.err_log("Error saving copy of sent mail:\n" + fname + "\n" + msg.as_string() + "\n")
      results[i] = True
    except Exception as e:
      serv.quit()
      util.err_log("Sending email, error while sending.\n" + traceback.format_exc() + "\n")
      return results, "Error sending message #" + str(i) + " [" + fname + "]: " + str(e)

  serv.quit()
  return results, ""

 

# given list of filenames
# return vector of successes [True, False, ...], err_msg
def main(flist, mgr):
  # sort them into different "from" addresses and connect to each server once
  fromaddr_to_fnames = {}
  for fname in flist:
    fromline = mgr.get(fname, mailfile.FROM_L)
    frompr = addr.str_to_pair(fromline)
    fromaddr = frompr[1]
    if fromaddr not in fromaddr_to_fnames:
      fromaddr_to_fnames[fromaddr] = [fname]
    else:
      fromaddr_to_fnames[fromaddr].append(fname)

  success = set()
  msg = ""
  for fromaddr,fnames in fromaddr_to_fnames.items():
    res, msg = connect_and_send(fromaddr, fnames, mgr)
    for i,good in enumerate(res):
      if good:
        success.add(fnames[i])
    if len(msg) > 0:
      break
  return [f in success for f in flist], msg



def main_cli():
  if len(sys.argv) >= 2:
    print(usage_str)
    exit(0)

  flist = [f.strip() for f in sys.stdin.readlines()]
  res, err = main(flist, mailfile.MailMgr())
  print("Sent " + str(res) + "/" + str(len(flist)) + " messages.")
  if res < len(flist):
    print(err)


if __name__ == "__main__":
  main_cli()


