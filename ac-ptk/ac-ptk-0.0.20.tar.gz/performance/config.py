import os

from performance import properties

WORK_DIR = '%s/ptk/' % os.path.expandvars('$HOME')

ptk_properties = properties.parse("%s/ptk.properties" % WORK_DIR)

""" debuggale """
DEBUG = ptk_properties.get_bool("debug", True)

""" email configuration """
smtp_server = ptk_properties.get("smtp_server")
user_name = ptk_properties.get("user_name")
password = ptk_properties.get("password")
sender = ptk_properties.get("sender")
cc = ptk_properties.get_arr("cc")
mail_to = ptk_properties.get_arr("mail_to")

""" memory dump """
dump_interval = ptk_properties.get_int("dump_interval", 1)

