####
# bomail.util.search_opts
#
# Parse search options!
####

import os
import shlex
import datetime

import bomail.cli.mailfile as mailfile
import bomail.util.tags as tags
import bomail.util.addr as addr
import bomail.util.datestuff as datestuff
from bomail.util.listmail import ListOpts

options_str = """
All arguments are optional:
 -h               [print this help]
 -n 200           only return first 200 results
 -sortold         list by oldest (default is by newest)

 -a datestr       after date. datestr can be e.g. yyyy-mm-dd
 -b datestr       before date

 -open            state is open
 -scheduled       state is scheduled
 -closed          state is closed
 -draft           is a draft
 -sent            is sent from me
 -attach          has an attachment

 -notags          has no tags
 -to-me           addressed to any of my aliases in config file

Use multiple times to match any, use "str1, str2" to match all:
 -t str           has str as a tag
 -nt str          does not have str as a tag
 -to str          str is in to, cc, or bcc field
 -from str        str is in from field
 -subject str     str is in subject field
 query            query is in email somewhere
"""


def with_quotes(q):
  return ('"' if q[0] != '"' else '') + q + ('"' if q[-1] != '"' else '')

# add query q to search string
def get_new_search_str(old_str, q):
  sq = SearchQuery()
  args = shlex.split(old_str)
  sq.parse(args)

  # if no search query in old string, just append this one
  if len(sq.querylist_list) == 0:
    return old_str + " " + with_quotes(q)

  # otherwise, add it to every search query
  ind = 0
  outargs = []
  while True:
    if ind >= len(args):
      break
    if args[ind] in ['-n', '-a', '-b', '-t', '-nt', '-to', '-from', '-subject']:
      outargs += args[ind:ind+2]
      ind += 2
    elif args[ind] in ['-sortold', '-open', '-scheduled', '-closed', '-draft', '-sent', '-attach', '-notags', '-to-me']:
      outargs += args[ind:ind+1]
      ind += 1
    else:
      outargs.append(with_quotes(args[ind] + ", " + q))
      ind += 1
  return " ".join(outargs)



