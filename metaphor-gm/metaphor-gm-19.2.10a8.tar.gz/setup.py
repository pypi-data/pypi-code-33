#-*- coding: ISO-8859-15 -*-
# Metaphor-gm

import os, sys, site
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
from setuptools.command.install import install as _install
from setuptools.extension import Extension

from distutils.dir_util import mkpath
from distutils.util import convert_path
from datetime import datetime

# sys.stderr.write("cmdline : " + " ".join(sys.argv) + "\n")
# sys.stdout.write("cmdline : " + " ".join(sys.argv) + "\n")

def get_option(args, option_name, short_option_name=""):
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

is_test = get_option(sys.argv, 'test')
no_cython = get_option(sys.argv, 'no-cython')
keep_C = get_option(sys.argv, 'keep-c')
no_rename_py = get_option(sys.argv, 'no-rename-py')

localpath = os.path.dirname(__file__)
if localpath and localpath != os.getcwd():
    os.chdir(localpath)

#installpath = self.get_install_path()

modulename = "metaphor"
modulepath = os.path.join(localpath, modulename)
main_ns = {}
ver_path = os.path.join(modulepath, "version_gm.py")
ver_path = convert_path(ver_path)
try:
    with open(ver_path, encoding="ISO-8859-15") as ver_file:
        exec(ver_file.read(), main_ns)
except:
    with open(ver_path) as ver_file:
        exec(ver_file.read(), main_ns)
module_version = main_ns['__version__']

entry_points = {}
projectname = "metaphor-gm"
installrequires = ('metaphor')
cythonfile = os.path.join(modulename, 'cythonlist.txt')

languageLevel = int(sys.version_info[0])
    
homedir = os.path.expanduser(chr(126))
dodebug = 1
debugfilemain = os.path.join(homedir, "install{0}-{1}.txt".format(modulename, module_version))
debugfilevirtual = os.path.join(homedir, "installvirtual{0}-{1}.txt".format(modulename, module_version))
       
def beforeRun(cythonlist):
    from Cython.Build import cythonize
    print("local path : {0}".format(localpath))
    cythonizelist = []
    renamelist = []
    for basefile in cythonlist:
        fullfile = os.path.join(localpath, basefile)
        pydfile = "{0}.pyd".format(fullfile)   
        pyxfile = "{0}.pyx".format(fullfile)
        pyfile = "{0}.py".format(fullfile)
        crfile = "{0}._py".format(fullfile)
        shortpyfile = "{0}.py".format(basefile)
        shortpyxfile = "{0}.pyx".format(basefile)
        shortcrfile = "{0}._py".format(basefile)

        if os.path.exists(pyxfile):
            if os.path.exists(pyfile):
                os.rename(pyfile, crfile)
                sys.stdout.write("renaming {0} to {1}\n".format(shortpyfile, shortcrfile))
            cythonizelist.append(pyxfile)
        elif os.path.exists(pyfile):
            renamelist.append((pyfile, crfile, shortpyfile, shortcrfile))
            cythonizelist.append(pyfile)
        elif os.path.exists(crfile) and not os.path.exists(pydfile):
            os.rename(crfile, pyfile)
            sys.stdout.write("renaming {0} to {1}\n".format(shortcrfile, shortpyfile))
            renamelist.append((pyfile, crfile, shortpyfile, shortcrfile))
            cythonizelist.append(pyxfile)
    cythonize(cythonizelist, compiler_directives={'language_level' : languageLevel})
    ll = len(renamelist)
    for ind, (pyfile, crfile, shortpyfile, shortcrfile) in enumerate(renamelist):
        os.rename(pyfile, crfile)
        sys.stdout.write("[{2}/{3}] renaming {0} to {1}\n".format(
            shortpyfile, shortcrfile, ind+1, ll))
    return #cythonlist, cythonpathlist, long_Description

def afterRun(projectname, cythonlist, cythonpathlist):# 
    if not keep_C:
        for basefile in  cythonlist:
            fullfile = os.path.join(localpath, basefile)
            Cfile = "{0}.c".format(fullfile)
            shortCfile = "{0}.c".format(basefile)
            pyxfile = "{0}.pyx".format(fullfile)
            pyfile = "{0}.py".format(fullfile)
            crfile = "{0}._py".format(fullfile)
            shortpyfile = "{0}.py".format(basefile)
            shortcrfile = "{0}._py".format(basefile)
            if not no_rename_py and os.path.exists(crfile) and not os.path.exists(pyfile):
                os.rename(crfile, pyfile)
                sys.stdout.write("renaming {0} to {1}\n".format(shortcrfile, shortpyfile))
            if not no_rename_py and os.path.exists(crfile) and not os.path.exists(pyfile):
                os.rename(crfile, pyfile)
                sys.stdout.write("renaming {0} to {1}\n".format(shortcrfile, shortpyfile))
            if not 'bdist_wheel' in sys.argv and os.path.exists(Cfile):
                os.remove(Cfile)
                sys.stdout.write("deleting {0}\n".format(shortCfile))
    with open('tempfile.txt', 'w') as ff:
        ff.write(main_ns['distname'](projectname))

