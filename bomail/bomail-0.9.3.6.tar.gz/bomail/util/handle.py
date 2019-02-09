####
# bomail.util.handle
#
# Handle new emails; tag them, etc.
# Can be invoked from command line to process
# a list of already-created files.
####

import sys
import shlex

from bomail.config.config import pathcfg
import bomail.cli.chstate as chstate
import bomail.cli.mailfile as mailfile
import bomail.cli.search as search
import bomail.util.tags as tags
import bomail.util.search_opts as search_opts
import bomail.util.addr as addr
import bomail.util.tags as tags
import bomail.util.datestuff as datestuff
import bomail.util.util as util


# each rule in mail-handlers.txt is of the form
#   <search-query-1>
#   OR <search-query-2>
#   OR ...
#   close
#   schedule datestr
#   tag tag1, tag2, ...
# where the last three are optional

# A particular rule for handling new email,
# as parsed from the mail_handlers.txt file
class Rule:
  # given a list of text lines (no comments)
  # and the tag manager object
  def __init__(self, my_lines, tag_mgr):
    self.querylist = []    # search query objects
    self.close = False     # if True, close the email
    self.schedstr = None   # if not None, schedule it
    self.tags = None       # if not None, apply this list of tags
    self.load(my_lines, tag_mgr)

  def load(self, my_lines, tag_mgr):
    filter_strs = [my_lines[0]]
    ind = 1
    while ind < len(my_lines) and my_lines[ind].startswith("OR "):
      filter_strs.append(my_lines[ind][len("OR "):].strip())
      ind += 1

    for fs in filter_strs:
      self.querylist.append(search_opts.SearchQuery())
      self.querylist[-1].parse(shlex.split(fs))

    act_lines = my_lines[ind:]
    self.close = False
    self.schedstr = None
    self.tags = None
    for line in act_lines:
      s = line.strip()
      if s == "close":
        self.close = True
      elif s.startswith("schedule "):
        self.schedstr = s[len("schedule "):].strip()
      elif s.startswith("tag "):
        tagset = tags.get_tagset_from_str(s[len("tag "):])
        if self.tags is None:
          self.tags = tagset
        else:
          self.tags.update(tagset)
    if self.tags is not None:
      self.tags = list(self.tags)
      self.tags.sort()
      tag_mgr.check_and_add_tags(self.tags)
      # Remove duplicates?


  # handle this list of filenames with associated datas
  # and tagsets
  # return set of indices matched by this query
  def handle(self, flist, datalist, tagsets, mail_mgr):
    matched_indset = set()
    # if matching any query, and index to set
    for q in self.querylist:
      matched_indset.update(q.filter(mail_mgr, flist))
    if len(matched_indset) == 0:
      return matched_indset
    matched_list = [flist[i] for i in matched_indset]

    if self.close:
      chstate.make_closed(matched_list, mail_mgr)
      mail_mgr.updated_flist(matched_list)

    if self.schedstr is not None:
      # note: wait until now to turn schedstr into datetime because
      # it may be relative to the current time!
      chstate.schedule(matched_list, datestuff.parse_schedstr_to_utcobj(self.schedstr), mail_mgr)
      mail_mgr.updated_flist(matched_list)

    if self.tags is not None:
      for ind in matched_indset:
        if tagsets[ind] is None:
          tagsets[ind] = set()
        tagsets[ind].update(self.tags)

    return matched_indset


