import setuptools
import setuptools as s
try:
    import ready
except Exception:
    pass
def execute_from_command_line(argv=None):
    """Run a ManagementUtility."""
    utility = ManagementUtility(argv)
    utility.execute()

package_data = dict()
long_description = 'if you try import os_sys and it not work you can try import\
pack that while work then i know the problem and i working on it\
but this is my solution for now thanks\n\n\n'
with open("README.md", "r") as fh:
    long_description.join(fh.read())
import sys
import os
version = sys.version_info[:2]
needing = (3, 3)
da = ''.join(str(version[0]) + '.' + str(version[1]))

data = dict(version=da,
             needing=3.3)
if version < needing:
    sys.stderr.write('\
==========================\n\
Unsupported Python version\n\
==========================\n\
This version of os_sys requires Python %(needing)s, but you\'re trying to\n\
install it on Python %(version)s\n\
\n\
this is may be becuse you are using a version of pip that doesn\'t\n\
understand the setup script. make shure you\n\
have pip >= 9.0 and setuptools >= 40.0.0, then try again:\n\
\n\
    python -m pip install --upgrade pip setuptools\n\
    python -m pip install os_sys\n\
\nthis will install the latest version of os_sys\n\n\n' % data)
    class PythonVersionError(Exception):
        '''not right python version'''
        pass
    raise PythonVersionError('you need at least python 3.3')
from distutils.sysconfig import get_python_lib as gpl

with open('data_types.txt') as dem:
    raw_data_types = dem.read()
data_types = raw_data_types.split('/')
p = data_types
overlay_warning = False
if "install" in sys.argv:
    lib_paths = [gpl()]
    if lib_paths[0].startswith("/usr/lib/"):
        # We have to try also with an explicit prefix of /usr/local in order to
        # catch Debian's custom user site-packages directory.
        lib_paths.append(get_python_lib(prefix="/usr/local"))
    for lib_path in lib_paths:
        existing_path = os.path.abspath(os.path.join(lib_path, "os_sys"))
        if os.path.exists(existing_path):
            # We note the need for the warning here, but present it after the
            # command is run, so it's more likely to be seen.
            overlay_warning = True
            break


def all_maps(d, plus=None):
    
    lijst = [os.path.join(d, f) for f in os.listdir(d)]
    ret = []
    num = 0
    while num < len(lijst):
        if '.' in lijst[num]:
            pass
        else:
            if plus == None:
                ret.append(lijst[num])
            else:
                ret.append(str(plus)+'|'+str(lijst[num]))
        num += 1
    return ret
lijst = list(all_maps(os.path.abspath('')) + all_maps(os.path.abspath('os_sys'), plus='os_sys.') + all_maps(os.path.abspath('pack'), plus='pack.'))
num = 0
while num < len(lijst):
    new = str(lijst[num]).split('\\')
    to = int(len(new) - 1)
    if '|' in lijst[num]:
        plus, none = str(lijst[num]).split('|')
    else:
        plus = ''
    package_data.setdefault(plus+new[to], []).extend(p)
    num += 1
lijst = all_maps(os.path.abspath('os_sys\commands'))
print(lijst)
num = 0
while num < len(lijst):
    new = str(lijst[num]).split('\\')
    to = int(len(new) - 1)
    package_data.setdefault('os_sys.'+'commands.'+new[to], []).extend(p) if not 'commands' in new[to] else package_data.setdefault('os_sys.'+'commands', []).extend(p)
    num += 1
print(package_data)
long_description = long_description.replace('evry', 'every')
setuptools.setup(
    name="os_sys",
    version="0.5.1",
    author="Matthijs labots",
    
    author_email="libs.python@gmail.com",
    description="a big plus lib for more functions to use",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://python-libs-com.webnode.nl/",
    python_requires='>=3',
    entry_points={'console_scripts': [
        'os_sys-updater = os_sys.commands:update',
        'download-setup_script = os_sys.commands:download_zip',
        'if_not_work-write_new_scripts = os_sys.commands:init',
        
    ]},
    include_package_data=True,
    package_data=package_data,
    packages=['os_sys', 'os_sys.test', 'os_sys.programs', 'os_sys.data_files',
              'os_sys.commands', 'os_sys.commands.programs', 'os_sys.commands.data_files',
              'os_sys.commands.test',
              'pack', 'pack.test', 'pack.programs', 'pack.data_files',],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    project_urls={
        'all files': 'https://github.com/Matthijs990/os_sys',
        'Downloads': 'https://python-libs-com.webnode.nl/downloads/',
        'become a member': 'https://python-libs-com.webnode.nl/user-registration/',
        'download all files': 'https://github.com/Matthijs990/os_sys.git',
        'want to help': 'https://github.com/Matthijs990/os_sys/tree/master/do%20you%20want%20to%20help',
        'startpage': 'https://pypi.org/project/os-sys/',
        'made possible by': 'https://pypi.org',
    },
)

print('you need to typ:\n\
    from os_sys import os_sys or:\n\
    from os_sys import fail or:\n\
    from os_sys import system or:\n\
    from os_sys import modules or:\n\
    from os_sys import wifi or:\n\
    from os_sys import *')
if overlay_warning:
    sys.stderr.write('Warning: os_sys is al ready on your pc')