def getcythonlist(no_cython):
    if no_cython:
        return [], []
    cythonlist = []
    cythonpathlist = []
    cythonlistfilename = os.path.join(modulepath, cythonfile)
    if no_cython:
        cythonlist = []
    if not os.path.exists(cythonlistfilename):
        cythonlistfilename = cythonfile
    if os.path.exists(cythonlistfilename):
        with open(cythonlistfilename) as ff:
            cythonlist = [val.strip() for val in ff]
        cythonlist = [val for val in cythonlist if val and not val.startswith("#")]
    for cythonitem in cythonlist:
        lst = []
        folder, base = os.path.split(cythonitem)
        while folder:
            lst.insert(0, base)
            folder, base = os.path.split(folder)
        lst.insert(0, base)
        cythonpathlist.append(".".join(lst))
    return cythonlist, cythonpathlist

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
        print(temp.__file__)
        try:
            temp.test.runtest()
        except: 
            print("No test in {0}".format(temp))
    
    def afterRunInstall(self, message, logfile):
        
        def fullCythonList(localpath=""):
            if not localpath:
                return cythonlist
            if not os.path.exists(localpath):
                return []
            lst = [os.path.join(localpath, val) for val in cythonlist] 
            return lst
        
#         if logfile:
#             with open(logfile, "a") as ff:
        installpath = self.get_install_path()
        installedcythonlist = os.path.join(installpath, 'metaphor', 'cythonlist.txt')
        sys.path.insert(0, installpath)
       
        with open(logfile, "a") as ff:
            ff.write(message)
            ff.write('installpath = {0}\n'.format(installpath))
        if dodebug:
            print("{0} path : {1}".format(modulename, installpath))
        cleanlist = fullCythonList(installpath)
        for fil in cleanlist:
            ffil = '{0}{1}'.format(fil, ".c")
            if os.path.exists(ffil):
                os.remove(ffil)
                sys.stderr.write('removed {0}\n'.format(ffil))
            else:
                if dodebug:
                    print('cannot find {0}'.format(ffil))  
        os.remove(installedcythonlist)
        if self.test:
            self.doAfterInstallTest()
 
    def beforeRunInstall(self, message, logfile):
        
        if self.virtual and "--user" in sys.argv:
            sys.argv.pop(sys.argv.index("--user"))
        userTarget = "--user" in sys.argv 
        with open(logfile, "w") as ff:
            ff.write(datetime.now().strftime("%d/%m/%Y %H:%M:%S\n"))
            ff.write(message)
            ff.write("virtual = %s\n"%self.virtual)
            if userTarget:
                ff.write("--user option ON\n")

    def run(self):
        pre_install_message = "start original {0} install\n".format(modulename)
        post_install_message = "original {0} install done\n".format(modulename)
        self.virtual = self.isVirtual()
        logfile = debugfilevirtual if self.virtual else debugfilemain
        self.beforeRunInstall(pre_install_message, logfile)                
        res = _install.run(self) 
        self.afterRunInstall(post_install_message, logfile)
        return res

def runsetup(projectname, no_cython, cythonlist, cythonModlist):

    licence = """Apache License Version 2.0, January 2004
    http://www.apache.org/licenses/
    """
    cythonClistExt = ["{0}.c".format(val) for val in cythonlist]
    try:
        with open('README.md', 'r') as ff:
            long_Description = ff.read()
    except:
        long_Description = ""

    extension_params = [(valname, val) for (valname, val) in zip(cythonModlist, cythonClistExt)]
    extmodules = [Extension(valname, [val]) for valname, val in extension_params]
    dodebug = 0 

    installdev_url = "https://pypi.python.org/pypi/{0}".format(modulename)
    excludelist = []
    packages = find_packages()
    installrequires = ('metaphor', )
    classifiers = [ "Development Status :: 4 - Beta",
                    "Environment :: MacOS X",
                    "Intended Audience :: Science/Research",
                    "License :: OSI Approved :: Apache Software License",
                    "Operating System :: MacOS :: MacOS X",
                    "Programming Language :: Python :: 3.6",
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
          platforms = ['Windows', 'Linux', 'Mac OS X'],
          license = licence,
          zip_safe=False,
          entry_points=entry_points,
          packages = packages,
          include_package_data=True,
          install_requires = installrequires,
          classifiers = classifiers,
          cmdclass={'install': install}, 
          ext_modules = extmodules,
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

    #action d'installation
    installaction = 'install' in sys.argv or 'develop' in sys.argv
    #action de preparation des distribution"
    distaction = 0
    for arg in sys.argv[1:]:
        if arg[:5] in ('sdist', 'bdist', 'build'):
            distaction = 1
            break
        
    cythonlist, cythonpathlist = [], []
    if not no_cython:
        print("run beforeRun")
        cythonlist, cythonpathlist = getcythonlist(no_cython)
        if distaction:
            beforeRun(cythonlist)
        if installaction and not len(cythonlist):
            sys.stdout.write("Empty cython list\n")
        print("beforeRun done")
    if is_test:
        for val, pth in zip(cythonlist, cythonpathlist):
            print("{0}\t\t{1}".format(val, pth) )            
    else:
        runsetup(projectname, no_cython, cythonlist, cythonpathlist) 

    if distaction and not no_cython:
        print("run afterRun")
        afterRun(projectname, cythonlist, cythonpathlist)
        print("afterRun done")
    if distaction:
        print("setup done")