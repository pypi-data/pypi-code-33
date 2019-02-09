####
# bomail.cli.mailfile
#
# Specifies the bomail file format, called 'mailfile',
# and mail manager object, and some commands to view/edit
# metadata of emails.
####

import sys
import os, bisect
import email.utils, uuid
import traceback

from bomail.config.config import pathcfg
import bomail.util.tags as tags
import bomail.util.attach as attach
import bomail.util.msgids as msgids
import bomail.util.datestuff as datestuff
import bomail.util.util as util

####
# This file specifies
# (1) the mailfile format and interface
# (2) MailMgr, the mail manager object
#
# Emails are stored in "mailfiles".
# A mailfile is of the form:
#   field_name: field_value
#   ...
#   field_name: field_value
#   =================
#   body_of_email
#
# Formats of specific entries:
# "addr" can be either of these:
#    name@domain.com
#    Longer Name Here <name@domain.com>
#
# "msg_id" is an email message id enclosed in < >
#
# "date" is an ISO8061 date string in UTC time, i.e. yyyy-mm-ddTHH:MM:SS or some prefix
#
# attachment file paths are quote-enclosed
# (with inner quotes backslash-escaped, and all backslashes escaped)
#
# no newlines except in the body
#
# all lists are comma-and-space separated, implying that their
# elements shouldn't have either commas or spaces in them
# except attachment filenames which are quote enclosed
####

fields = ["from","to","cc","bcc","reply-to","subject","date","sent","msg-id","references","referenced_by","attachments","state","tags","body"]
FROM_L   = 0    # addr
TO_L     = 1    # addr list
CC_L     = 2    # addr list
BCC_L    = 3    # addr list
REPLY_L  = 4    # addr list (reply-to header)
SUBJ_L   = 5    # string with no newline
DATE_L   = 6    # datestr (ISO8061 format)
SENT_L   = 7    # "True" if sent from me, "False" otherwise
MSG_ID_L = 8    # msg_id
REFS_L   = 9    # list of msg_ids
REF_BY_L = 10   # list of msg_ids
ATTACH_L = 11   # list of attachment files
STATE_L  = 12   # "open", "closed", or "scheduled datestr"
TAGS_L   = 13   # list of tags
BODY_L   = 14   # arbitrary string

sep = "================\n"  # between headers and body

usage_str = """
Usage: reads a list of filenames from stdin and does the action for all of them.
Options: -g (get the indicated fields), -add-tags, -rm-tags

  mailfile.py -h                  # print this help
  mailfile.py -g all              # get and print all fields
  mailfile.py -g from bcc date    # get and print the fields 'from', 'bcc', and 'date'
  mailfile.py -add-tags tag1 tag2 # add the tags 'tag1' and 'tag2'
  mailfile.py -rm-tags tag1 tag2  # remove the tags 'tag1' and 'tag2'
"""


error_data = [
  "error file not found <>", "", "", "", "",  # from, to, cc, bcc, reply-to
  "", "9999-12-28", "False", email.utils.make_msgid(uuid.uuid4().hex), # subj, date, sent, msgid
  "", "", "", "open", "", # refs, ref-by, attach, state, tags
  "error file not found"]  # body



#-------------------------------
# fileid is of the form yyyy/mm-dd/THH:MM-msgid.ext

DRAFT_EXT = ".draft"
MAIL_EXT = ".mail"
MIME_EXT = ".mime"

def msgid_as_path(msg_id):
  return msg_id.replace("/","-")

def get_datestart_file_part(data):
  msgid = data[MSG_ID_L]
  # convert date to utc
  datestr = data[DATE_L]
  obj = datestuff.parse_to_utc_obj(datestr)
  s = obj.strftime("%Y/%m-%d/T%H:%M:%S")    # maybe not cross-platform
  return s + "-" + msgid_as_path(msgid)

def get_datestart_filename(data, is_draft):
  s = get_datestart_file_part(data)
  ext = DRAFT_EXT if is_draft else MAIL_EXT
  return s + ext

# return full path to mailfile
def get_filename(data, is_draft):
  s = get_datestart_filename(data, is_draft)
  d = pathcfg.drafts_dir if is_draft else pathcfg.email_dir
  return os.path.join(d, s)

# where its attachments are stored
def get_attach_dir(data, is_draft):
  s = get_datestart_filename(data, is_draft)
  return os.path.join(pathcfg.attach_dir, s)

def get_trash_attach_dir(data, is_draft):
  s = get_datestart_filename(data, is_draft)
  return os.path.join(pathcfg.trash_dir, "attach", s)

# return full file path
def get_trashfilename(data, is_draft):
  s = get_datestart_filename(data, is_draft)
  if is_draft:
    return os.path.join(pathcfg.trash_dir, "draft", s)
  return os.path.join(pathcfg.trash_dir, s)

# return fullfile path
def get_rawfilename(data):
  s = get_datestart_file_part(data)
  return os.path.join(pathcfg.old_rawmail_dir, s + MIME_EXT)


#--------------------------------------
# reading/writing to files

# filename is full path to file
# return data array
def read_file(filename):
  data = []
  try:
    with open(filename) as f:
      for i in range(len(fields)-1):
        line = f.readline()
        data.append(line[len(fields[i]) + 2 : -1])  # erase "field: " and trailing "\n"
      f.readline()  # separator ==========
      data.append(f.read()) # body
  except:
    util.err_log("mailfile: could not find " + str(filename) + "\n")
    return list(error_data)
  return data

# filename is a full path
def write_to_file(filename, data):
  os.makedirs(filename[:filename.rfind("/")], exist_ok=True)
  with open(filename, "w") as f:  # if not, crash because that's bad!!
    f.write(data_to_str(data))


