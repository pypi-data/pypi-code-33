####
# bomail.config.config
#
# Main configuration file.
# When loaded, it tries to open ~/.bomailrc and read it; if unsuccessful,
# it runs a short setup program asking questions.
####

import os, sys

import bomail.config.conf_strs as conf_strs

#--------------------------------------------------------------

old_config_filename = ".bomailrc"
config_filename = "bomail.conf"

home = os.getenv("HOME")
old_config_file = os.path.join(home, old_config_filename)

general_config_dir = os.getenv("XDG_CONFIG_HOME")
if general_config_dir is None or len(general_config_dir) == 0:
  general_config_dir = os.path.join(home, ".config")  # XDG spec
config_dir = general_config_dir
config_file = os.path.join(config_dir, config_filename)

general_data_dir = os.getenv("XDG_DATA_HOME")
if general_data_dir is None or len(general_data_dir) == 0:
  general_data_dir = os.path.join(home, ".local", "share")  # XDG spec
default_data_dir = os.path.join(general_data_dir, "bomail")

default_newmail_dir = os.path.join(home, "mail/new")
default_oldmail_dir = os.path.join(home, "mail/cur")


# Initial setup!
if not os.path.exists(config_file) and not os.path.exists(old_config_file):
  print("\nWelcome to bomail!")

  sys.stdout.write("Name (as it will appear in From line): ")
  sys.stdout.flush()
  myname = sys.stdin.readline().strip()
  sys.stdout.write("Email address (primary, i.e. send email from): ")
  sys.stdout.flush()
  myaddr = sys.stdin.readline().strip()

  sys.stdout.write("Email data location? (leave blank to use " + default_datadir +"): ")
  sys.stdout.flush()
  datadir = sys.stdin.readline().strip()
  if len(datadir) == 0:
    datadir = default_datadir

  sys.stdout.write("Process new mail from where? (leave blank to use " + default_newmail_dir + "): ")
  sys.stdout.flush()
  newmail_dir = sys.stdin.readline().strip()
  if len(newmail_dir) == 0:
    newmail_dir = default_newmail_dir

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
      f.write(conf_strs.bomail_tabcomplete_str)

  # this is not ideal because it doesn't change if the configuration at
  # the bottom of the file changes
  metadata_dir  = os.path.join(datadir, "metadata/")
  handlers_file = os.path.join(metadata_dir, "mail-handlers.txt")
  if not os.path.exists(handlers_file):
    os.makedirs(metadata_dir, exist_ok=True)
    with open(handlers_file, "w") as f:
      f.write(conf_strs.sample_mailhandlers_str)

  s = conf_strs.sample_config_str.replace("YOUR NAME", myname).replace("USER@DOMAIN.COM", myaddr).replace("DATADIR", datadir).replace("NEWMAILDIR",newmail_dir).replace("OLDMAILDIR",oldmail_dir).replace("HOMEDIR",home)
  os.makedirs(config_dir, exist_ok=True)
  with open(config_file, "w") as f:
    f.write(s)

  print(conf_strs.setup_success_str)
  exit(0)



#--------------------------------------------------------------

# migrate from pre-0.9.3 old versions of bomail to 0.9.3
if not os.path.exists(config_file):
  os.makedirs(config_dir, exist_ok=True)
  with open(old_config_file) as f:
    s = f.read()
  with open(config_file, "w") as f:
    f.write(s)
  os.remove(old_config_file)



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
# Organization locations

bomail_data_base = options_dict["data_location"]
new_rawmail_dir = options_dict["new_rawmail_location"]
old_rawmail_dir = options_dict["processed_rawmail_location"]

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
rel_email_dirname = "email/"
rel_drafts_dirname = "drafts/"
rel_attach_dirname = "attachments/"
rel_trash_dirname = "trash/"
rel_metadata_dirname = "metadata/"
email_dir     = os.path.join(bomail_data_base, rel_email_dirname)
attach_dir    = os.path.join(bomail_data_base, rel_attach_dirname)
drafts_dir    = os.path.join(bomail_data_base, rel_drafts_dirname)
trash_dir     = os.path.join(bomail_data_base, rel_trash_dirname)
metadata_dir  = os.path.join(bomail_data_base, rel_metadata_dirname)

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

# --------------------------------------------------------------
# User info

names = []
email_addrs = []
smtp_servernames = []
smtp_ports = []
smtp_usernames = []
smtp_passwords = []

# return True on success, False on failure
# for user 1, there's no suffix e.g. name = MY_NAME
# for users 2 on, there are, e.g. name2 = MY_OTHER_NAME
def get_user_info(j):
  suffix = "" if j==0 else str(j)
  if not ("name" + suffix) in options_dict:
    return False
  name = options_dict["name" + suffix]
  email_addr = options_dict["email_addr" + suffix]
  servname = options_dict["smtp_servername" + suffix]
  if servname == "localhost":
    # no need to get password, port, etc
    smtp_servernames.append(servname)
    names.append(name)
    email_addrs.append(email_addr)
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
    except:
      with open(error_log_file, "a") as f:
        f.write("config: Could not read username/password from " + options_dict["smtp_userpass_file" + suffix])
      return False
  else: # get username and password straight from the config
    uname = options_dict["smtp_username" + suffix]
    pword = options_dict["smtp_password" + suffix]

  smtp_servernames.append(servname)
  names.append(name)
  email_addrs.append(email_addr)
  smtp_usernames.append(uname)
  smtp_passwords.append(pword)
  return True

# first get myname, then myname2, myname3, ...
get_user_info(0)
j = 2
while get_user_info(j):
  j += 1


my_aliases = []
if "alias_addresses" in options_dict:
  my_aliases = [s.strip() for s in options_dict["alias_addresses"].split(",")]


