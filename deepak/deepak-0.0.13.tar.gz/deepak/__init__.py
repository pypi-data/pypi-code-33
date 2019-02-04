#coding: utf-8
import os
import sys
sys.tracebacklimit=0
import platform
import subprocess
import getpass


def install():
    jpath = 'notSet'
    while (jpath == 'notSet'):
        jpath=javapath()
    #print jpath
    server_type = ''
    while (server_type != 'tomcat' and server_type != 'jboss'):
        server_type=server()
    app_server_path = app_deploy(server_type)
    print "DB Connection Details for the application Server"
    print 'Application Deployed Lets proceed with DB Changes'
    db_type=''
    while (db_type != 'OracleSQL' and db_type != 'MySQL'):
        db_type=dbselect()
    dbase=db(server_type,db_type,app_server_path)
    return ('You have successfully Install Canvas!!! Ready to Rock and Roll')

def remove():
     print "Remove is yet to Implement"
     return ('Thanks for Choosing Canvas')

def upgrade():
     print "Upgrade is yet to Implement"
     return ('Thanks for Choosing Canvas')

def server():
    server_value=raw_input('Enter Server Preference 1.Tomcat 2.Jboss (input 1 or 2): ')
    val = 0
    try:
        val = int(server_value)
    except ValueError:
        print("input is not valid, Try again!!!")
        return ''
    if(val ==1 or val==2):
        if(val ==1):
            print 'You have choose Tomcat as your Application Server'
            return 'tomcat'
        if(val ==2):
            print 'You have choose JBOSS as your Application Server'
            return 'jboss'
    else:
        print 'Choose between 1 and 2'
        print 'Please try again!!!'
        return ''

def dbselect():
    db_value=raw_input('Enter DB Preference 1.OracleSQL 2.MySQL (input 1 or 2): ')
    val = 0
    try:
        val = int(db_value)
    except ValueError:
        print("input is not valid, Try again!!!")
        return ''
    if(val ==1 or val==2):
        if(val ==1):
            print 'You have choose OracleSQL as your Database'
            return 'OracleSQL'
        if(val ==2):
            print 'You have choose MySQL as your Database'
            return 'MySQL'
    else:
        print 'Choose between 1 and 2'
        print 'Please try again!!!'
        return ''

def javapath():
    platform_check = platform.system()
    print platform_check
    if(platform_check == "Linux"):
        javapath=raw_input('Enter Java path(Supports java 1.8+ ) : ')
        #java_string = javapath + " -version 2>&1 | awk -F[\\\"_] 'NR==1{print $2}'"
        java_string = javapath + " -version 2>&1 | awk -F[\\\"\.] -v OFS=. \'NR==1{print $2,$3}\'"
        #print java_string
        java_version = subprocess.check_output(java_string, shell=True)
        print java_version.strip()
        if(java_version.strip() == '.'):
            print "Please Enter the valid Java Path"
            return 'notSet'
        java_float = 0.0
        try:
            java_float = float(java_version)
        except ValueError:
            java_float = float(java_version.split("-")[0])
            #java_float = 1 + (int(java_version)*0.1)
        print java_float

        if (float(java_float) >= 1.8):
            print 'Java Version Compertable with the bench mark. Lets Proceed Further!!!'
        else:
            print 'Java version not supported!!!'
            exit()
        #print java_version
        return javapath

