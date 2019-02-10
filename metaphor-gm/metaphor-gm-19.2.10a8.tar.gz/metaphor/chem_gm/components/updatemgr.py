#-*- coding: ISO-8859-15 -*-
# $Id: updatemgr.py 4303 2016-11-11 09:57:44Z jeanluc $
#
# Copyright 2016 Jean-Luc PLOIX
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
'''
Created on 3 juil. 2014

@author: jeanluc
'''

from future.standard_library import install_aliases
install_aliases()

import urllib
#import urllib2
from urllib.request import urlopen
from urllib.error import HTTPError
#from threading import Thread
#import thread
import sys, os
import shutil
import subprocess
from subprocess import PIPE
import tempfile
#from monal.util.toolbox import tempFileName, make_dir
from ...monal.util.utils import is_mac
from ...monal.util.toolbox import isiterable

def restart_program(params=[]):
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function.
    params is a list of parameters for calling the program"""
    python = sys.executable
    lst = sys.argv + params
    os.execl(python, python, * lst)

# def getPipUpdates(packageName="", withequal=False):
#     try:
#         import xmlrpclib as xmlrpc
#     except:
#         import xmlrpc
#     import pip
#     
#     pypi = xmlrpc.client.ServerProxy('https://pypi.python.org/pypi')
#     if not packageName:
#         iterlist = pip.get_installed_distributions()
#     elif isinstance(packageName, str):
#         iterlist = [val for val in pip.get_installed_distributions() if val.project_name == packageName]
#     elif isiterable(packageName):
#         lst = []
#         for val in pip.get_installed_distributions():
#             cond = False
#             for test in packageName:
#                 cond = val.project_name == test
#                 if cond:
#                     break
#             if cond: lst.append(val)
#         iterlist = lst
#     else:
#         iterlist = []
#     res = []
#     
#     try:
#         for dist in iterlist:
#             available = pypi.package_releases(dist.project_name)
#             if not available:
#                 # Try to capitalize pkg name
#                 available = pypi.package_releases(dist.project_name.capitalize())
#                 
#             if available:
#                 if withequal:
#                    cond = available[0] >= dist.version
#                 else:
#                    cond = available[0] > dist.version
#                 if cond:
#                     res.append((dist.project_name, available[0], dist.location))
#     except:
#         pass
#     return res
# 
# # def updateurls(urls, writer=sys.stdout, prefix="", option=""):
# #     curdir = os.getcwd()
# #     locdir = tempfile.mkdtemp(prefix="update")
# #     os.chdir(locdir)
# #     try:
# #         lst = []
# #         dirlst = []
# #         for val in urls:
# #             if isinstance(val, tuple):
# #                 val = "/".join(val) + ".tar.gz"
# #             valname = os.path.basename(val)
# #             lst.append("updating with %s"% val)
# #             f, _ = urllib.urlretrieve(val, filename=valname)
# #             untar(f)
# #             dirloc = valname[:-len(".tar.gz")]
# #             dirlst.append(dirloc)
# #             r unsetup(dirloc, prefix=prefix, option=option)
# #         lst .append("")
# #         if writer:
# #             writer.write('\n'.join(lst))
# #     finally:
# #         os.chdir(curdir)
# #         shutil.rmtree(locdir, ignore_errors=True)
# #         # attention a ignore_errors.
# #     
# # def updateurls__(urls, writer=sys.stdout, prefix="", option="", passwd=""):  # with pip
# #     curdir = os.getcwd()
# #     #locdir = tempfile.mkdtemp(prefix="update")
# #     #os.chdir(locdir)
# #     try:
# #         lst = []
# #         dirlst = []
# #         for val in urls:
# #             url, targetmodule = val
# #             #if isinstance(val, tuple):
# #             #    val = "/".join(val) + ".tar.gz"
# #             valname = os.path.basename(url)
# #             lst.append("updating with %s"% url)
# #             #modulepath = os.path.dirname(val[1].__file__)
# #             modulepath = "Users/jeanluc/Desktop/graphmachine"
# #             optionloc = '--target %s %s' %(modulepath, option)
# #             runpipinstall(url, prefix=prefix, option=optionloc, passwd=passwd)
# #         lst .append("")
# #         if writer:
# #             writer.write('\n'.join(lst))
# #     finally:
# #         pass
# #         #os.chdir(curdir)
# #         #shutil.rmtree(locdir, ignore_errors=True)
# #         # attention a ignore_errors.
    
def updateurls_(urls, writer=sys.stdout, option="", passwd=""):  # with steup
#     curdir = os.getcwd()
    lst = []
    for url, targetmodule in urls:
        installdir = os.path.dirname(targetmodule.__path__[0])  
        #installdir = "/Users/jeanluc/Desktop/TestInstall"
        out, err = updatefromurl(url, installdir, option=option, passwd=passwd)
        if out:
            lst.append(out)
        if err:
            lst.append("%s for %s"%(err, url))
        else:
            lst.append("updating with %s"% url)
        lst.append("")
        if writer:
            writer.write('\n'.join(lst))
        # attention a ignore_errors.
    
# def runPipInstall(modules, prefix="", root="", options=[], passwd="", writer=None):
#     import pip
#     local = os.getcwd()
#     os.chdir("/")
#     try:
#         if writer is None:
#             writerout = sys.stdout
#             writererr = sys.stderr
#         else:
#             writerout = writer
#             writererr = writer
#         pip_args = ['--no-cache-dir']  #'-vvv' 
#         try:
#             proxy = os.environ['http_proxy']
#         except KeyError:
#             proxy = ""
#         if proxy:
#             pip_args.append('--proxy')
#             pip_args.append(proxy)
#         pip_args.append('install')
#         if prefix:
#             if prefix.startswith('/'):
#                 prefix = prefix[1:]
#             pip_args.append('--prefix')
#             pip_args.append(prefix)
#         if root:
#             if root.startswith('/'):
#                 root = root[1:]
#             pip_args.append('--root')
#             pip_args.append(root)
#         for opt in options:
#             pip_args.append(opt)
#         for req in modules:
#             pip_args.append(req)
#         res = pip.main( pip_args)
#     finally:
#         os.chdir(local)
#     return res
# 
# 
# # def runpipinstall(url, writer=None, prefix="", option="", passwd=""):
# #     if writer is None:
# #         writerout = sys.stdout
# #         writererr = sys.stderr
# #     else:
# #         writerout = writer
# #         writererr = writer
# #     cmdline = ("%s pip install %s %s"% (prefix, option, url)).strip()
# #     obj = subprocess.Popen(cmdline, shell=True, stdin=PIPE, stdout=PIPE, 
# #         stderr=PIPE)
# #     if passwd:
# #         out, err = obj.communicate(passwd)   #+ '\n'
# #     else:
# #         out, err = obj.communicate()   
# #     writerout.write(out) 
# #     writererr.write(err)
# 
# def updatepypi(packages, writer=None, prefix="", root="", options=[], passwd=""):  # with pypi
#     packnames = [packname for packname, _ in packages]
#     #for packname, _ in packages:  #version
#     runPipInstall(packnames, writer=writer, prefix=prefix, root=root, options=options) #, passwd=passwd)
                 
def updatefromurl(url, installdir="", option="", passwd=""):
    try:
        locdir = tempfile.mkdtemp(prefix="update")
        modname = os.path.basename(url)
        valname = os.path.join(locdir, modname)
        curdir = os.getcwd()
        f, _ = urllib.urlretrieve(url, filename=valname)
        setupdir = untar(f, dest=installdir)
        os.chdir(setupdir)
#         if not "PYTHONPATH" in os.environ.keys():
#             os.environ["PYTHONPATH"] = setupdir
#         else:
#             os.environ["PYTHONPATH"] = "%s:%s"% (installdir, os.environ["PYTHONPATH"]) 
#         option = '%s --install-lib="%s"'%(option, installdir)
        out, err = runsetup(installdir, setupdir, option, passwd)
    finally:
        os.chdir(curdir)
        shutil.rmtree(locdir, ignore_errors=True)
        #shutil.rmtree(setupdir, ignore_errors=True)
    return out, err

def getrecentproducts(urlbase, appli, version, ext=".tar.gz", withcur=False):
    def getInventory(basenameonly=True, ext=".tar.gz"):
        url = os.path.join(urlbase, "inventory.txt")
        #"%s/inventory" %(urlbase)
        try:
            conn = urlopen(url)
            result = conn.read().split("\n")
        except HTTPError:
            result = []
        result = [val.strip() for val in result if val]
        if basenameonly:
            result = [os.path.basename(val) for val in result]
        if ext:
            result = [val for val in result if val.endswith(ext)]
        return result
        
    def fullversion(lst, car):
        res = [str(val) for val in lst]
        if car in ['a', 'b']:
            last = car.join(res[-2:])
            res.pop()
            res[-1] = last
        return ".".join(res)
    def levellst(targetlst, verlstint, basever, car):
        res = []
        empty = 0
        OK = True
        while OK:
            verlstint[-1] = basever
            curversion = fullversion(verlstint, car)
            shortprod = "%s-%s" %(appli, curversion)
            prod = "%s%s" %(shortprod, ext)
            #url = "%s/%s" %(urlbase, prod)
            basever += 1
            if prod in targetlst:
                res.append(shortprod)
                empty = 0
            else:
                curversion = fullversion(verlstint, "")
                shortprod = "%s-%s" %(appli, curversion)
                prod = "%s%s" %(shortprod, ext)
                if prod in targetlst:
                    res.append(shortprod)
                    empty = 0              
                else:
                    empty += 1
                    OK = empty < 10
                
#             try: 
#                 conn = urllib2.urlopen(url)
#                 conn.close()
#                 res.append(shortprod)
#                 empty = 0
#             except IOError:
#                 empty += 1
#                 OK = empty < 10
        return res   
    
    lst = getInventory()
    res = []
    car = 'a'
    verlst = version.split(car)
    if len(verlst) == 1:
        car = '.'
        verlst = version.split(car)
        if len(verlst) < 2:
            raise Exception("bad version string")
    elif len(verlst) == 2:
        headlst = verlst[0].split('.')
        headlst.append(verlst[-1])
        verlst = headlst
    verlstint = [int(val) for val in verlst] 
    basever = verlstint[-1]
    upbasever = verlstint[-2]
    if not withcur:
        basever += 1
    res = levellst(lst, verlstint, basever, car)
    OKup = True
    test = 0
    while OKup:
        test += 1
        upbasever += 1
        verlstint[-2] = upbasever
        resloc = levellst(lst, verlstint, 0, car)
        OKup = len(resloc) or (test <= 5)
        res.extend(resloc)
    
    return res

def untar(fname, dest="", verbose=0):
    import tarfile
    destname = ""
    if (fname.endswith("tar.gz")):
        destname = os.path.basename(fname)
        destname = destname[:-len(".tar.gz")]
        if dest:
            basedir = dest 
            destname = os.path.join(dest, destname)
        else:
            basedir = os.path.dirname(fname)
        tar = tarfile.open(fname)
        tar.extractall(basedir)
        tar.close()
        if verbose:
            print("Extracted in Current Directory")
    elif verbose:
        print("Not a tar.gz file: '%s '" % fname)
    return destname
            
def runsetup(installdir="", setupdir="", option="", passwd=""):
    if setupdir:
        setuopy = os.path.join(setupdir, "setup.py")
    else:
        setuopy = "setup.py"
    if not is_mac():
        prefix = ""
    elif passwd:
        prefix = "echo %s | sudo -S"% passwd
    else:    
        prefix = "sudo"
    out = err =""
    if installdir:
        cmdline = ('%s PYTHONPATH="%s" python %s install --install-lib="%s" %s'% (prefix, installdir, setuopy, installdir, option)).strip()
    else:
        cmdline = ("%s python setup.py install %s"% (prefix, option)).strip()
    print("cmdline =",  cmdline)
    obj = subprocess.Popen(cmdline, stdin=PIPE, stdout=PIPE, stderr=PIPE, 
                           shell=True)
    if 0: #passwd:
        out, err = obj.communicate(passwd + '\n' )  #
    else:
        out, err = obj.communicate()
    return out, err
    
#===============================================================================
# class updateThread(Thread):
#     def __init__(self, url, writer, group=None, target=None, name=None, args=(), kwargs={}):
#         Thread.__init__(self, group, target, name, args, kwargs)
#         self.urls = urls
#         self.writer = writer
#         
#     def run(self):
#         curdir = os.getcwd()
#         locdir = tempFileName(prefix="update")
#         os.mkdir(locdir)
#         os.chdir(locdir)
#         lst = []
#         dirlst = []
#         for val in self.urls:
#             valname = os.path.basename(val)
#             lst.append("updating with %s"% val)
#             f, m = urllib.urlretrieve(val, filename=valname)
#             untar(f)
#             dirloc = valname[:-len(".tar.gz")]
#             dirlst.append(dirloc)
#             r unsetup(dirloc)
#         lst .append("")
#         if self.writer:
#             self.writer.write('\n'.join(lst))
#         os.chdir(curdir)
#===============================================================================

#==============================================================================
if __name__ == "__main__":
    
    #runpipinstall("DummyPdf", writer=None, prefix="sudo", option="--user", passwd="Larten3556")
    #runpipinstall("DummyPdf", writer=None, option="--user")
    runPipInstall(["DummyPdf"], prefix="", options = ["--upgrade", "--user"])
    
#     url = "http://download.netral.fr/products/grapgmachine/graphmachine-2.1.0.51.tar.gz"
#     installdir = "/Users/jeanluc/Desktop/TestInstall"
#     option = ""
#     passwd = "Larten3556"
#     
#     out, err = updatefromurl(url, installdir=installdir, option=option, passwd=passwd)
#     print err
#     print out
#     #import monal, graphmachine
#     lstt = []
#     urlbase = "http://download.netral.fr/products/monalpy"
#     appli = "monal"
#     curversion = "3.3.0a7"
#     #curversion = monal.__version__
#     ext = ".tar.gz"
#     lst = getrecentproducts(urlbase, appli, curversion, ext)
#     #if len(lst): 
#         #lstt.append("%s/%s%s"%(urlbase, lst[-1], ext))
#     urlbase = "http://download.netral.fr/products/graphmachine"
#     appli = "graphmachine"
#     curversion = "1.3.0a7"
#     #curversion = graphmachine.__version__
#     lst = getrecentproducts(urlbase, appli, curversion, ext)
#     #for val in lst: 
#     if len(lst):
#         lstt.append("%s/%s%s"%(urlbase, lst[-1], ext))
# #        print val
#     #for val in lstt:
#     updateurls(lstt)
#         #print val
#     if not len(lstt):
#         print "nothing to upgrade"
#     else:
#         print "done"
    
    
    #===========================================================================
    # url = "http://download.netral.fr/products/graphmachine/graphmachine-1.3.0a8.tar.gz"
    # 
    # conn = urllib2.urlopen(url)
    # html = conn.read()
    # with open("res.html", "w") as f:
    #     f.write(html)
    # conn.close()
    #===========================================================================