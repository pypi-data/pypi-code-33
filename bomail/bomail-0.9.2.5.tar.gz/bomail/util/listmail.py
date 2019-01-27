####
# bomail.util.listmail
#
# (Quickly) list emails matching date range or simple state queries.
# The idea is it's fast because it doesn't have to open the files.
####

import sys
import os.path

import bomail.config.config as config
import bomail.util.datestuff as datestuff
import bomail.cli.mailfile as mailfile

# after and before may be none
def list_all(after, before, mgr, dirname=config.email_dir):
  if not os.path.exists(dirname):
    return []
  all_years = os.listdir(dirname)
  if len(all_years) == 0:
    return []
  output = []
  for year_str in all_years:
    if after is not None and year_str < after[:4]:   continue
    if before is not None and year_str > before[:4]: continue
    year_prefix = year_str + "-"
    year_dir = dirname + year_str + "/"
    all_days = os.listdir(year_dir)
    for day_str in all_days:
      date_str = year_prefix + day_str
      if after is not None and date_str[:len(after)] < after:   continue
      if before is not None and date_str[:len(before)] > before: continue
      day_dir = year_dir + day_str + "/" 
      for s in os.listdir(day_dir):
        if len(s) >= 5 and (s[-4:] == "mail" or s[-5:] == "draft"):
          output.append(day_dir + s)
  return output

# openlist is sorted by reverse lexicographic order
def list_open(after, before, mgr):
  if not os.path.exists(config.openlist_file):
    return []
  output = []
  with open(config.openlist_file) as f:
    for line in f:
      filename = line[:-1] if (len(line) > 0 and line[-1] == "\n") else line
      if datestuff.datestr_matches(datestuff.get_date_from_filename(filename), after, before):
        output.append(filename)
  return output

# scheduledlist is sorted by schedule date, not file date!
# have to check date of file!
# lines have the form "scheduledate emailfilename"
def list_scheduled(after, before, mgr):
  if not os.path.exists(config.scheduledlist_file):
    return []
  output = []
  with open(config.scheduledlist_file) as f:
    for line in f:
      if len(line.strip()) == 0:
        continue
      filename = line.split()[1]
      if filename[-1] == "\n":
        filename = filename[:-1]
      ds = datestuff.get_date_from_filename(filename)
      if datestuff.datestr_matches(ds, after, before):
        output.append(filename)
  return output

def list_draft(after, before, mgr):
  return list_all(after, before, mgr, config.drafts_dir)

# similar to list_all, but use the attach directories (only the ones that exist)
def list_attachonly(after, before, mgr):
  if not os.path.exists(config.attach_dir):
    return []
  all_years = os.listdir(config.attach_dir)
  if len(all_years) == 0:
    return []
  output = []
  for year_str in all_years:
    if after is not None and year_str < after[:4]:   continue
    if before is not None and year_str > before[:4]: continue
    year_prefix = year_str + "-"
    year_dir = config.attach_dir + year_str + "/"
    all_days = os.listdir(year_dir)
    for day_str in all_days:
      date_str = year_prefix + day_str
      if after is not None and date_str[:len(after)] < after:   continue
      if before is not None and date_str[:len(before)] > before: continue
      day_dir = year_dir + day_str + "/" 
      for s in os.listdir(day_dir):
        if s[-1] == "/":
          s = s[:-1]
        mailfile_path = config.email_dir + year_str + "/" + day_str + "/" + s + ".mail"
        output.append(mailfile_path)
  return output
   


class ListOpts:
  def __init__(self):
    self.after_str = None
    self.before_str = None
    self.source = "all"

  def listmail(self, mgr):
    if self.source == "all":
      return list_all(self.after_str, self.before_str, mgr)
    elif self.source == "open":
      return list_open(self.after_str, self.before_str, mgr)
    elif self.source == "scheduled":
      return list_scheduled(self.after_str, self.before_str, mgr)
    elif self.source == "draft":
      return list_draft(self.after_str, self.before_str, mgr)
    elif self.source == "attach":
      return list_attachonly(self.after_str, self.before_str, mgr)


