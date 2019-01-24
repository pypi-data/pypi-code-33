####
# bomail.config.config
#
# Main configuration file.
# When loaded, it tries to open ~/.bomailrc and read it; if unsuccessful,
# it runs a short setup program asking questions.
####

import os, sys

bomailrc_filename = ".bomailrc"


#--------------------------------------------------------------
setup_success_str = """
Basic setup successful!
 (1) Edit ~/.bomailrc in order to send email and other options.
 (2) Edit ~/bomail/metadata/mail-handlers.txt to set up auto-tagging
     and processing of new mail.

Run bomail to begin...
"""


#--------------------------------------------------------------
bomail_tabcomplete_str = """

_bomail()
{
    local cur=${COMP_WORDS[COMP_CWORD]}
    COMPREPLY=( $(compgen -W "gui process check_sched search chstate compose mailfile send stats clean_tags" -- $cur) )
}
complete -F _bomail bomail

"""


#--------------------------------------------------------------
sample_mailhandlers_str = """## This file controls handling of new emails in bomail.
## In this file, lines starting with '#' are comments.

## ------------------------------------------------------
## Section 1: Special options
##
## Turn each off by commenting it with '#'.
## ------------------------------------------------------

## Tag replies to a thread with parent message's tags
-autotagreplies

## Use tags from last line of email if of the form "tags: tag1, ..."
-lastlinetags

## Automatically close any sent mail
-close-sent


## ---------------------------------------------------
## Section 2: Custom handlers
##
## You write these.
## ---------------------------
##
## Each handler is a list of search strings (see bomail search -h)
## followed by a list of actions to take for those messages.
## Actions are "open", "close", "schedule schedstr" (see bomail help datestr),
## and "tag tag1, tag2, ...". Examples:
##
## -from Facebook
## tag social
##
## -from Instagram
## OR -subject Instagram
## close
## AND tag social
"""

#--------------------------------------------------------------
sample_config_str = """## bomail configuration file
##
## All lines beginning with # are comments and are ignored.
## To uncomment a line, delete the initial #.



## ============================================================
## User info: must edit this section!

name = YOUR NAME
email_addr = USER@DOMAIN.COM

## Send email from this server.
## If smtp_servername = localhost, the other options are ignored.
## For SMTP, read username/pass from file, or enter them here.
smtp_servername = smtp.gmail.com
smtp_port = 587
smtp_userpass_file = /home/LINUXUSERNAME/.getmail/getmailrc
#smtp_username = USER or USER@DOMAIN.COM
#smtp_password = PASSWORD

#alias_addresses = ALSO_ME@DOMAIN.COM, ALSO_METOO@DOMAIN.COM

## Additional aliases here. Add numbers 2,3,...
## Just edit "From" line in email to send from these instead.
#name2 = YOUR NAME
#email_addr2 = ALTERNATE@DOMAIN.COM
#smtp_servername2 = smtp.office365.com
#smtp_port2 = 587
#smtp_userpass_file2 = /home/bo/.getmail/getmailrc_bowaggonergmail
#smtp_username2 = USER2 or USER2@DOMAIN.COM
#smtp_password2 = PASSWORD2



## ============================================================
## Organization options: should confirm these are okay

bomail_location = ~/bomail
new_rawmail_location = ~/mail/new
processed_rawmail_location = ~/mail/cur



## ============================================================
## Important UI options

## Comment next line to turn off threading (conversations)
threads_on

read_program = less
edit_program = vim

## Comment next line to use vim-style navigation (hjkl for left/down/up/right)
#arrowkey_navigation

## Options are light1, light2, dark1, dark2
colorscheme = dark1



## ============================================================
## Other UI options

## Options are none, some, all
strip_newlines_in_msg_preview = some

## Num lines (including subject/author/date and preview lines) per message
total_lines_per_msg = 5
threadview_total_lines_per_msg = 10

## Number of characters to use ("len") and for spacing ("pad")
date_len = 20
date_pad = 2
author_len = 24
author_pad = 2

## Comment to turn off
#hline_between_msgs
skipline_between_msgs
show_tags
tags_on_topline


"""
#--------------------------------------------------------------


home = os.getenv("HOME")
config_file = os.path.join(home, bomailrc_filename)


# Initial setup!
if not os.path.exists(config_file):
  print("\nWelcome to bomail!")

  sys.stdout.write("Name (as it will appear in From line): ")
  sys.stdout.flush()
  myname = sys.stdin.readline().strip()
  sys.stdout.write("Email address (primary, i.e. send email from): ")
  sys.stdout.flush()
  myaddr = sys.stdin.readline().strip()

  default_datadir = os.path.join(home,"bomail")
  sys.stdout.write("Data files location? (leave blank to use " + default_datadir +"): ")
  sys.stdout.flush()
  datadir = sys.stdin.readline().strip()
  if len(datadir) == 0:
    datadir = default_datadir

  
  default_newmail_dir = os.path.join(home, "mail/new")
  sys.stdout.write("Process new mail from where? (leave blank to use " + default_newmail_dir + "): ")
  sys.stdout.flush()
  newmail_dir = sys.stdin.readline().strip()
  if len(newmail_dir) == 0:
    newmail_dir = default_newmail_dir

  default_oldmail_dir = os.path.join(home, "mail/cur")
  sys.stdout.write("Put mail where after processing? (leave blank to use " + default_oldmail_dir + "): ")
  sys.stdout.flush()
  oldmail_dir = sys.stdin.readline().strip()
  if len(oldmail_dir) == 0:
    oldmail_dir = default_oldmail_dir

  sys.stdout.write("Add bomail command tab-completion to your ~/.bashrc file? (y/n): ")
  sys.stdout.flush()
  tabcomplete = sys.stdin.readline().strip()
  if len(tabcomplete) > 0 and tabcomplete[0] in ["y", "Y"]:
    with open(os.path.join(home, ".bashrc"), "a") as f:
      f.write(bomail_tabcomplete_str)

  # this is not ideal because it doesn't change if the configuration at
  # the bottom of the file changes
  metadata_dir  = os.path.join(datadir, "metadata/")
  handlers_file = os.path.join(metadata_dir, "mail-handlers.txt")
  if not os.path.exists(handlers_file):
    os.makedirs(metadata_dir, exist_ok=True)
    with open(handlers_file, "w") as f:
      f.write(sample_mailhandlers_str)

  with open(config_file, "w") as f:
    f.write(sample_config_str.replace("YOUR NAME", myname).replace("USER@DOMAIN.COM", myaddr).replace("~/bomail", datadir).replace("~/mail/new",newmail_dir).replace("~/mail/cur",oldmail_dir))

  print(setup_success_str)
  exit(0)


