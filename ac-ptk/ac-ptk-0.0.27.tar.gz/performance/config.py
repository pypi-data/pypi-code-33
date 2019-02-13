import os

from performance import properties

WORK_DIR = '%s/ptk/' % os.path.expandvars('$HOME')

ptk_properties = properties.parse("%s/ptk.properties" % WORK_DIR)

""" debuggale """


def DEBUG():
    return ptk_properties.get_bool("debug", True)


def dump_interval():
    return ptk_properties.get_int("dump_interval", 1)


""" email configuration """


def smtp_server():
    return ptk_properties.get("smtp_server")


def user_name():
    return ptk_properties.get("user_name")


def password():
    return ptk_properties.get("password")


def sender():
    return ptk_properties.get("sender")


def mail_to():
    return ptk_properties.get_arr("mail_to")


def cc():
    return ptk_properties.get_arr("cc")
