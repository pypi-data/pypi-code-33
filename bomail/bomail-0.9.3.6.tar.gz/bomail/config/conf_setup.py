
import os, sys

import bomail.config.conf_strs as conf_strs

# this file checks for the configuration file
# if not found, it runs a setup and exists
# otherwise, it parses it into options_dict

# save location of config file (and old config file)
old_config_filename = ".bomailrc"
config_filename = "bomail.conf"

home = os.getenv("HOME")

# pre-0.9.3 versions
old_config_file = os.path.join(home, old_config_filename)

# post-0.9.3 versions
general_config_dir = os.getenv("XDG_CONFIG_HOME")
if general_config_dir is None or len(general_config_dir) == 0:
  general_config_dir = os.path.join(home, ".config")  # XDG spec
config_dir = general_config_dir

config_file = os.path.join(config_dir, config_filename)


# Check for config file, if found return
# otherwise, run setup and exit(0)
if not os.path.exists(config_file) and not os.path.exists(old_config_file):
  # do setup!
  general_data_dir = os.getenv("XDG_DATA_HOME")
  if general_data_dir is None or len(general_data_dir) == 0:
    general_data_dir = os.path.join(home, ".local", "share")  # XDG spec
  default_datadir = os.path.join(general_data_dir, "bomail")
  
  default_newmail_dir = os.path.join(home, "mail/new")
  default_oldmail_dir = os.path.join(home, "mail/cur")
  
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

  print("""
Basic setup successful!
 (1) Edit """ + config_file + """ in order to send email and other options.
 (2) Edit """ + handlers_file + """ for filtering new mail.

Run bomail to begin...
""")
  exit(0)

# migrate from pre-0.9.3 old versions of bomail to 0.9.3
if not os.path.exists(config_file): # then old_config_file exists
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

options_dict["config_file"] = config_file

