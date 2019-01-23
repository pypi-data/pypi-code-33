
import os
import subprocess
from argparse import ArgumentParser

LEVELS = ['major','minor','patch']

def update_version(level):
    if os.path.isfile('version'):
        with open('version') as versionfile:
            oldversion = versionfile.read().strip()
    elif os.path.exists('version'):
        raise(RuntimeError("Can't create file 'version'"))
    else:
        oldversion="0.0.0"
    major, minor, patch = [int(x) for x in oldversion.split('.')]
    if level == 'major':
        major += 1
        minor = 0
        patch = 0
    elif level == 'minor':
        minor += 1
        patch = 0
    else: patch += 1
    newversion = '%i.%i.%i' % (major, minor, patch)
    with open('version', 'w') as versionfile:
        versionfile.write(newversion)
    return newversion

def git(command):
    process = subprocess.run(['git'] + command.split(), stdout=subprocess.PIPE)
    if process.returncode != 0:
        raise(RuntimeError('Failure of git command: ' + command))
    return process.stdout.decode()

def do(level=None):
    status = git('status -s')
    if status:
        raise RuntimeError('Git working tree must be clean to release')
    version = update_version(level)
    print('Version updated to ' + version)
    print(git('add version'))
    print(git('commit -m v' + version))
    print(git('tag v' + version))
    print(git('push'))
    print(git('push --tags'))
    print('Release complete')

def run():
    parser = ArgumentParser()
    parser.add_argument('level', choices=LEVELS, default='patch', nargs='?')
    level = parser.parse_args().level
    do(level)

if __name__=='__main__':
    run()
