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

# return True on success, False on failure
# for user 1, there's no suffix e.g. name = MY_NAME
# for users 2 on, there are, e.g. name2 = MY_OTHER_NAME
def get_user_info(sendcfg, options_dict, error_log_file, j):
  suffix = "" if j<=1 else str(j)
  if not ("name" + suffix) in options_dict:
    return False
  name = options_dict["name" + suffix]
  email_addr = options_dict["email_addr" + suffix]
  servname = options_dict["smtp_servername" + suffix]
  if servname == "localhost":
    # no need to get password, port, etc
    sendcfg.smtp_servernames.append(servname)
    sendcfg.names.append(name)
    sendcfg.email_addrs.append(email_addr)
    return True
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

  sendcfg.names.append(name)
  sendcfg.email_addrs.append(email_addr)
  sendcfg.smtp_servernames.append(servname)
  sendcfg.smtp_ports.append(int(options_dict["smtp_port" + suffix]))
  sendcfg.smtp_usernames.append(uname)
  sendcfg.smtp_passwords.append(pword)
  return True

def get_sendinfo(sendcfg, options_dict, error_log_file):
  sendcfg.names = []
  sendcfg.email_addrs = []
  sendcfg.smtp_servernames = []
  sendcfg.smtp_ports = []
  sendcfg.smtp_usernames = []
  sendcfg.smtp_passwords = []

  # first get myname, then myname2, myname3, ...
  get_user_info(sendcfg, options_dict, error_log_file, 0)
  j = 2
  while get_user_info(sendcfg, options_dict, error_log_file, j):
    j += 1

  sendcfg.my_aliases = []
  if "alias_addresses" in options_dict:
    sendcfg.my_aliases = [s.strip() for s in options_dict["alias_addresses"].split(",")]


