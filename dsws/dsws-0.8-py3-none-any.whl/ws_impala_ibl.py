
# Imapala beeline via hive2 driver is not viable due to lost columns issue
# beeline -u 'jdbc:hive2://bottou04.sjc.cloudera.com:21050/default;auth=noSasl'
# Thus, need to execute the following steps:
# * download the impala driver from https://www.cloudera.com/downloads/connectors/impala/jdbc
# * unpack & save to ~/jdbc/impala_41, chose location from following link
#   https://www.cloudera.com/documentation/enterprise/latest/topics/impala_jdbc.html
# HADOOP_CLASSPATH=/home/cdsw/jdbc/impala_41/* beeline -d "com.cloudera.impala.jdbc41.Driver" -u 'jdbc:impala://bottou01.sjc.cloudera.com:21050/bgg;AuthMech=0'
# http://www.ericlin.me/2017/04/how-to-use-beeline-to-connect-to-impala/
# strong preference goes towards having impala-shell avaialble, but
# there are python versions dependencies issues that have to be imitigated in 
# the docker container first before that is viable.


import pandas                            as _pd
from dsws.util import pretty             as _pretty
from dsws.util import sp                 as _sp
from os import environ                   as _env
import re                                as _re
from ast import literal_eval             as _literal_eval
from dsws.util import standard_cli_qry   as _standard_cli_qry


class Ibl:

    def __init__(self):
        conf=_literal_eval(_env[self.__module__.split(".")[-1].upper()])
        self.command=conf['command']
        self.qryconf=dict([(a,conf[a]) for a in conf if a.isupper()])

        
    def qry(self,qry,r_type="df",limit=0):
        """
        Run an impala beeline command
        
        qry in form accepted by dsws.util.standard_cli_qry
        r_type is "disp","df","msg","cmd"
        """
        qry=_standard_cli_qry(qry)
        qry[0]="-e" if qry[0]=="-q" else qry[0]
        if qry[0]=="-e":
            for k in self.qryconf:
                setter="SET %s=%s;" % (k,self.qryconf[k])
                qry[1]=setter+qry[1]
            qry[1]+=";"
            qry[1]='"'+_re.sub('"','\\'+'\"',qry[1])+'"'
        cmd=self.command+" ".join(qry)
        if r_type=="cmd":
            return(cmd)
        rslt = _sp(cmd, shell=True)
        if r_type in ("df","disp"):
            dat=rslt[0].split('\n')
            cols = [c.strip() for c in rslt[0].split('\n')[1].split('|')[1:-1]]
            col_count = len(cols)
            rows = [tuple(c.strip() for c in r.split('|')[1:-1]) for r in rslt[0].split('\n')[3:-2]]
            rows = [r for r in rows if len(r)==col_count]
            rslt = _pd.DataFrame(rows,columns=cols)        
            if r_type=="disp":
                _pretty(rslt,col="#5697cb")
                rslt=None
        elif r_type=="msg":
            rslt=rslt[1].split('\n')[-4]
        else:
            rslt=None
        return(rslt)