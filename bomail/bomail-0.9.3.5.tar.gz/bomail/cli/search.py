####
# bomail.cli.search
#
# Interface to searching email.
####

import sys
import os, subprocess, shlex
import textwrap

import bomail.cli.mailfile as mailfile
import bomail.cli.chstate as chstate
import bomail.util.search_opts as search_opts

my_usage_str = """
Searches through mail for files matching given arguments.
Currently case-sensitive only.
"""
usage_str = my_usage_str + search_opts.options_str


def is_valid_searchstr(arg_str):
  try:
    shlex.split(arg_str)
    return True
  except:
    return False


# return list of filenames
def search_argstr(arg_str, mgr):
  # note: shlex.split is quite slow, avoid calling it many times per second
  return search_arglist(shlex.split(arg_str), mgr)

# return list of filenames
def search_arglist(args, mgr):
  query = search_opts.SearchQuery()
  query.parse(args)
  return query.search(mgr)

# return list of filenames
def filter_argstr(arg_str, mgr, filelist):
  return filter_arglist(shlex.split(arg_str), mgr, filelist)

# return list of filenames
def filter_arglist(args, mgr, filelist):
  query = search_opts.SearchQuery()
  query.parse(args)
  inds = query.filter(mgr, filelist)
  return [filelist[i] for i in inds]
  

def main_cli():
  args = sys.argv[1:]
  if "-h" in args:
    print(usage_str)
    exit()
  flist = search_arglist(args, mailfile.MailMgr())
  print("\n".join(flist))


if __name__ == "__main__":
  main_cli()