class SearchQuery:
  def __init__(self, liststep=True):
    self.max_num = -1  # indiciates unlimited
    self.reverse = False

    self.listopts = ListOpts() if liststep else None
    self.orig_after_str = None
    self.orig_before_str = None
    self.after_str = None
    self.before_str = None

    # Can be found by listing (without opening files)
    self.open = None
    self.scheduled = None
    self.draft = None
    self.attach = None

    # Cannot be found by listing
    self.sent = None
    self.closed = None

    self.tagset_list = []
    self.not_tagset_list = []
    self.tolist_list = []
    self.fromlist_list = []
    self.subjectlist_list = []

    self.notags = None  # or True
    self.tome = None    # or True

    self.querylist_list = []


  def parse(self, old_arglist):
    arglist = list(old_arglist)
    if "-n" in arglist:
      i = arglist.index("-n")
      del arglist[i]
      if len(arglist) > i:
        try:
          self.max_num = int(arglist[i])
        except:
          self.max_num = 0
        del arglist[i]

    if "-sortold" in arglist:
      self.reverse = True
      arglist.remove("-sortold")

    if "-a" in arglist:
      i = arglist.index("-a")
      del arglist[i]
      if len(arglist) > i:
        s = arglist[i]
        self.orig_after_str = s
        del arglist[i]
    if "-b" in arglist:
      i = arglist.index("-b")
      del arglist[i]
      if len(arglist) > i:
        s = arglist[i]
        self.orig_before_str = s
        del arglist[i]
  
    # check draft first because it comes from a separate list
    # so it is always handled by listmail, not filter
    if "-draft" in arglist:
      if self.listopts is not None:
        self.listopts.source = "draft"
      else:
        self.draft = True
      arglist.remove("-draft")
    if "-open" in arglist:
      if self.listopts is not None and self.listopts.source == "all":
        self.listopts.source = "open"
      else:
        self.open = True
      arglist.remove("-open")
    if "-scheduled" in arglist:
      if self.listopts is not None and self.listopts.source == "all":
        self.listopts.source = "scheduled"
      else:
        self.scheduled = True
      arglist.remove("-scheduled")
    if "-attach" in arglist:
      if self.listopts is not None and self.listopts.source == "all":
        self.listopts.source = "attach"
      else:
        self.attach = True
      arglist.remove("-attach")

    if "-sent" in arglist:
      self.sent = True
      arglist.remove("-sent")
    if "-closed" in arglist:
      self.closed = True
      arglist.remove("-closed")

    while "-t" in arglist:
      i = arglist.index("-t")
      del arglist[i]
      if len(arglist) < i:
        break
      tagstr = arglist[i]
      self.tagset_list.append(tags.get_tagset_from_str(tagstr, include_folders=False))
      del arglist[i]

    while "-nt" in arglist:
      i = arglist.index("-nt")
      del arglist[i]
      if len(arglist) < i:
        break
      tagstr = arglist[i]
      self.not_tagset_list.append(tags.get_tagset_from_str(tagstr, include_folders=False))
      del arglist[i]

    while "-to" in arglist:
      i = arglist.index("-to")
      del arglist[i]
      if len(arglist) < i:
        break
      addrlist = arglist[i].split(",")
      self.tolist_list.append([s.strip() for s in addrlist])
      del arglist[i]

    while "-from" in arglist:
      i = arglist.index("-from")
      del arglist[i]
      if len(arglist) < i:
        break
      addrlist = arglist[i].split(",")
      self.fromlist_list.append([s.strip() for s in addrlist])
      del arglist[i]

    while "-subject" in arglist:
      i = arglist.index("-subject")
      del arglist[i]
      if len(arglist) < i:
        break
      strlist = arglist[i].split(",")
      self.subjectlist_list.append([s.strip() for s in strlist])
      del arglist[i]

    if "-notags" in arglist:
      self.notags = True
      arglist.remove("-notags")

    if "-to-me" in arglist:
      self.tome = True
      arglist.remove("-to-me")

    if len(arglist) > 0:
      self.querylist_list = [[s.strip() for s in quer.split(",")] for quer in arglist]



  def do_compile(self):
    slist = ["matched_inds = []\n"]
    slist.append("for ind,f in enumerate(filelist):\n")
    
    slist.append("  data = mgr.get_all(f)\n")

    # this is efficient so do it first
    if self.notags:
      slist.append("  if len(data[mailfile.TAGS_L]) > 0:\n")
      slist.append("    continue\n")

    need_date = self.after_str is not None or self.before_str is not None
    if need_date:
      slist.append("  datestr = data[mailfile.DATE_L]\n")
      slist.append("  if not datestr_matches(datestr, self.after_str, self.before_str):\n")
      slist.append("    continue\n")

    if self.open is not None:
      slist.append("  if not data[mailfile.STATE_L].startswith(\"open\"):\n")
      slist.append("    continue\n")
    if self.scheduled is not None:
      slist.append("  if not data[mailfile.STATE_L].startswith(\"scheduled\"):\n")
      slist.append("    continue\n")
    if self.closed is not None:
      slist.append("  if not data[mailfile.STATE_L].startswith(\"closed\"):\n")
      slist.append("    continue\n")
    if self.draft is not None:
      slist.append("  if f[-5:] != \"draft\":\n")
      slist.append("    continue\n")
    if self.sent is not None:
      slist.append("  if not data[mailfile.SENT_L] == \"True\":\n")
      slist.append("    continue\n")
    if self.attach is not None:
      slist.append("  if len(data[mailfile.ATTACH_L]) == 0:\n")
      slist.append("    continue\n")

    if self.tome is not None:
      slist.append("  prlist_list = [addr.str_to_pairlist(data[j]) for j in [mailfile.TO_L, mailfile.CC_L, mailfile.BCC_L]]\n")
      slist.append("  if not any([any([addr.is_pair_me(pr) for pr in prlist]) for prlist in prlist_list]):\n")
      slist.append("    continue\n")

    # need to match all of a set
    if len(self.tagset_list) > 0 or len(self.not_tagset_list) > 0:
      slist.append("  data_tagset = tags.get_tagset_from_str(data[mailfile.TAGS_L], include_folders=True)\n")
    if len(self.tagset_list) > 0:
      slist.append("  if not any([ts.issubset(data_tagset) for ts in self.tagset_list]):\n")
      slist.append("    continue\n")
    # if we match all of a set, then skip
    if len(self.not_tagset_list) > 0:
      slist.append("  if any([nts.issubset(data_tagset) for nts in self.not_tagset_list]):\n")
      slist.append("    continue\n")
    # need to match all of a set
    if len(self.tolist_list) > 0:
      slist.append("  if not any([all([s in data[mailfile.TO_L] or s in data[mailfile.CC_L] or s in data[mailfile.BCC_L] for s in tolist]) for tolist in self.tolist_list]):\n")
      slist.append("    continue\n")
    if len(self.fromlist_list) > 0:
      slist.append("  if not any([all([s in data[mailfile.FROM_L] for s in fromlist]) for fromlist in self.fromlist_list]):\n")
      slist.append("    continue\n")
    if len(self.subjectlist_list) > 0:
      slist.append("  if not any([all([s in data[mailfile.SUBJ_L] for s in subjectlist]) for subjectlist in self.subjectlist_list]):\n")
      slist.append("    continue\n")

    # skip if none of the queries have all their strings somewhere
    if len(self.querylist_list) > 0:
      slist.append("  if not any([all([any([q in s for s in data]) for q in qlist]) for qlist in self.querylist_list]):\n")
      slist.append("    continue\n")

    slist.append("  matched_inds.append(ind)\n")
    # stop if we've found enough!
    if self.max_num > 0:
      slist.append("  if len(matched_inds) >= " + str(self.max_num) + ":\n")
      slist.append("    break\n")

     # save the compiled search query to file