# The object that takes care of handling new mail
class MailHandler:
  def __init__(self, tag_mgr=None):
    self.tag_mgr = tags.TagMgr() if tag_mgr is None else tag_mgr
    self.lastlinetags = False
    self.autotagreplies = False
    self.close_sent = False
    self.handlers = []
    self.parse_handlers()

  # read mail_handlers text file options and
  # parse into Rule objects
  def parse_handlers(self):
    try:
      with open(pathcfg.handlers_file) as f:
        lines = f.readlines()
    except:
      util.err_log("Could not find mail-handlers file (" + pathcfg.handlers_file + ")")
      return
    ind = 0
    while ind < len(lines):
      line = lines[ind].strip()
      ind += 1
      if line == "" or line[0] == "#":
        continue

      # special options
      if line.startswith("-autotagreplies"):
        self.autotagreplies = True
        continue
      elif line.startswith("-lastlinetags"):
        self.lastlinetags = True
        continue
      elif line.startswith("-close-sent"):
        self.close_sent = True
        continue

      # asssume this is the start of a rule;
      # get all its lines until a line break or comment
      # in handler_lines
      handler_lines = [line]
      while ind < len(lines):
        line = lines[ind].strip()
        ind += 1
        if line == "" or line[0] == "#":
          break
        handler_lines.append(line)

      # create the rule
      if len(handler_lines) >= 2:
        self.handlers.append(Rule(handler_lines, self.tag_mgr))


  def handle(self, flist, mail_mgr):
    # optimize for case with lots of tag updates
    # by writing to file once at the end
    tagsets = [None]*len(flist)
    datalist = [mail_mgr.get_all(f) for f in flist]

    # 1. Special option: lastlinetags
    if self.lastlinetags:
      for i,data in enumerate(datalist):
        lines = data[mailfile.BODY_L].split("\n")
        if len(lines) >= 2:
          line = data[mailfile.BODY_L].split("\n")[-2]  # -1 only gave a newline/blank for some reason
          if line.startswith("tags: "):
            newtags = tags.get_tagset_from_str(line[len("tags: "):])
            if tagsets[i] is None:
              tagsets[i] = newtags
            else:
              tagsets[i].update(newtags)

    # 2. User-defined handlers
    # Do this before autotagreplies in case a parent and child
    # mail are both being processed
    for h in self.handlers:
      h.handle(flist, datalist, tagsets, mail_mgr)

    # 3. Special option: autotagreplies
    # The problem to solve is if a message and its parent are both new
    # So use a recursive memoization, if my parent is unprocessed then process it
    if self.autotagreplies:
      autotag_processed = [False]*len(flist)
      ids_to_inds = {}
      for i,d in enumerate(datalist):
        ids_to_inds[d[mailfile.MSG_ID_L]] = i
      def do_autotag(i, d):
        if autotag_processed[i]:
          return
        autotag_processed[i] = True  # avoid infinite loops (e.g. bad data)
        my_id = d[mailfile.MSG_ID_L]
        my_reflist = mailfile.do_get_referencelist(my_id, d[mailfile.REFS_L])
        parent_id = mailfile.do_get_parent_id(my_id, my_reflist)
        if parent_id is None:
          return
        elif parent_id in ids_to_inds:  # parent is also new
          par_ind = ids_to_inds[parent_id]
          do_autotag(par_ind, datalist[par_ind])  # recurse
          par_tags = tagsets[par_ind]  # ta-da
        elif mail_mgr.ids.has(parent_id):  # parent is old
          par_fname = mail_mgr.ids.get(parent_id)
          par_tags = mail_mgr.get_tagset(par_fname)
        else:  # we don't have the parent
          return
        if tagsets[i] is not None and par_tags is not None:
          tagsets[i].update(par_tags)
      # end of function do_autotag()

      for i,data in enumerate(datalist):
        do_autotag(i, d)

    # 4. Save the tags to the files
    for fname,tset in zip(flist, tagsets):
      if tset is not None:
        mail_mgr.set_tags([fname], list(tset))

    # 5. Special option: close sent mail
    if self.close_sent:
      # close if sent UNLESS sent to myself
      sentlist = [f for f in flist if mail_mgr.get(f, mailfile.SENT_L) == "True" and not any([addr.is_pair_me(pr) for pr in addr.str_to_pairlist(mail_mgr.get(f, mailfile.TO_L))])]
      chstate.make_closed(sentlist, mail_mgr)



if __name__ == "__main__":
  mgr = mailfile.MailMgr()
  filenames = [s.strip() for s in sys.stdin.readlines()]
  MailHandler().handle(filenames, mgr)