def app_deploy(server_type):
    #print 'inside app deploy: ' + server_type
    if (server_type == 'tomcat'):
        tomcatpath=raw_input('Enter Tomcat base path(If you dont have tomcat Please install tomcat) : ')
        if not os.path.exists(tomcatpath):
            print "File path not exist && please recheck it once and try again"
            tomcatpath=raw_input('Enter Tomcat base path(If you dont have tomcat Please install tomcat) : ')
            if not os.path.exists(tomcatpath):
                print "File path not exist & you have exceed your limit please install tomcat and try again"
                exit()
        #dirname = os.path.dirname(__file__)
        #print dirname
        if not os.path.exists(tomcatpath+ "/webapps"):
            print 'unable to find the Webapp folder: '+tomcatpath+ '/webapps'
            exit()
        if not os.path.exists(tomcatpath+ "/bin"):
            print 'unable to find the bin folder: '+tomcatpath+ '/bin'
            exit()
        #print (os.path.exists("~/.canvas"))
        if os.path.exists("/var/.canvas"):
            if os.path.exists("/var/.canvas/jenkins.war"):
                print 'Latest War'
            else:
                subprocess.check_output("wget http://mirrors.jenkins.io/war-stable/latest/jenkins.war && mv jenkins.war /var/.canvas/jenkins.war && chmod +x /var/.canvas/jenkins.war", shell=True)
        else:
            subprocess.check_output("mkdir /var/.canvas && mkdir /var/.canvas/template && wget http://mirrors.jenkins.io/war-stable/latest/jenkins.war && mv jenkins.war /var/.canvas/jenkins.war && chmod +x /var/.canvas/jenkins.war", shell=True)
        if os.path.exists(tomcatpath+ "/jenkins.war"):
            subprocess.check_output(" rm -rf " +tomcatpath+"/jenkins.war && rm -rf " +tomcatpath.strip()+"/webapps/jenkins", shell=True)

        tomcat_status = subprocess.check_output("cp /var/.canvas/jenkins.war "+tomcatpath.strip()+"/webapps", shell=True)
        print 'War Deployed'
        return tomcatpath
    if (server_type == 'jboss'):
        jbosspath=raw_input('Enter Jboss base path(If you dont have JBoss Please install Jboss) : ')
        if not os.path.exists(jbosspath):
            print "File path not exist && please recheck it once and try again"
            jbosspath=raw_input('Enter Jboss base path(If you dont have tomcat Please install Jboss) : ')
            if not os.path.exists(jbosspath):
                print "File path not exist & you have exceed your limit!!! please install Jboss and try again"
                exit()
        if not os.path.exists(jbosspath+ "/standalone"):
            print 'unable to find the Standalone folder: '+jbosspath+ '/standalone'
            exit()
        if not os.path.exists(jbosspath+ "/bin"):
            print 'unable to find the bin folder: '+jbosspath+ '/bin'
            exit()
        #print (os.path.exists("~/.canvas"))
        if os.path.exists("/var/.canvas"):
            if os.path.exists("/var/.canvas/jenkins.war"):
                print 'Latest War Exist in Canvas Home folder!!!'
            else:
                subprocess.check_output("wget http://mirrors.jenkins.io/war-stable/latest/jenkins.war && mv jenkins.war /var/.canvas/jenkins.war && chmod +x /var/.canvas/jenkins.war", shell=True)
        else:
            subprocess.check_output("mkdir /var/.canvas && wget http://mirrors.jenkins.io/war-stable/latest/jenkins.war && mv jenkins.war /var/.canvas/jenkins.war && chmod +x /var/.canvas/jenkins.war", shell=True)
        if os.path.exists(jbosspath+ "/jenkins.war"):
            subprocess.check_output(" rm -rf " +jbosspath+"/jenkins.war && rm -rf " +jbosspath.strip()+"/webapps/jenkins", shell=True)

        jboss_status = subprocess.check_output("cp /var/.canvas/jenkins.war "+jbosspath.strip()+"/standalone", shell=True)
        print 'War Deployed'
        return jbosspath

