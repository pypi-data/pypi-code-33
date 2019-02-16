#!/usr/bin/python2.7

import sys
import os
import subprocess

class GynxRunner(object):

    def __init__(self, *args, **kwargs):
        options = sys.argv[1:]
        self.options = options
        self._help = 'help' in options
        self._verbose = 'verbose' in options
        self._clean = 'clean' in options
        self._refresh = 'refresh' in options
        self._auth = 'auth' in options
        self._dry = 'dry' in options
        self.create_cache()

    @property
    def appdir(self):
        """
        Attempt to import gynx project to locate and return the environment path.
        If the project can't be imported, a development environment is assumed
        and the directory at ../gynx/ from the script location is returned.
        """
        try:
            import gynx
            appdir = gynx.__path__[0]
        except ImportError:
            appdir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                'gynx'
            )
        if os.path.isdir(appdir):
            return appdir
        else:
            print "%s is not a valid directory" % appdir
            sys.exit()

    def create_cache(self):
        """
        Create CACHE folder inside the app directory for storing JSON state.
        """
        appdir = self.appdir
        if not os.path.isdir(os.path.join(appdir, 'CACHE')):
            os.mkdir(os.path.join(appdir, 'CACHE'))

    def execute(self, commands):
        """
        Execute a list of shell commands using subprocess.call
        """
        for command in commands:
            subprocess.call(command, shell=True)

    def help(self):
        return """
NAME

    gynx

DESCRIPTION

    Google Drive sync for Linux

USAGE

    gynx  [-V|--version] [-h|--help] [-v|--verbose] [-c|--clean] [-r|--refresh]
          [-a|--auth] [-d|--dry-run]

OPTIONS

    -V --version      Print gynx version
    -h --help         Print this help text
    -v --verbose      Verbose output
    -c --clean        Clear file cache before run
    -r --refresh      Delete local drive before run
    -a --auth         Renew authentication token
    -d --dry-run      Print operations without execution
"""

    def clean(self):
        """
        Remove JSON files in CACHE folder if they exist
        """
        if os.path.exists(os.path.join(self.appdir, 'CACHE', 'remote.json')):
            print "Clearing remote cache..."
            os.remove(os.path.join(self.appdir, 'CACHE', 'remote.json'))
        if os.path.exists(os.path.join(self.appdir, 'CACHE', 'local.json')):
            print "Clearing local cache..."
            os.remove(os.path.join(self.appdir, 'CACHE', 'local.json'))

    def refresh(self):
        """
        Delete the contents of the local directory after user confirmation.
        Clean files in CACHE first if -c|--clean flag not also specified.
        """
        confirm = raw_input("This will delete the contents of your current directory. \nAre you sure you want to continue? (y/n): ")
        if confirm.upper() == 'Y':
            if not self._clean:
                self.clean()
            print "Deleting local directory contents..."
            self.execute(['rm -rv %s/*' % os.getcwd()])

    def authorize(self):
        """
        Delete token.json and allow the user to re-authorize
        """
        if os.path.exists(os.path.join(self.appdir, 'credentials', 'token.json')):
            print "Clearing authenticaton token..."
            os.remove(os.path.join(self.appdir, 'credentials', 'token.json'))

    def start(self, arguments):
        """
        Run app.py with parsed arguments
        """
        if os.path.exists(os.path.join(self.appdir, 'app.py')):
            app = os.path.join(self.appdir, 'app.py')
            command = 'python "%s" %s' % (app, arguments)
            self.execute([command])

    def run(self):
        """
        Run functions based on arguments and pass remaining arguments to app.py
        """
        arguments = ""
        if self._help:
            print self.help()
            sys.exit()
        if self._verbose:
            arguments += "verbose "
        if self._clean:
            self.clean()
        if self._refresh:
            self.refresh()
        if self._auth:
            self.authorize()
        if self._dry:
            arguments += "dry"
        self.start(arguments)

runner = GynxRunner()
runner.run()
