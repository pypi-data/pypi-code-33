####
# bomail.cli.meta
#
# A little utility to migrate or re-read metadata.
####

import os,sys,shutil,traceback

import bomail.config.config as config
from bomail.config.config import pathcfg

import bomail.config.edit_config as edit_config

import bomail.cli.mailfile as mailfile
import bomail.cli.search as search
import bomail.cli.chstate as chstate

import bomail.util.addr as addr
import bomail.util.msgids as msgids
from bomail.util.tags import TagMgr

usage_str = """
To migrate bomail's data folder to a different path:
This moves to path/bomail/email, path/bomail/metadata, etc.

  bomail meta -m path/

To delete the log files (l as in log):

  bomail meta -l

To update some kinds of metadata (multiple options may be included):
  bomail meta -h         show this help and exit
  bomail meta -b         re-generate address book (addresses and counts)
  bomail meta -t         re-generate list of tags
  bomail meta -d         update all thread (conversation) relationships
  bomail meta -i         re-generate message IDs
  bomail meta -s         re-generate open list and scheduled list

  bomail meta -a         do all of the above

Why you would want to update metadata:
 -if a tag is obsolete, bomail meta -t will remove it from suggestions
  (can also edit metadata/tags.txt)
 -running bomail meta -d may help bomail find thread relationships,
  it tries to update dynamically so this probably won't help.
 -the others should not be necessary unless there was a crash/error.
"""

# maximum messages to hold in memory before releasing them
MAX_MSGS_IN_MEM = 10000


# update thread stuff
def update_refby_info(ids_to_fnames, ids_to_refbysets):
  mgr = mailfile.MailMgr()
  msgs_in_mem = 0
  for msgid,refby in ids_to_refbysets.items():
    if msgid not in ids_to_fnames:  # reference a message we don't have
      continue
    mgr.set(ids_to_fnames[msgid], mailfile.REF_BY_L, ", ".join(sorted(list(refby))))
    msgs_in_mem += 1
    if msgs_in_mem >= MAX_MSGS_IN_MEM:
      mgr = mailfile.MailMgr()
      msgs_in_mem = 0

# assume both oldpre and newpre are directories and s is a path
def replace_prefix(s, oldpre, newpre, helpstr):
  if not s.startswith(oldpre):
    # problem...
    return s
  else:
    return os.path.join(newpre,s[len(oldpre):])


