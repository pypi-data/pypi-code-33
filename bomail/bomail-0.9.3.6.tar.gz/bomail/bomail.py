
import os, sys

from bomail.config.config import pathcfg
from bomail.cli import gui,process,check_sched,search,chstate,mailfile,compose,send,meta,stats
import bomail.util.datestuff as datestuff


usage_str = """
Usage:
Use bomail <command> -h for help on that command.

Commands:

  bomail gui          Launch interface (if in doubt, run this)

  bomail process      Check for and process new emails
  bomail check_sched  Check 'scheduled' emails and unschedule them
  bomail search       Search
  bomail chstate      Change state of emails (open/closed/scheduled/trash)
  bomail compose      Compose new emails as blank, reply, forward
  bomail mailfile     See fields of an email or add/remove tags
  bomail send         Send drafts
  bomail meta         Change data location, cleanup metadata
  bomail stats        See some stats about email

  bomail help datestr Print help about using relative dates
  bomail help tags    Print help about 'dirlike' tags
  bomail help meta    Print help about mail filters and other maintenence

Configuration: """ + pathcfg.config_file + """
Data location: """ + pathcfg.bomail_data_base + """
Email filters: """ + pathcfg.handlers_file + """

"""

taghelp_str = """
Using tags:

An email can have unlimited tags.
Searching for emails with a given tag must match
exactly (so "bomail search -t happy" does not match
emails tagged happydays, but does match emails tagged happy.)

Twist: 'directory-like' tags.
Whenever your tag has a / character, it matches searches
for tags of a prefix up to a /.

Example: anything tagged social/twitter, social/facebook,
or social/mastodon will match "bomail search -t social".
However, none of those will match "bomail search -t facebook".
(Use "bomail search -t social/facebook" instead.)

"""

metahelp_str = """
Metadata and maintenence info:

-- Mail filters/handling --
Please modify the mail-handlers file located in
""" + pathcfg.handlers_file + """

-- Trash --
When trashed, *the original MIME email file is not touched.*
The mailfile and stripped attachments *are not permanently deleted.*
They are placed in """ + pathcfg.trash_dir + """
which you may clear at your convenience.

-- Metadata files --
These are in """ + pathcfg.metadata_dir + """
To refresh metadata, run bomail meta -h
  mail-handlers.txt  Handling new mail - please modify!
  error_log.txt      Errors are logged here. May modify/delete.
  acts_log.txt       Logs all actions, can grow large. May modify/delete.
  addr_book.txt      Used to suggest recipients. No harm to modifying.
  tags.txt           Used to suggest tags. No harm to modifying.
  msg_ids.txt        Do not modify (maps msg id to filename location)
  openlist.txt       Do not modify (list of "open" state emails, for speed)
  scheduledlist.txt  Do not modify ("scheduled" state emails and time to open)
"""

def main():
  if len(sys.argv) <= 1:
    print(usage_str)
    exit(0)

  if sys.argv[1] == "help":
    if len(sys.argv) <= 2:
      print(usage_str)
    elif sys.argv[2] == "datestr":
      print(datestuff.datestr_str)
    elif sys.argv[2] == "tags":
      print(taghelp_str)
    elif sys.argv[2] == "meta":
      print(metahelp_str)
    else:
      print(usage_str)
    exit(0)

  # hacky but simple: make programs act like they were
  # invoked from command line
  sys.argv = sys.argv[1:]

  if sys.argv[0] == "gui":
    gui.main_cli()
  elif sys.argv[0] == "process":
    process.main_cli()
  elif sys.argv[0] == "check_sched":
    check_sched.main_cli()
  elif sys.argv[0] == "search":
    search.main_cli()
  elif sys.argv[0] == "chstate":
    chstate.main_cli()
  elif sys.argv[0] == "mailfile":
    mailfile.main_cli()
  elif sys.argv[0] == "compose":
    compose.main_cli()
  elif sys.argv[0] == "meta":
    meta.main_cli()
  elif sys.argv[0] == "send":
    send.main_cli()
  elif sys.argv[0] == "stats":
    stats.main_cli()

  else:
    print(usage_str)

if __name__ == "__main__":
  main()