def db(server_type,db_type,app_server_path):
    print server_type +' :  '+ db_type
    dbip=raw_input('Please provide the Database IP/FQDN: ')
    dbport=raw_input('Please provide the Database Port: ')
    dbuser=raw_input('Please provide the Database user: ')
    dbpass= getpass.getpass('Please provide the Database password(password will not be displayed): ')
    subprocess.check_output("rm -rf /var/.canvas/tmpl && git clone https://github.com/sunlove123/tmpl.git /var/.canvas/tmpl", shell=True)
    if not os.path.exists("/var/.canvas/template"):
        subprocess.check_output("mkdir /var/.canvas/template", shell=True)
    subprocess.check_output("cp /var/.canvas/tmpl/* /var/.canvas/template/", shell=True)
    subprocess.check_output("sed -i 's/{ip}/'"+dbip+"'/g' /var/.canvas/template/*", shell=True)
    subprocess.check_output("sed -i 's/{port}/'"+dbport+"'/g' /var/.canvas/template/*", shell=True)
    subprocess.check_output("sed -i 's/{user}/'"+dbuser+"'/g' /var/.canvas/template/*", shell=True)
    subprocess.check_output("sed -i 's/{pass}/'"+dbpass+"'/g' /var/.canvas/template/*", shell=True)
    #subprocess.check_output("cp /var/.canvas/template/", shell=True)
    if (server_type == 'tomcat'):
        if (db_type == 'MySQL'):
            dbflag  = 0
            with open(app_server_path + '/conf/server.xml', 'r') as fh:
                if 'ModelHouseCT' in line or 'ModelHouse' in line or 'ExpertStudio' in line or 'ExpertStudioTarget' in line:
                    dbflag = 1
                    print 'DB Entries already present in server.xml'
                    break
            if dbflag == 0:
                tmp = open("/tmp/temp_server.xml", 'w')
                f = open('/var/.canvas/template/s.txt', 'r')
                text = f.read().strip()
                f.close()
                with open(app_server_path + '/conf/server.xml', 'r+') as fh:
                    for line in fh:
                        tmp.write(line)
                        if '<GlobalNamingResources>' in line:
                            tmp.write(text)
                tmp.close()
            dbflag  = 0
            with open(app_server_path + '/conf/config.xml', 'r') as fh:
                if 'ModelHouseCT' in line or 'ModelHouse' in line or 'ExpertStudio' in line or 'ExpertStudioTarget' in line:
                    dbflag = 1
                    print 'DB Entries already present in config.xml'
                    break
            if dbflag == 0:
                tmp = open("/tmp/temp_config.xml", 'w')
                f = open('/var/.canvas/template/c.txt', 'r')
                text = f.read().strip()
                f.close()
                with open(app_server_path + '/conf/config.xml', 'r+') as fh:
                    for line in fh:
                        tmp.write(line)
                        if '<Context>' in line:
                            tmp.write(text)
                tmp.close()
            if dbflag == 0:
                subprocess.check_output("mv /tmp/temp_server.xml " +app_server_path + "/conf/server.xml", shell=True)
                subprocess.check_output("mv /tmp/temp_config.xml " +app_server_path + "/conf/config.xml", shell=True)
        if (db_type == 'OracleSQL'):
            dbflag  = 0
            with open(app_server_path + '/conf/server.xml', 'r') as fh:
                if 'ModelHouseCT' in line or 'ModelHouse' in line or 'ExpertStudio' in line or 'ExpertStudioTarget' in line:
                    dbflag = 1
                    print 'DB Entries already present in server.xml'
                    break
            if dbflag == 0:
                tmp = open("/tmp/temp_server.xml", 'w')
                f = open('/var/.canvas/template/s.txt', 'r')
                text = f.read().strip()
                f.close()
                with open(app_server_path + '/conf/server.xml', 'r+') as fh:
                    for line in fh:
                        tmp.write(line)
                        if '<GlobalNamingResources>' in line:
                            tmp.write(text)
                tmp.close()
            dbflag  = 0
            with open(app_server_path + '/conf/config.xml', 'r') as fh:
                if 'ModelHouseCT' in line or 'ModelHouse' in line or 'ExpertStudio' in line or 'ExpertStudioTarget' in line:
                    dbflag = 1
                    print 'DB Entries already present in config.xml'
                    break
            if dbflag == 0:
                tmp = open("/tmp/temp_config.xml", 'w')
                f = open('/var/.canvas/template/c.txt', 'r')
                text = f.read().strip()
                f.close()
                with open(app_server_path + '/conf/config.xml', 'r+') as fh:
                    for line in fh:
                        tmp.write(line)
                        if '<Context>' in line:
                            tmp.write(text)
                tmp.close()
            if dbflag == 0:
                subprocess.check_output("mv /tmp/temp_server.xml " +app_server_path + "/conf/server.xml", shell=True)
                subprocess.check_output("mv /tmp/temp_config.xml " +app_server_path + "/conf/config.xml", shell=True)

    if (server_type == 'jboss'):
        if (db_type == 'MySQL'):
            dbflag  = 0
            with open(app_server_path + '/standalone/configuration/standalone.xml', 'r') as fh:
                if 'ModelHouseCT' in line or 'ModelHouse' in line or 'ExpertStudio' in line or 'ExpertStudioTarget' in line:
                    dbflag = 1
                    print 'DB Entries already present in Standalone.xml'
                    break
            if dbflag == 0:
                tmp = open("/tmp/temp_standalone.xml", 'w')
                f = open('/var/.canvas/template/sa.txt', 'r')
                text = f.read().strip()
                f.close()
                with open(app_server_path + '/standalone/configuration/standalone.xml', 'r+') as fh:
                    for line in fh:
                        tmp.write(line)
                        if '<datasources>' in line:
                            tmp.write(text)
                tmp.close()
            if dbflag == 0:
                subprocess.check_output("mv /tmp/temp_standalone.xml " +app_server_path + "/standalone/configuration/standalone.xml", shell=True)

        if (db_type == 'OracleSQL'):
            dbflag  = 0
            with open(app_server_path + '/standalone/configuration/standalone.xml', 'r') as fh:
                if 'ModelHouseCT' in line or 'ModelHouse' in line or 'ExpertStudio' in line or 'ExpertStudioTarget' in line:
                    dbflag = 1
                    print 'DB Entries already present in Standalone.xml'
                    break
            if dbflag == 0:
                tmp = open("/tmp/temp_standalone.xml", 'w')
                f = open('/var/.canvas/template/sa.txt', 'r')
                text = f.read().strip()
                f.close()
                with open(app_server_path + '/standalone/configuration/standalone.xml', 'r+') as fh:
                    for line in fh:
                        tmp.write(line)
                        if '<datasources>' in line:
                            tmp.write(text)
                tmp.close()
            if dbflag == 0:
                subprocess.check_output("mv /tmp/temp_standalone.xml " +app_server_path + "/standalone/configuration/standalone.xml", shell=True)
    print 'DB Configuration added!!! Please Restart the Server to make effect of the changes!!!!'
    return "ok"
#install()
