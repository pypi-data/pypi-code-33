#-*- coding: ISO-8859-15 -*-
# Metaphor-gm-Test

import os, sys, site
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
from setuptools.command.install import install as _install
from setuptools.extension import Extension

from distutils.dir_util import mkpath
from distutils.util import convert_path
from datetime import datetime

def get_option(args, option_name, short_option_name=""):
    res = False
    test = "--{0}".format(option_name)
    res = test in args
    if res:
        args.pop(args.index(test))
    else:
        if not short_option_name:
            short_option_name = option_name
        test = "-{0}".format(short_option_name)
        res = test in args
        if res:
            args.pop(args.index(test))
        else:
            for ind, val in enumerate(args):
                if val.startswith(test):
                    rac, res = val.split('=')
                    args.pop(ind)
                    break         
    return res

"action de preparation des distribution"
if len(sys.argv) == 1:
    distaction = True
else:
    distaction = sys.argv[1][:5] in ('sdist', 'bdist', 'build')

is_test = get_option(sys.argv, 'test')

localpath = os.path.dirname(__file__)
if localpath and localpath != os.getcwd():
    os.chdir(localpath)

modulename = "metaphor"
modulepath = os.path.join(localpath, modulename)

entry_points = {'console_scripts': ['chem_gm_test=metaphor.test_chem_gm.main:run']}
projectname = "metaphor-gm-test"
 
languageLevel = int(sys.version_info[0])
 
main_ns = {}
ver_path = os.path.join(modulepath, "version_gm_test.py")
ver_path = convert_path(ver_path)
try:
    with open(ver_path, encoding="ISO-8859-15") as ver_file:
        exec(ver_file.read(), main_ns)
except:
    with open(ver_path) as ver_file:
        exec(ver_file.read(), main_ns)
module_version = main_ns['__version__']

homedir = os.path.expanduser(chr(126))
dodebug = 1
saveinstallinfo = 1
debugfilemain = os.path.join(homedir, "install{0}-{1}.txt".format(modulename, module_version))
debugfilevirtual = os.path.join(homedir, "installvirtual{0}-{1}.txt".format(modulename, module_version))

def copyfileEx(src, dest, deleteolddest=False, outfile=None):
    import shutil
    if os.path.exists(src):
        shutil.copyfile(src, dest)
        if outfile:
            outfile.write("copying {0} to {1}\n".format(src, dest))
    elif deleteolddest and os.path.exists(dest):
        os.remove(dest)
        if outfile:
            outfile.write("erasing {0}\n".format(dest))
        
def removefileEx(target, outfile=None):
    if os.path.exists(target):
        os.remove(target)
        if outfile:
            outfile.write("erasing {0}\n".format(target))
    
def beforeRun():
    try:
        with open("README.md", 'r') as ff:
            long_Description = ff.read()
    except:
        long_Description = ""
    return long_Description

def afterRun(projectname):# 
    with open('tempfile.txt', 'w') as ff:
        ff.write(main_ns['distname'](projectname))

class install(_install):
    debug = dodebug
    user_options = _install.user_options + [
        ('debug', None, 'use debug file') ,
        ('test', 't', 'run test after install')]

    def initialize_options(self):
        self.debug = 0
        self.test = 0
        _install.initialize_options(self)

    def finalize_options(self):
        _install.finalize_options(self)

    def isVirtual(self):
        """detect if python run in a virtual environment.
        """
        from sysconfig import get_config_var
        prefix = get_config_var('prefix')
        platbase = get_config_var('platbase')
        res = (prefix != platbase) or not hasattr(site, 'getuserbase') 
        if not res:
            try:
                prefix.index('envs')  
                res = True
            except: pass
        return res

    def get_install_path(self):
        test = self.get_outputs()[0]
        loc = ""
        while loc != modulename and test:
            test, loc = os.path.split(test)
        return test

    def doAfterInstallTest(self):
        temp = __import__(modulename)
        #import ins talldev
        #try:
#             try:
#                 import importlib
#             except ImportError:
#                 import imp as importlib
#             
#             temp = importlib.reload(temp)
#             except ImportError:
#                 temp = reload(temp)
        print(temp.__file__)
        #from temp.test import runtest
        try:
            temp.test.runtest()
        except: 
            print("No test in {0}".format(temp))
    
    def afterRunInstall(self, installaction, message, outfile, virtual, userTarget):
        if outfile:
            outfile.write(message)
            outfile.write("virtual = %s\n"%virtual)
            if userTarget:
                outfile.write("--user option ON\n")
        installpath = self.get_install_path()
        sys.path.insert(0, installpath)
        if dodebug:
            print("{0} path : {1}".format(modulename, installpath))
