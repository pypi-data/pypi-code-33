
# change the configuration file automatically

import sys, os
import tempfile

import bomail.config.config as config


# change a line of the bomail.conf file of the form "opt_name = value"
def change_option(opt_name, new_value):
  with open(config.config_file) as fromf:
    lines = fromf.readlines()
  for i,line in enumerate(lines):
    if line.startswith(opt_name + " ="):
      lines[i] = opt_name + " = " + new_value + "\n"  # need newline
  with open(config.config_file, "w") as tof:
    tof.write("".join(lines))