#-------------------------------
# formatting of things

# turn refstr into list of msgids
# if my_id is not None, make sure to remove it from refs
# if it is None, ignore it
def do_get_referencelist(my_id, refstr):
  reflist = []
  if len(refstr) == 0:
    return reflist
  for r in refstr.split(", "):
    rs = r.strip()
    if len(rs) > 0 and (my_id is None or rs != my_id):
      reflist.append(rs)
  return reflist


def do_get_parent_id(my_id, reflist):
  if len(reflist) == 0 or reflist[-1] == my_id:
   return None
  return reflist[-1]


def data_to_str(data):
  a = []
  for i,field in enumerate(fields[:-1]):
    a.append(field)
    a.append(": ")
    a.append(data[i])
    a.append("\n")
  a.append(sep)
  a.append(data[BODY_L])
  return "".join(a)


# lazily loaded mailfiles
class MailMgr:
  def __init__(self):
    self.ids = msgids.Ids()
    # filename to data array
    # None or not present if data is not loaded
    self.datas = {}
    
  def ensure_loaded(self, fname):
    if fname not in self.datas or self.datas[fname] is None:
      self.datas[fname] = read_file(fname)

        
  def get(self, fname, ind):
    self.ensure_loaded(fname)
    return self.datas[fname][ind]

  def get_all(self, fname):
    self.ensure_loaded(fname)
    return self.datas[fname]

  def set(self, fname, ind, val):
    self.ensure_loaded(fname)
    self.datas[fname][ind] = val
    write_to_file(fname, self.datas[fname])

  def get_attachlist(self, fname):
    self.ensure_loaded(fname)
    s = self.datas[fname][ATTACH_L]
    return attach.attach_str_to_paths(s)

  def set_attachlist(self, fname, pathlist):
    self.set(fname, ATTACH_L, attach.attach_paths_to_str(pathlist))

  def get_references(self, fname):
    my_id = self.get(fname, MSG_ID_L).strip()
    refstr = self.get(fname, REFS_L)
    return do_get_referencelist(my_id, refstr)

  # get msgids that I am referenced by
  def get_refby(self, fname):
    s = self.get(fname, REF_BY_L)
    return do_get_referencelist(None, s)

  def add_refby(self, fname, refd_by):
    prev_refbys = set(self.get_refby(fname))
    prev_refbys.add(refd_by)
    self.set(fname, REF_BY_L, ", ".join(sorted(list(prev_refbys))))

  # get the id of the message that 'fname' replies to, or None
  def get_parent_id(self, fname):
    return do_get_parent_id(self.get(fname, MSG_ID_L), self.get_references(fname))

  def get_tags(self, fname, include_folders=False):
    return tags.get_taglist_from_str(self.get(fname, TAGS_L), include_folders=include_folders)

  def get_tagset(self, fname, include_folders=False):
    return tags.get_tagset_from_str(self.get(fname, TAGS_L), include_folders=include_folders)

  def add_tags(self, flist, my_taglist):
    taglist = tags.get_taglist_from_list(my_taglist)  # clean, sort tags
    if len(taglist) > 0:
      for fname in flist:
        new_taglist = tags.join(taglist, self.get_tags(fname))
        self.set(fname, TAGS_L, tags.get_str_from_clean_taglist(new_taglist))

  def remove_tags(self, flist, my_taglist):
    taglist = tags.get_taglist_from_list(my_taglist)  # clean, sort tags
    if len(taglist) > 0:
      for fname in flist:
        new_taglist = tags.get_nonmatching(self.get_tags(fname), taglist)
        self.set(fname, TAGS_L, tags.get_str_from_clean_taglist(new_taglist))

  def set_tags(self, flist, taglist):
    tagstr = tags.get_str_from_taglist(taglist)  # clean tags
    for fname in flist:
      self.set(fname, TAGS_L, tagstr)

  # if there was an update to these files (added, changed, or deleted),
  # just remove them from dict and re-load at next request
  def updated_flist(self, flist):
    for f in flist:
      if f in self.datas:
        del self.datas[f]

  def create(self, flist, datalist):
    idlist = [d[MSG_ID_L] for d in datalist]
    self.ids.add(idlist, flist)
    for fname,d in zip(flist, datalist):
      self.datas[fname] = d
      write_to_file(fname, d)
    # now that they're all written, update referenced-by info
    for fname in flist:
      for i_ref in self.get_references(fname):
        if self.ids.has(i_ref):
          self.add_refby(self.ids.get(i_ref), self.get(fname, MSG_ID_L))

  # when files are deleted
  def update_for_trashed(self, flist, idlist):
    for fname in flist:
      if fname in self.datas:  # which it should be...
        del self.datas[fname]
    self.ids.remove(idlist, flist)


def main_cli():
  if len(sys.argv) <= 1 or "-h" in sys.argv:
    print(usage_str)
    exit(0)
  flist = [line.strip() for line in sys.stdin.readlines()]
  mgr = MailMgr()
  if sys.argv[1] == "-g":
    if len(sys.argv) <= 2:
      print(usage_str)
      exit(0)
    if sys.argv[2] == "all":
      print("\n\n".join([data_to_str(mgr.get_all(fname)) for fname in flist]))
    else:
      inds = [fields.index(s) for s in sys.argv[2:]]
      print("\n\n".join(["\n".join([mgr.get(fname, i) for i in inds]) for fname in flist]))
  elif sys.argv[1] == "-add-tags":
    taglist = sys.argv[2:]
    mgr.add_tags(flist, taglist)
  elif sys.argv[1] == "-rm-tags":
    taglist = sys.argv[2:]
    mgr.remove_tags(flist, taglist)
  else:
    print(usage_str)


if __name__ == "__main__":
  main_cli()