# single pass through all of our files
# newdir is the new data base of bomail
def update(do_tags, do_book, do_threads, do_ids, do_lists, olddir=None, newdir=None):
  mgr = mailfile.MailMgr()
  all_fnames = search.search_argstr("", mgr)
  used_tagset = set()
  addrpr_to_counts = dict()  # map (name, email) to (send_count, recv_count)
  ids_to_fnames = dict()
  ids_to_refbysets = dict()  # map id to all id's it is referenced by
  openlist = []  # filename
  scheduledlist = [] # pair (filename, datestr)
  msgs_in_mem = 0
  for fname in all_fnames:
    if do_tags:
      my_tagset = mgr.get_tagset(fname)
      used_tagset.update(my_tagset)

    if do_book:
      if mgr.get(fname, mailfile.SENT_L) == "True":
        for line in [mailfile.TO_L,mailfile.CC_L,mailfile.BCC_L]:
          prs = addr.str_to_pairlist(mgr.get(fname, line))
          for rec in prs:
            if rec in addrpr_to_counts:
              addrpr_to_counts[rec][0] += 1
            else:
              addrpr_to_counts[rec] = [1,0]
      else:  # we received this email from them
        auths = addr.str_to_pairlist(mgr.get(fname, mailfile.FROM_L))
        for auth in auths:
          if auth in  addrpr_to_counts:
            addrpr_to_counts[auth][1] += 1
          else:
            addrpr_to_counts[auth] = [0,1]
      

    if do_threads or do_ids:
      msgid = mgr.get(fname, mailfile.MSG_ID_L)
      ids_to_fnames[msgid] = fname
      if do_threads:
        for i_ref in mgr.get_references(fname):
          if i_ref in ids_to_refbysets:
            ids_to_refbysets[i_ref].add(msgid)
          else:
            ids_to_refbysets[i_ref] = set([msgid]) # start with one elem

    if do_lists:
      state = mgr.get(fname, mailfile.STATE_L)
      if state == "open":
        openlist.append(fname)
      elif state.startswith("scheduled"):
        datestr = state.split()[1]
        scheduledlist.append((fname,datestr))
    
    # do attachments
    if olddir is not None and newdir is not None:
      alist = mgr.get_attachlist(fname)
      if len(alist) > 0:
        blist = [replace_prefix(s, olddir, newdir, fname) for s in alist]
        mgr.set_attachlist(fname, blist)

    # release memory every so often
    msgs_in_mem += 1
    if msgs_in_mem >= MAX_MSGS_IN_MEM:
      mgr = mailfile.MailMgr()
      msgs_in_mem = 0
  # end loop

  if do_tags:
    tagmgr = TagMgr()
    tagmgr.reset_tags_to(list(used_tagset))

  if do_book:
    addr.write_addr_file(addrpr_to_counts)

  if do_threads:
    update_refby_info(ids_to_fnames, ids_to_refbysets)

  if do_ids:
    msgids.rewrite_from_dict(ids_to_fnames)
    
  if do_lists:
    chstate.rewrite_open_list(openlist)
    chstate.rewrite_scheduled_list(scheduledlist)


def migrate(newdir):
  olddir = pathcfg.bomail_data_base
  if not os.path.exists(newdir):
    print("Error: path does not exist: " + newdir)
  print("Moving data files...")
  try:
    newpath = os.path.join(newdir, "bomail")
    shutil.move(pathcfg.bomail_data_base, newpath)
    print("done!")
  except:
    print("Unable to move data directory!")
    traceback.print_exc()
    exit(0)
  bomail.config.config.load_paths(newdir)
  try:
    edit_config.change_option("data_location", newpath)
    print("successfully edited config file")
  except:
    print("Moved data, but unable to edit configuration file bomail.conf!")
    print("Please make change in " + pathcfg.config_file)
    print("data_location = " + newpath)
    print()
    traceback.print_exc()

  # now our lists and msgid file are out of date
  print("updating metadata...")
  update(False, False, False, True, True, olddir=olddir, newdir=newdir)
  print("done!")
  


def main_cli():
  if len(sys.argv) <= 1 or "-h" in sys.argv:
    print(usage_str)
    exit(0)

  if "-l" in sys.argv:
    if os.path.exists(pathcfg.error_log_file):
      os.remove(pathcfg.error_log_file)
    if os.path.exists(pathcfg.acts_log_file):
      os.remove(pathcfg.acts_log_file)
    print("deleted log files")
    exit(0)

  do_tags, do_book, do_ids, do_threads, do_lists = False, False, False, False, False
  if "-t" in sys.argv or "-a" in sys.argv:
    do_tags = True
  if "-b" in sys.argv or "-a" in sys.argv:
    do_book = True
  if "-d" in sys.argv or "-a" in sys.argv:
    do_threads = True
  if "-i" in sys.argv or "-a" in sys.argv:
    do_ids = True
  if "-s" in sys.argv or "-a" in sys.argv:
    do_lists = True

  if any([do_tags, do_book, do_threads, do_ids, do_lists]):
    print("updating metadata...")
    update(do_tags, do_book, do_threads, do_ids, do_lists)
    print("done!")
 
  if "-m" in sys.argv:
    i = sys.argv.index("-m")
    if i+1 >= len(sys.argv):
      print("Missing path argument (use -h for help)")
      exit(0)
    migrate(sys.argv[i+1])

  
if __name__ == "__main__":
  main_cli()

