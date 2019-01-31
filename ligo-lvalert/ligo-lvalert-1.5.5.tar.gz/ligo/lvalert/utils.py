#!/usr/bin/python
# Copyright (C) Patrick Brady, Brian Moe, Branson Stephens (2015)
#
# This file is part of lvalert
#
# lvalert is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# It is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with lvalert.  If not, see <http://www.gnu.org/licenses/>.

from netrc import netrc, NetrcParseError
import stat
import sys
import os
if os.name == 'posix':
    import pwd
from six.moves.urllib.parse import urlparse
from six import StringIO
from optparse import *
from subprocess import Popen,PIPE

# Note that some of these utilities are not available unless glue is installed.

import warnings
import json

try:
    from glue.ligolw import ligolw
    from glue.ligolw import table
    from glue.ligolw.table import Table
    from glue.ligolw import lsctables
    from glue.ligolw import utils
except ImportError:
    Table = object
else:
    class LIGOLWContentHandler(ligolw.LIGOLWContentHandler):
        pass
    lsctables.use_in(LIGOLWContentHandler)

##############################################################################
#
#          definition of the LVAlertTable
#
##############################################################################

class LVAlertTable(Table):
  """
  for reference, file is written as
  file: //host/path_to_file/file
  uid: the unique id assigned by gracedb
  temp_data_loc: current location (just the directory)
                 of the ouput of the pipeline (this is VOLATILE)
  """
  tableName = "lvalert:table"
  validcolumns = {
    "file": "lstring",
    "uid": "lstring",
    "temp_data_loc": "lstring",
    "alert_type": "lstring",
    "description": "lstring",
    }
    
class LVAlertRow(object):
  __slots__ = list(LVAlertTable.validcolumns.keys())
  
LVAlertTable.RowType = LVAlertRow

##############################################################################
#
#          useful utilities
#
##############################################################################

def parse_file_url(file_url):
  """
  simple function to parse the file urls of the form:
  file://host_name/path_to_file/file
  where path_to_file is assumed to be the /private subdir of a gracedb entry
  returns:
  host: host_name in the above example
  full_path: path_to_file/file in the above example
  general_dir: the /general subdir of the gracedb entry (where data not
  produced by the event supplier should be placed)
  """
  parsed = urlparse(file_url)
  host = parsed[1]
  path, fname = os.path.split(parsed[2])
  
  return host, path, fname

def get_LVAdata_from_stdin(std_in, as_dict=False):
  """
  this function takes an LVAlertTable *OR* a JSON-serialized dictionary from 
  sys.stdin and it returns:

  a full dictionary of the LVAlertTable values, or:

  file: the filename (if any) associated with the alert
  uid: the gracedb unique id associated with the event in the LVAlertTable
  data_loc: a URL for the payload file
  """
  warnings.warn("get_LVAdata_from_stdin is deprecated. Use Python's json module: json.loads(stdin.read())")
  content = std_in.read()
  # Try interpreting it as JSON first.
  try:
    out_dict = json.loads(content)
    file = out_dict['file']
    uid  = out_dict['uid']
    data_loc = out_dict['data_loc']
    description = out_dict['description']
    alert_type = out_dict['alert_type']
  except Exception as e:
    # We don't have a file object anymore, because we .read() it.
    # Instead, we want this to load a blob of text. 
    f = StringIO(content)
    doc = utils.load_fileobj(f, contenthandler = LIGOLWContentHandler)[0]
    lvatable = table.get_table(doc, LVAlertTable.tableName)
    file = lvatable[0].file
    uid = lvatable[0].uid
    data_loc = lvatable[0].temp_data_loc
    description = lvatable[0].description
    alert_type = lvatable[0].alert_type
  if as_dict:
    return {
      "file"        : file,
      "uid"         : uid,
      "data_loc"    : data_loc,
      "description" : description,
      "alert_type"  : alert_type,
    }
  return file, uid, data_loc

