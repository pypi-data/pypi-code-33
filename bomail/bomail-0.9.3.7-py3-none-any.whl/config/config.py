####
# bomail.config.config
#
# Main configuration file.
# When loaded, it tries to open config file and read it; if unsuccessful,
# it runs a short setup program asking questions.
####

# use: from bomail.config.config import guicfg,sendcfg,optcfg,pathcfg

import os, sys

# check for config file; if not, run setup and exit
from bomail.config.conf_setup import options_dict
import bomail.config.guiconfig as guicfg
import bomail.config.optconfig as optcfg
import bomail.config.pathconfig
import bomail.config.sendconfig

class PathConfig:
  def __init__(self):
    pass
pathcfg = PathConfig()

class SendConfig:
  def __init__(self):
    pass
sendcfg = SendConfig()

# loads pathcfg
def load_paths(new_data_base):
  bomail.config.pathconfig.get_paths(pathcfg,
    options_dict["config_file"],
    new_data_base,
    options_dict["new_rawmail_location"],
    options_dict["processed_rawmail_location"])

load_paths(options_dict["data_location"])

bomail.config.sendconfig.get_sendinfo(sendcfg, options_dict, pathcfg.error_log_file)


