####
# bomail.cli.check_sched
#
# Look through scheduledlist and put emails on openlist if their time has come.
####

import sys
import os
import tempfile

from bomail.config.config import pathcfg
import bomail.cli.chstate as chstate
import bomail.cli.mailfile as mailfile
import bomail.util.util as util
import bomail.util.datestuff as datestuff


# Format of scheduled file lines: datestring filename
# Format of open file lines: filename


def main(mail_mgr):
  if not os.path.exists(pathcfg.scheduledlist_file):
    return []
  nowobj = datestuff.get_utc_nowobj()
  to_open = []
  # read through scheduledlist_file, opening all emails until we find a date that exceeds now
  with open(pathcfg.scheduledlist_file) as sched_f, tempfile.NamedTemporaryFile(dir=".", mode="w", delete=False) as new_f:
    for full_line in sched_f:
      line = full_line.strip()
      if len(line) == 0:
        continue
      ind = line.index(" ")
      datestr = line[:ind].strip()
      filename = line[ind+1:].strip()
      dateobj = datestuff.parse_to_utc_obj(datestr)
      if nowobj >= dateobj:
        to_open.append(filename)
        # and don't write to new_f, and continue
      else:
        if len(to_open) == 0:
          break  # no files to open, no changes
        # need to write the rest of file to new_f
        new_f.write(full_line)
  if len(to_open) == 0:
    os.remove(new_f.name)
    return to_open
  util.mv_file(new_f.name, pathcfg.scheduledlist_file)
  chstate.make_open(to_open, mail_mgr)
  return to_open


def main_cli():
  changed_files = main(mailfile.MailMgr())
  if len(changed_files) == 0:
    print("No updates.")
  else:
    print("Opened " + str(len(changed_files)) + (" message:" if len(changed_files) == 1 else " messages:"))
    print("\n".join(changed_files))


if __name__ == "__main__":
  main_cli()