#         os.remove(cythonfile)
        if self.test:
            self.doAfterInstallTest()
        if outfile:
            outfile.close()
 
    def beforeRunInstall(self, installaction, message):
        if installaction:
            virtual = self.isVirtual()
            if virtual and "--user" in sys.argv:
                sys.argv.pop(sys.argv.index("--user"))
            userTarget = "--user" in sys.argv 
            if saveinstallinfo:
                outfile = open(debugfilevirtual if virtual else debugfilemain, "w")
            else:
                outfile = None
            if outfile:
                outfile.write(datetime.now().strftime("%d/%m/%Y %H:%M:%S\n"))
                outfile.write(message)
            return outfile, virtual, userTarget
        return None, 0, 0

    def run(self):
        pre_install_message = "start original {0} install\n".format(modulename)
        outfile, virtual, userTarget = self.beforeRunInstall(installaction, pre_install_message)                
        res = _install.run(self) 
        post_install_message = "original {0} install done\n".format(modulename)
        self.afterRunInstall(installaction, post_install_message, outfile, virtual, userTarget)
        return res

def runsetup(projectname, long_Description):

    licence = """Apache License Version 2.0, January 2004
    http://www.apache.org/licenses/
    """
 #    cythonClistExt = ["{0}.c".format(val) for val in cythonlist]

 #    extension_params = [(valname, val) for (valname, val) in zip(cythonModlist, cythonClistExt)]
#     sys.stdout.write("\n")    
#     for valname, val in extension_params:
#         sys.stdout.write("\t{0}\t\t{1}\n".format(valname, val))
#     sys.stdout.write("\n")
 #    extmodules = [Extension(valname, [val]) for valname, val in extension_params]
    dodebug = 0 

    installdev_url = "https://pypi.python.org/pypi/{0}".format(modulename)
    packages = find_packages()

    installrequires = ('metaphor',)

    classifiers = [ "Development Status :: 4 - Beta",
                    "Environment :: MacOS X",
                    "Intended Audience :: Science/Research",
                    "License :: OSI Approved :: Apache Software License",
                    "Operating System :: MacOS :: MacOS X",
                    "Programming Language :: Python :: 2.7",
                    "Topic :: Scientific/Engineering :: Artificial Intelligence",
                    ]

    setup(name=projectname,
          version=module_version,
          description="Neural network toolbox",
          long_description=long_Description,
          long_description_content_type="text/markdown",
          author="Jean-Luc PLOIX",
          author_email="jeanluc.ploix@gmail.com",
          url="http://www.netral.fr",
          download_url=installdev_url, 
          platforms = ('Windows', 'Linux', 'Mac OS X'),
          license = licence,
          zip_safe=False,
          entry_points=entry_points,
          include_package_data=True,

          packages = packages,
          install_requires = installrequires,
          classifiers = classifiers,
          cmdclass={'install': install}, 
#           ext_modules = extmodules,
#           package_data = {'metaphor': ['monal/include/*.h']},
#           include_package_data=True,
#           data_files = [('', ['metaphor/monal/include/ntdefines.h', 
#                             'metaphor/monal/include/mathplus.h', 
#                             'metaphor/monal/include/nttoolbox.h', 
#                             'metaphor/monal/include/nttype.h', 
#                             'metaphor/monal/include/train.h']),]
          )

if __name__ == "__main__":

    if len(sys.argv) == 1:
        sys.argv.append("sdist")
    try:
        if "SETUPPATH" in os.environ:
            pth = os.environ["SETUPPATH"]
            if not os.path.exists(pth):
                mkpath(pth)
            os.chdir(pth)
            
    except: 
        pass

    installaction = 'install' in sys.argv or 'develop' in sys.argv
    long_Description = ""
    print("run beforeRun")
    long_Description = beforeRun()
    print("beforeRun done")
    if is_test:
        for val, pth in zip(cythonlist, cythonpathlist):
            print("{0}\t\t{1}".format(val, pth) )            
    else:
        runsetup(projectname, long_Description) 

    if distaction:
        print("run afterRun")
        afterRun(projectname)
        print("afterRun done")
        print("setup done")