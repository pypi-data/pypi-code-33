"""
Data Science Workspace Utility

Utilty functions for working with workspace libraries
"""

import subprocess                                          as _subprocess
import os                                                  as _os
from IPython.core.display import display                   as _display
from IPython.core.display import HTML                      as _HTML
import numpy                                               as _np
import re                                                  as _re
import shlex                                               as _shlex
import time                                                as _time 


def pretty(df, max_lines=50, col="lightgray"):
    df = df[:max_lines].to_html(index=False)
    df = df.replace('<th>','<th style="text-align:center;background-color:%s">' % col)
    _display(_HTML("<div align=center>" + df + "</div>"))


def sp(cmd_lst,shell=False):
    alt_env = _os.environ.copy()
    #REF: Haven't neded yet, can use alt_env
    #alt_env["PATH"] = "/usr/bin:" + alt_env["PATH"]
    sp = _subprocess.Popen(cmd_lst, env=alt_env, 
                          stdout=_subprocess.PIPE,
                          stderr=_subprocess.PIPE,
                          shell=shell)
    return(sp.communicate())

  
def launch_term(cli=''):
    f=open(".picker","wb")
    f.write(cli.encode('utf8'))
    f.close()
    id=_os.environ["CDSW_ENGINE_ID"]
    cd=_os.environ["CDSW_DOMAIN"]
    tp = [p for p in sp(["ps","aux"])[0].split() \
          if b'--path' in p][0][8:]
    url="http://tty-%s.%s/%s/"%(id,cd,tp.decode('utf8'))
    script='<script type="text/Javascript">window.open("%s");</script>'%url
    _display(_HTML(script))
    _time.sleep(6) 
    f=open(".picker","wb")
    f.write(''.encode('utf-8'))
    f.close()

def launch_url(url=None):
    """
    Launches url
    """
    script='<script type="text/Javascript">window.open("%s");</script>'%url
    _display(_HTML(script))
    _time.sleep(4)
    
def standard_cli_qry(qry):
    """
    Standard form for cli queries
    
    Allows three forms:
      starts with '-', parses with no further checks
      find first word is file, -f <path> no further checks
      otherwise parses as query, -e and text
    """
    if "." in qry.split()[0]:
        if "/" not in qry.split()[0]:
            _os.environ['PROJECT_HOME']="/home/cdsw"
            qry=_os.environ['PROJECT_HOME']+"/sql/"+qry
        rslt=["-f",qry]
    elif qry[0][0]=="-":
        rslt=_shlex.split(qry)
    else:
        rslt=["-e",qry]
    return(rslt)


def standard_conn_qry(qry):
    """
    Standard form for connection queries
    
    Allows grouping of commands using ";" seperator
    Each command can have the following form:
       Standard executable statement
       single file, read as sql
    """
    if qry.__class__ == str:
        qry=[q for q in qry.split(";") if q!='']
    rslt=[]
    for q in qry:
        if q[0]=="-":
            q=" ".join(q.split()[1:]).strip('"').strip("'")
        if "." in q.split()[0]:
            f==q.split()[0]
            if "/" not in f:
                _os.environ['PROJECT_HOME']="/home/cdsw"
                f=_os.environ['PROJECT_HOME']+"/sql/"+f
            f=open(f,'r')
            l=[x for x in f.read().split('\n') if x[:2]!='--']
            q=[_re.sub('\\s+',' ',x) for x in " ".join(l).split(";") if x!='']
        rslt+=[q,]
    return(rslt)


def standard_sess_qry(qry):
    """
    Standard form for session queries
    
    Does not allow grouping of commands using ";" seperator
    only first query selected if found.
    Each command can have the following form:
       Standard executable statement
       single file, read as sql
    """
    if qry.__class__ == str:
        qry=qry.split(";")[0]
    q=qry
    if "." in q.split()[0]:
        f==q.split()
        if "/" not in f:
            _os.environ['PROJECT_HOME']="/home/cdsw"
            f=_os.environ['PROJECT_HOME']+"/sql/"+f
        f=open(f,'r')
        l=[x for x in f.read().split('\n') if x[:2]!='--']
        q=[_re.sub('\\s+',' ',x) for x in " ".join(l).split(";") if x!='']
    return(q)
  
def qry_type(qry):
    """
    Determine query type; cli or conn
    
    Looks for cli args, or file submission for cli else conn
    Use for determining types within magics - sess type is not
    included since they will have their own deticated magics
    """
    if qry[0]=="-" or "." in qry.split()[0]:
        return("cli")
    else:
        return("conn")

def no_return(qry):
    """
    Query logic to capture queries that have no return
    other than successfull or not"""
    return(("CREATE TABLE" in qry.upper()) |
           (("SELECT" not in qry.upper()) & ("SHOW" not in qry.upper())) )
    
    
    
