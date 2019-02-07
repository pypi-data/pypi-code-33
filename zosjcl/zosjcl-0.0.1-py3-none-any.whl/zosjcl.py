# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
import socket

class QueryError(Exception):
    pass


class FileNameError(Exception):
    pass

class ZosJCL:

    def __init__(self, user='USERNAME', dsn='USERNAME.LIB.'):
        self.user = user
        self.job_header = '//' + self.user + "A JOB ,'  -- ZOS -- ',MSGCLASS=X,NOTIFY=&SYSUID" + "\n"
        self.dsn = dsn


    def change_jobheader(self, jobheader):
        self.job_header=jobheader
        if "\n" not in self.job_header:
            self.job_header = self.job_header + "\n"
        return self.job_header


    def jobheader(self):
        return self.job_header


    def delete_files(self, files):
        jcl = """//%%STEP%%  EXEC PGM=IDCAMS
//SYSPRINT DD  SYSOUT=*
//UTPRINT  DD  SYSOUT=*
//SYSIN    DD  *
%%COMANDOS%%"""
        txt = ''
        for i in files:
            delete_file = self.create_filename(i)
            txt += "         DELETE {} PURGE\n".format(delete_file)
        txt += "         SET MAXCC=0\n"
        return jcl.replace('%%COMANDOS%%', txt)

    def create_filename(self, file):
        if len(file.split('.')) == 1: # because I'm getting (example) 'COL' instead of 'USERNAME.LIB.XXXX'
            file = self.dsn + file

        for i in file.split('.'):
            if len(i) > 8:
                raise FileNameError('Invalid filename. Maybe the filename size (dsn) have len() > 8 !?')
                exit()

        return file


    def create_query_columns(self, tbname):

        if tbname.count('.') == 2:
            ambiente = tbname.split('.')[0]
            connection = tbname.split('.')[1]
            tabela = tbname.split('.')[2]
        elif tbname.count('.') == 1:
            ambiente = ''
            connection = tbname.split('.')[0]
            tabela = tbname.split('.')[1]
        else:
            raise Exception("I cant work with this table name! Sorry!!!" )

        str = """SELECT NAME, COLNO, COLTYPE, LENGTH, SCALE, NULLS
        FROM {}SYSIBM.SYSCOLUMNS
        WHERE TBNAME = '{}'
          AND TBCREATOR = '{}'
        ORDER BY COLNO"""

        return str.format(ambiente, tabela, connection)


    def unload_table_definition(self, tbname, output_file, space='(CYL,(1,1),RLSE)'):
        file = self.create_filename(output_file)
        jcl = """//%%STEP%% EXEC PGM=INZUTILB,PARM=('EP=UTLGLCTL/DSN'),REGION=0M
//SYSOUT   DD  SYSOUT=*
//SYSDBOUT DD  SYSOUT=*
//SYSPRINT DD  SYSOUT=*
//CEEDUMP  DD  SYSOUT=*
//SYSUDUMP DD  SYSOUT=F
//SYSTSPRT DD  SYSOUT=*
//CPYDDN   DD  DUMMY
//SYSPUNCH DD  DUMMY
//SYSREC00 DD DSN=%%MFFILE%%,
//             DISP=(NEW,CATLG,CATLG),  *GDG(+1)
//             DCB=(CORTEX.DSCB),
//             UNIT=(SYSDA),SPACE=%%SPACE%%
//SYSIN    DD  *

 UNLOAD TABLESPACE
 LOCK NO QUIESCE NO

%%QUERY%%


 OUTDDN(SYSREC00)
 FORMAT DELIMITED SEP X'5E' DELIM '"'
 OPTIONS PIC ('P',LEAD,',','*.0')
"""
        query = self.create_query_columns(tbname)
        return jcl.replace('%%QUERY%%', query).replace('%%MFFILE%%', file).replace('%%SPACE%%',space)

    def unload_query(self, query, output_file, space='(CYL,(1,1),RLSE)'):

        file = self.create_filename(output_file)
        jcl = """//%%STEP%% EXEC PGM=INZUTILB,PARM='DSN,STEP001',REGION=0M
//SYSOUT   DD  SYSOUT=*
//SYSDBOUT DD  SYSOUT=*
//SYSPRINT DD  SYSOUT=*
//CEEDUMP  DD  SYSOUT=*
//SYSUDUMP DD  SYSOUT=F
//SYSTSPRT DD  SYSOUT=*
//CPYDDN   DD  DUMMY
//SYSPUNCH DD  DUMMY
//SYSREC00 DD DSN=%%MFFILE%%,
//             DISP=(NEW,CATLG,CATLG),  *GDG(+1)
//             DCB=(CORTEX.DSCB),
//             UNIT=(SYSDA),SPACE=%%SPACE%%
//SYSIN    DD  *

 UNLOAD TABLESPACE
 LOCK NO QUIESCE NO

%%QUERY%%


 OUTDDN(SYSREC00)
 FORMAT DELIMITED SEP X'5E' DELIM '"'
 OPTIONS PIC ('P',LEAD,',','*.0')
"""
        return jcl.replace('%%QUERY%%', query).replace('%%MFFILE%%', file).replace('%%SPACE%%',space)


    def receive_files(self, file_list):
        """
        ### 
        ### receive a filename in the workstation via ftp on port 8021
        ###
        ###  I'm not proud in the following code... it works for me.
        """
        jcl = """//%%STEP%% EXEC PGM=FTP
//SYSPRINT DD  SYSOUT=*
//SYSUDUMP DD  SYSOUT=*
//SYSSUM   DD  SYSOUT=*
//SYSMAP   DD  SYSOUT=*
//SYSPUNCH DD  SYSOUT=*
//UTPRINT  DD  SYSOUT=*
//OUTPUT   DD  SYSOUT=*
//ENVIA    DD  DUMMY
//INPUT    DD *
%%IP%% %%PORT%%
user mypass
LOCSITE SBDATACONN=(IBM-037,ISO8859-1)
%%COMANDOS%%QUIT
"""
        txt = ''
        for i in file_list:
            delete_file = self.create_filename(i)
            txt += "PUT '" + delete_file + "' " + i.lower() + '.csv' + "\n"
        return jcl.replace('%%COMANDOS%%', txt).replace('%%IP%%', socket.gethostbyaddr(socket.gethostname())[2][0]).replace('%%PORT%%', '8021')

    def build_steps(self, txt):

        cnt = 1
        while '%%STEP%%' in txt:
            txt = txt.replace('%%STEP%%', 'STEP' + str(cnt).rjust(3,str('0')), 1)
            cnt += 1
        return txt


    def select_all_fields_from(self, tbname, where_condition, file, space='(CYL,(1,1),RLSE)'):

        if 'WHERE' not in where_condition.upper():
            raise QueryError('select_all_fields_from: you must code a "WHERE" condition')

        for i in where_condition.split("\n"):
            if len(i.strip()) > 80:
                raise QueryError('select_all_fields_from: the "WHERE" condition is limited to 80bytes per line')

        sql = "SELECT * FROM {}\n".format(tbname)
        sql += where_condition

        return self.unload_query(sql, file, space=space)

    
    def execute_fileman(self, member_name):
        """
        execute filemanager and print output to self.user + '.FILEMAN.OUTPUT'
        #
        # Must work on this!
        # 
        """
        lib = member_name.strip().split('(')[0]
        member = member_name.strip().split('(')[1].strip(')')
        
        output_file = self.user + '.FILEMAN.OUTPUT'
        jcl = self.delete_files([output_file])
        jcl += """//%%STEP%% EXEC PGM=FMNMAIN,COND=(0,NE)                         
//SYSOUT   DD SYSOUT=*                                          
//FMNTSPRT DD SYSOUT=*                                          
//*SYSPRINT DD SYSOUT=*                                         
//SYSPRINT DD DISP=(NEW,CATLG,CATLG),
//           DSN={},
//           UNIT=(SYSDA),SPACE=(CYL,(1,1),RLSE,,ROUND),        
//           DCB=(CORTEX.DSCB,RECFM=FB,LRECL=150,BLKSIZE=27900) 
//SYSTERM  DD SYSOUT=*                                          
//SYSIN    DD *                                                 
$$FILEM SET HEADERPG=YES,PAGESIZE=60                            
$$FILEM PBK DSNIN={},                            
$$FILEM LANG=COBOL,                                             
$$FILEM CBLMAXRC=08,                                            
$$FILEM OVERRIDE=YES,                                           
$$FILEM CBLLIBS=(,                                              
$$FILEM     ),                                                  
$$FILEM ARRAY=YES,                                              
$$FILEM MEMBER={}
"""
        return jcl.format(output_file, lib, member)

if __name__ == "__main__":

    a = ZosJCL()
    jcl  = a.jobheader()
    jcl += a.delete_files(['COLS','UNL'])
    jcl += a.unload_table_definition('DSVDB2.TRT030_TRANSFR', 'COLS')
    jcl += a.select_all_fields_from('DSVDB2.TRT030_TRANSFR', "WHERE SCT_REFMSG = '7'", 'UNL')
    jcl += a.receive_files(['COLS', 'UNL'])
    jcl += a.delete_files(['COLS', 'UNL'])
    """
    jcl += a.execute_fileman('DES.TPS.BRUNO(DOT002)')
    """
    jcl = a.build_steps(jcl)

    print(jcl)