####
# bomail.config.sendconfig
#
# Main configuration file.
# When loaded, it tries to open config file and read it; if unsuccessful,
# it runs a short setup program asking questions.
####

import os, sys

from bomail.config.conf_setup import options_dict


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