def get_LVAdata_from_file(filename, as_dict=False):
  """
  this function takes the name of an xml file containing a single LVAlertTable
  and it returns:
  host: the machine the payload file was created on
  full_path: the full path to (and including) the payload file
  general_dir: the directory in gracedb that the output of your code should
               be written to
  uid: the gracedb unique id associated with the event in the LVAlertTable
  """
  doc = utils.load_filename(filename, contenthandler = LIGOLWContentHandler)
  lvatable = table.get_table(doc, LVAlertTable.tableName)
  file = lvatable[0].file
  uid = lvatable[0].uid
  data_loc = lvatable[0].temp_data_loc

  if as_dict:
    return {
      "file" : lvatable[0].file,
      "uid" : lvatable[0].uid,
      "data_loc" : lvatable[0].temp_data_loc,
      "description" : lvatable[0].description,
      "alert_type" : lvatable[0].alert_type,
    }

  return file, uid, data_loc  

def make_LVAlertTable(file_url, uid, data_loc, alert_type="new", desc=""):
  """
  create xml doc which contains an LVAlert Table
  with submission file file_loc and  data located at data_loc
  """
  xmldoc = ligolw.Document()
  xmldoc.appendChild(ligolw.LIGO_LW())
  lvalerttable = lsctables.New(LVAlertTable)
  row = lvalerttable.RowType()
  row.file = file_url
  row.uid = uid
  row.temp_data_loc = data_loc
  row.alert_type = alert_type
  row.description = desc
  lvalerttable.append(row)
  xmldoc.childNodes[0].appendChild(lvalerttable)

  return xmldoc


#the following is meant as a template for small jobs
#notes:
#   * we only use the vanilla universe which is appropriate for python
#    jobs and things not condor-compiled
#   * it only works for single-process jobs; anything more complicated will
#    require a dag
condor_sub_template = \
                    """
                    universe = vanilla
                    executable = macroexecutible
                    arguments = macroargs
                    log = macrolog
                    error = macroerr
                    output = macroout
                    getenv = True
                    notification = never
                    queue
                    """
def write_condor_sub(executible, args, logdir, uid):
  """
  write a simple condor submission file
  uid: unique id used in naming the files (to avoid conflicts)
  executible: the name of the executible file
  args: a list of arguments to executible
  logdir: directory to keep log files
  returns the name of the file
  """
  subfile = condor_sub_template.replace('macroexecutible', executible)\
            .replace('macroargs', args)\
            .replace('macrolog', os.path.join(logdir,str(uid)+'.log'))\
            .replace('macroerr', os.path.join(logdir,str(uid)+'.err'))\
            .replace('macroout', os.path.join(logdir,str(uid)+'.out'))
  fname = str(uid) + '.sub'
  f = open(fname,'w')
  f.write(subfile)
  f.close()

  return fname

def submit_condor_job(subfile):
  """
  submit the subfile to condor
  returns the process id
  """
  p = Popen(["condor_submit "+subfile], shell=True).pid
  
  return p

class safe_netrc(netrc):
    """The netrc.netrc class from the Python standard library applies access
    safety checks (requiring that the netrc file is readable only by the
    current user, and not by group members or other users) only if using the
    netrc file in the default location (~/.netrc). This subclass applies the
    same access safety checks regardless of the path to the netrc file."""

    def _parse(self, file, fp, *args, **kwargs):
        # Copied and adapted from netrc.py from Python 2.7
        if os.name == 'posix':
            prop = os.fstat(fp.fileno())
            if prop.st_uid != os.getuid():
                try:
                    fowner = pwd.getpwuid(prop.st_uid)[0]
                except KeyError:
                    fowner = 'uid %s' % prop.st_uid
                try:
                    user = pwd.getpwuid(os.getuid())[0]
                except KeyError:
                    user = 'uid %s' % os.getuid()
                raise NetrcParseError(
                    ("~/.netrc file owner (%s) does not match"
                     " current user (%s)") % (fowner, user),
                    file)
            if (prop.st_mode & (stat.S_IRWXG | stat.S_IRWXO)):
                raise NetrcParseError(
                   "~/.netrc access too permissive: access"
                   " permissions must restrict access to only"
                   " the owner", file)
        return netrc._parse(self, file, fp, *args, **kwargs)
