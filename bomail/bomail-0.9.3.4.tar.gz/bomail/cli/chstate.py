####
# bomail.cli.chstate
#
# Change state of files (open/closed/scheduled/trash).
####

import sys
import shutil
import os, subprocess
import tempfile
from subprocess import Popen, PIPE

from bomail.config.config import pathcfg
import bomail.cli.mailfile as mailfile
import bomail.util.remove_lines as remove_lines
import bomail.util.merge_lines as merge_lines
import bomail.util.util as util
import bomail.util.datestuff as datestuff

usage_str = """
Change the state of an email to open, closed, or scheduled.
Reads a list of filenames from stdin, one per line.
Call with no args or -h to print this help.

  bomail chstate -o           # make filenames open
  bomail chstate -c           # make filenames closed
  bomail chstate -t           # trash filenames
  bomail chstate -ut          # untrash filenames
  bomail chstate -s datestr   # schedule filename for datestr (e.g. yyyy-mm-dd)
"""


# remove files from open and scheduled lists
def remove_from_lists(flist):
  if os.path.exists(pathcfg.openlist_file):
    remove_lines.do_sorted(pathcfg.openlist_file, sorted(flist))
  if os.path.exists(pathcfg.scheduledlist_file):
    remove_lines.do_sched(pathcfg.scheduledlist_file, set(flist))

def check_flist(flist):
  result = []
  for fname in flist:
    if os.path.exists(fname):
      result.append(fname)
    else:
      util.err_log("Nonexistent filename: " + fname)
  return result

# change all files' state to open
def make_open(flist, mgr, remove_old=True):
  flist = check_flist(flist)
  if remove_old:
    remove_from_lists(flist)
  # sort openlist by lexicographic
  merge_lines.do(pathcfg.openlist_file, sorted(flist))
  for f in flist:
    mgr.set(f, mailfile.STATE_L, "open")


# change all files' state to closed
def make_closed(flist, mgr):
  flist = check_flist(flist)
  remove_from_lists(flist)
  for f in flist:
    mgr.set(f, mailfile.STATE_L, "closed")


def scheduled_list_str(fname, sched_datestr):
  return sched_datestr + " " + fname


# schedule all files for dateobj, a datetime object
def schedule(flist, dateobj, mgr):
  flist = check_flist(flist)
  remove_from_lists(flist)
  datestr = datestuff.get_printed_schedulestr(dateobj)
  # sort scheduledlist
  lines = [scheduled_list_str(f, datestr) for f in flist]
  merge_lines.do(pathcfg.scheduledlist_file, lines)
  for f in flist:
    mgr.set(f, mailfile.STATE_L, "scheduled " + datestr)

# given (unsorted) list of open files, rewrite our save file
def rewrite_open_list(flist):
  flist.sort()  # ascending sort
  with open(pathcfg.openlist_file, "w") as f:
    f.write("\n".join(flist))

# given (unsorted) list of pairs (fname, datestr), rewrite save
def rewrite_scheduled_list(prlist):
  slist = [scheduled_list_str(pr[0], pr[1]) for pr in prlist]
  slist.sort(reverse=True)  # newest first
  with open(pathcfg.scheduledlist_file, "w") as f:
    f.write("\n".join(slist))

# trash all files, including remove them from msg_ids_file
# return corresponding list of new full filenames (in trash folder)
def trash(flist, mgr):
  remove_from_lists(flist)
  os.makedirs(pathcfg.trash_dir, exist_ok=True)
  newnames = []
  idlist = [mgr.get(fname, mailfile.MSG_ID_L) for fname in flist]
  for f in flist:
    # 1. move/write the file
    d = mgr.get_all(f)
    is_draft = f.endswith(mailfile.DRAFT_EXT)
    new_fullname = mailfile.get_trashfilename(d, is_draft)
    new_dir = os.path.dirname(new_fullname)
    os.makedirs(new_dir, exist_ok=True)
    if os.path.exists(f):
      util.mv_file(f, new_fullname)
    else:
      mailfile.write_to_file(new_fullname, d)
    # 2. move attachments
    if len(d[mailfile.ATTACH_L].strip()) > 0:
      attach_dir = mailfile.get_attach_dir(d, is_draft)
      if os.path.exists(attach_dir):
        trash_attach_dir = mailfile.get_trash_attach_dir(d, is_draft)
        os.makedirs(os.path.dirname(trash_attach_path[:-1]), exist_ok=True)  # make sure to get the parent
        util.mv_dir(attach_dir, trash_attach_dir)  # make the destination
