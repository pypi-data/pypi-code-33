__all__ = ['os_sys', 'fail', 'modules', 'system', 'wifi']
import requests
import sys
import os




 
def update(argv=None):
    from subprocess import getstatusoutput
    getstatusoutput('pip install --upgrade os_sys')

def download_zip():
    url = 'https://jumpshare.com/'  
    r = requests.get('https://github.com/Matthijs990/os_sys/archive/master.zip')
    print('downloading:')

    with open('test.zip', 'wb') as f:  
        f.write(r.content)
    from time import sleep, time
    now = time()
    def chek(now, duur):
        a = now
        b = time()
        c = b - a
        return c <= duur
    while chek(now, 10):
        print('|', end='')
        sleep(0.1)
    print(end='\n')
    print('done!')


def init():
    values = dict(
    name="os_sys",
    version="0.4.9",
    author="Matthijs labots",
    
    author_email="libs.python@gmail.com",
    description="a big plus lib for more functions to use",
    long_description='long_descrioption',
    long_description_content_type="text/markdown",
    url="https://python-libs-com.webnode.nl/",
    python_requires='>=3',
    entry_points={'console_scripts': [
        'os_sys-updater = os_sys.commands:update',
        'download-setup_script = os_sys.commands:download_zip',
        
    ]},
    include_package_data=True,
    package_data='package_data',
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
    keys = list(values)
    index = 0
    s = open('setup_values.txt', 'w+')
    while index < len(keys):
        s.write(str(keys[index])+'='+str(values[keys[index]])+'\n')
        index += 1
    s.close()
    path = os.path.abspath('')
    
    print(path)
    path = path.split('\\')
    fil = int(len(path) - 1)
    h = 0
    mystr = ''
    
    
    
    del path[fil]
    print(path)
    while h < len(path):
        mystr = mystr + path[h]
        mystr = mystr + '\\'
        h += 1
    print(path)
    print(mystr)


    
    index = 0
    s = open(mystr+'data_files\settings.config', 'w+')
    while index < len(keys):
        s.write(str(keys[index])+'='+str(values[keys[index]])+'\n')
        index += 1
    s.close()
    
    del index
    del s
    del values
    del keys
import os
import sys
import functools
import distutils.core
import distutils.filelist
from distutils.util import convert_path
from fnmatch import fnmatchcase
def all_maps(d):
    lijst = [os.path.join(d, f) for f in os.listdir(d)]
    ret = []
    num = 0
    while num < len(lijst):
        if '.' in lijst[num]:
            pass
        else:
            ret.append(lijst[num])
        num += 1
    return ret
print(all_maps(os.path.abspath('')))
print(os.path.abspath(''))


    