#    with open("compile_log.txt", "w") as myf:
#      myf.write("".join(slist))

    return compile("".join(slist), '<string>', 'exec')
    

  # convert relative dates and time zones to absolute UTC
  def interpret_dates(self):
    self.after_str = None
    self.before_str = None
    if self.listopts is not None:
      self.listopts.after_str = None
      self.listopts.before_str = None

    if self.orig_after_str is not None:
      self.after_str = datestuff.parse_schedstr_to_utcstr(self.orig_after_str)
      if self.listopts is not None:
        self.listopts.after_str = self.after_str[:10]
        if self.orig_after_str[0] in ["p","m"]:
          if not any([s in self.orig_after_str for s in [".","H","M"]]):
            self.after_str = None  # listmail can take care of it
        else:
          if len(self.orig_after_str) <= 10:
            self.after_str = None
 
    if self.orig_before_str is not None:
      self.before_str = datestuff.parse_schedstr_to_utcstr(self.orig_before_str)
      if self.listopts is not None:
        self.listopts.before_str = self.before_str[:10]
        if self.orig_before_str[0] in ["p","m"]:
          if not any([s in self.orig_before_str for s in [".","H","M"]]):
            self.before_str = None  # listmail can take care of it
        else:
          if len(self.orig_before_str) <= 10:
            self.before_str = None
                

  # list all mail matching basic part of query
  def listmail(self, mgr):
    self.interpret_dates()
    filelist = self.listopts.listmail(mgr)
    if self.reverse:
      return reversed(filelist)
    return filelist

  # return list of indices matching our query on filelist
  # which is assumed to have passed listmail testing first!
  def filter(self, mgr, filelist):
    self.interpret_dates()
    # check if we need to do anything!
    if all([x is None for x in [self.after_str, self.before_str, self.open, self.scheduled, self.closed, self.draft, self.sent, self.attach, self.notags, self.tome]]):
      if all([len(x) == 0 for x in [self.tagset_list, self.not_tagset_list, self.tolist_list, self.fromlist_list, self.subjectlist_list, self.querylist_list]]):
        return list(range(len(filelist)))

    compiled_obj = self.do_compile()
    namespace ={"self": self, "addr": addr, "datestr_matches": datestuff.datestr_matches, "mailfile": mailfile, "mgr": mgr, "tags": tags, "filelist": filelist}
    exec(compiled_obj, namespace)
    return namespace["matched_inds"]


  def search(self, mgr):
    filelist = self.listmail(mgr)
    matched_inds = self.filter(mgr, filelist)
    result = [filelist[i] for i in matched_inds] 
    if self.max_num > 0:
      return result[:self.max_num]
    return result


