import boto3
import re
import zipfile
from os import listdir, getcwd, sep
from os.path import isfile, join, basename
from io import BytesIO

 
l = boto3.client('lambda')
workingDir = getcwd() + sep
workingDir = workingDir.replace('\\', '/')


class FunctionNameError(Exception):
    pass


class ProjectFolder(object):
    def __init__(self, project_dir):
        self.workingDir = project_dir
        self.dirs = []
        self.ignore = []
        self.files = []
        self._import_ignore()

    def _import_ignore(self):
        with open(self.workingDir + '.lambdevignore.txt') as f:
            self.ignore = [line.rstrip('\n').rstrip('\r') for line in f]
            print('- Ignoring: {}'.format(self.ignore))

    # Sort out files and dirs in a root directory
    def _sort(self):
        names = listdir(self.workingDir)
        #  print(names)
        for name in names:
            if name[0] == '.' or name in self.ignore or name[-3:] == 'pyc':
                pass
            else:
                if isfile(self.workingDir + name):
                    self.files.append(join(sep, self.workingDir, name))
                    #  print(self.workingDir + name)
                else:
                    self.dirs.append(self.workingDir + name + sep)
        #  print(self.dirs)
        #  print(self.files)

    # loop until all recursive files are added to files list
    def _get_recursive(self):
        while len(self.dirs) > 0:
            self.workingDir = self.dirs.pop()
            # print('workingDir = %s' % workingDir)
            self._sort()

    def _zipit(self):
        global workingDir
        buf = BytesIO()
        p = re.compile(r'/{}/'.format(workingDir.split('/')[-2]))
        with zipfile.ZipFile(buf, 'w') as ziph:
            for f in self.files:
                ziph.write(f, f[p.search(f).end():])
        buf.seek(0)
        return buf.read()

    def build_zip(self):
        print("- Building...")
        self._sort()
        self._get_recursive()
        return self._zipit()


def get_function_name():
    try:
        with open(workingDir + 'function_name.txt') as f:
            return [line.rstrip('\n').rstrip('\r') for line in f][0]
    except FileNotFoundError:
        raise(FunctionNameError('No function_name.txt. Does the lambda function exist?'))


def _upload_file(z):
    print('- Uploading...')
    l.update_function_code(
        FunctionName=get_function_name(),
        ZipFile=z
    )


# build and upload deployment package
def upload_package():
    x = ProjectFolder(workingDir)
    _upload_file(x.build_zip())


def alias_exists(alias_response, desired):
    for alias in alias_response['Aliases']:
        if alias['Name'] == desired:
            return True
    return False