#        os.makedirs(trash_attach_dir, exist_ok=True)
#        for attach_f in os.listdir(attach_dir):
#          util.mv_file(os.path.join(attach_dir,attach_f),
#                       os.path.join(trash_attach_dir,attach_f))
    newnames.append(new_fullname)
  mgr.update_for_trashed(flist, idlist)
  return newnames


# given list of filenames
def do_untrash(trashed_flist, mgr):
  datalist = [mailfile.read_file(f) for f in trashed_flist]
  create_flist = [mailfile.get_filename(d, f.endswith(mailfile.DRAFT_EXT)) for f,d in zip(trashed_flist, datalist)]
  untrash(create_flist, datalist, mgr)


# given list of new relative filenames and data to put in them
def untrash(create_flist, datalist, mgr):
  # 1) create mailfiles
  create(create_flist, datalist, mgr)
  # 2) move attachments back if needed
  for fname,d in zip(create_flist,datalist):
    if len(d[mailfile.ATTACH_L].strip()) > 0:
      is_draft = fname.endswith(mailfile.DRAFT_EXT)
      trash_attach_dir = mailfile.get_trash_attach_dir(d, is_draft)
      attach_dir = mailfile.get_attach_dir(d, is_draft)
      for attach_f in os.listdir(trash_attach_dir):
        util.mv_file(os.path.join(trash_attach_dir,attach_f),
                     os.path.join(attach_dir,attach_f))

# the opposite of trash basically
# given a list of filenames and the data
# do error checking, call mgr.create(), and set state open
def create(flist, datalist, mgr):
  for fname,d in zip(flist, datalist):
    if os.path.exists(fname):
      s = ["Creating file, already exists: " + fname]
      d2 = mailfile.read_file(fname)
      for i in range(len(d)):
        if d2[i] != d[i]:
          s.append(">>>> old version " + mailfile.fields[i])
          s.append(d2[i])
          s.append(">>>> new version:")
          s.append(d[i])
      util.err_log("\n".join(s))
    elif mgr.ids.has(d[mailfile.MSG_ID_L]):
      util.err_log("Creating file, non-identical file with same message ID already exists: " + mgr.ids.get(d[mailfile.MSG_ID_L]) + "\n"
                   + "New data:\n  " + "\n  ".join(d) + "\n")
    else:
      mgr.create(flist, datalist)
  make_open(flist, mgr, False)  # False == don't try to remove old ones from list
 

def main(args, flist, mgr):
  flist.sort()
  if args[0] == "-o":
    make_open(flist, mgr)
  elif args[0] == "-c":
    make_closed(flist, mgr)
  elif args[0] == "-t":
    trash(flist, mgr)
  elif args[0] == "-ut":
    do_untrash(flist, mgr)  # filelist are all currently in trash
  elif args[0] == "-s":
    sched = datestuff.parse_schedstr_to_utcobj(args[1])
    if sched is None:
      print("Could not parse scheduling date string!")
      exit(0)
    schedule(flist, sched, mgr)


def main_cli():
  if len(sys.argv) < 2 or "-h" in sys.argv:
    print(usage_str)
    exit(0)
  mgr = mailfile.MailMgr()
  # remove each trailing newline
  main(sys.argv[1:], [s[:-1] for s in sys.stdin.readlines()], mgr)

if __name__ == "__main__":
  main_cli()