# Function to open and parse config file
def parse_config_file():
  options_dict = {}
  def parse_line(line):
    line = line.strip()
    if len(line) > 0 and line[0] != "#":
      if "=" in line:
        left, right = line.split("=")
        options_dict[left.strip()] = right.strip()
      else:
        options_dict[line.strip()] = True
  
  with open(config_file) as f:
    for line in f:
      parse_line(line)
  return options_dict


# Actually do it
options_dict = parse_config_file()


# --------------------------------------------------------------
# User info

names = []
email_addrs = []
smtp_servernames = []
smtp_ports = []
smtp_usernames = []
smtp_passwords = []

# return True on success, False on failure
def get_user_info(j):
  suffix = "" if j==0 else str(j)
  if not ("name" + suffix) in options_dict:
    return False
  names.append(options_dict["name" + suffix])
  email_addrs.append(options_dict["email_addr" + suffix])
  smtp_servernames.append(options_dict["smtp_servername" + suffix])
  if smtp_servernames[-1] == "localhost":
    return True
  smtp_ports.append(int(options_dict["smtp_port" + suffix]))
  if ("smtp_userpass_file" + suffix) in options_dict:
    try:
      with open(options_dict["smtp_userpass_file" + suffix]) as f:
        for line in f:
          if line.startswith("username ="):
            uname = line[line.index("=")+1:].strip()
          if line.startswith("password ="):
            pword = line[line.index("=")+1:].strip()
      smtp_usernames.append(uname)
      smtp_passwords.append(pword)
    except:
      raise Exception("Could not read username/password from " + options_dict["smtp_userpass_file" + suffix])
  else: # get username and password straight from the config
    smtp_usernames.append(options_dict["smtp_username" + suffix])
    smtp_passwords.append(options_dict["smtp_password" + suffix])
  return True

# first get empty suffix, then 2, 3, ...
get_user_info(0)
j = 2
while get_user_info(j):
  j += 1

my_aliases = []
if "alias_addresses" in options_dict:
  my_aliases = [s.strip() for s in options_dict["alias_addresses"].split(",")]



# --------------------------------------------------------------
# Organization locations

def add_slash(s):
  return s if s[-1] == "/" else s + "/"

bomail_data_base = add_slash(options_dict["bomail_location"].replace("~", home))
new_rawmail_dir = add_slash(options_dict["new_rawmail_location"].replace("~", home))
old_rawmail_dir = add_slash(options_dict["processed_rawmail_location"].replace("~", home))

# save a copy of sent messages here if sending from localhost
save_sent_dir = new_rawmail_dir


# --------------------------------------------------------------
# Options not in bomailrc (may edit)

# how many new emails to process at a time, -1 for no limit
process_new_limit = -1

# how many new emails to process in a batch, decrease to save memory
# for very large imports
process_batch_size = 1000

# tag drafts with same tags as parent
autotag_draft_replies = True

# Replying to emails
# will replace %from, %to, %date, %time, %body
# with the corresponding text from the quoted email
quote_format = """\n
%from wrote on %date at %time:
%body"""

# %a is day of week; %Y,%m,%d are year/month/date
# %H,%M are hour/minute
quote_date_fmt = "%a, %Y-%m-%d"  
quote_time_fmt = "%H:%M"         
quote_line_prefix = "> "


# --------------------------------------------------------------
# File locations: suggested not to edit

# Locations of directories
email_dir     = os.path.join(bomail_data_base, "email/")
attach_dir    = os.path.join(bomail_data_base, "attachments/")
drafts_dir    = os.path.join(bomail_data_base, "drafts/")
trash_dir     = os.path.join(bomail_data_base, "trash/")
metadata_dir  = os.path.join(bomail_data_base, "metadata/")

# Locations of files that must be edited by hand
handlers_file      = os.path.join(metadata_dir, "mail-handlers.txt")
addr_alias_file    = os.path.join(metadata_dir, "aliases.txt")

# Locations of files that may be edited by hand
tags_file          = os.path.join(metadata_dir, "tags.txt")
addr_book_file     = os.path.join(metadata_dir, "addr_book.txt")

# Locations of files that should not be hand-edited
openlist_file      = os.path.join(metadata_dir, "openlist.txt")
scheduledlist_file = os.path.join(metadata_dir, "scheduledlist.txt")
msg_ids_file       = os.path.join(metadata_dir, "msg_ids.txt")
tab_config_file    = os.path.join(metadata_dir, "tab_config.py")

# Locations of logs, these can be deleted whenever
acts_log_file      = os.path.join(metadata_dir, "acts_log.txt")
error_log_file     = os.path.join(metadata_dir, "error_log.txt")

for d in [email_dir, attach_dir, drafts_dir, trash_dir, metadata_dir]:
  if not os.path.exists(d):
    os.makedirs(d)

