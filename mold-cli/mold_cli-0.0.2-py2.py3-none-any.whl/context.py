'''
a MoldContext parses and stores sys.argv and os.environ, it also has several constants and provieds
some convience methods. One context gets created in __main__ and is passed through the entire app.
'''


from mold.util import fs, query, system

_flags = set([
    'help', '-h', '--help',
    '--no-linking', '--force', 
    '--complete', '--color', 
    '--no-prompt', '--sign',
    ])

# STORES ARGS AND ENV VARS
class MoldContext:
    def __init__(self, sys_argv, os_environ):
        # parse and strip flags from argv
        mold_argv = [] # argv witout flags or path to file being executed
        flags = set([]) 
        for arg in sys_argv:
            if _flags.issuperset([arg]):
                flags.add(arg)
            else:
                mold_argv.append(arg)

        # PARGS ARGV AND COMPLETE ARGV
        self.sys_argv  = sys_argv
        # mold_argv is offset by one when the completion is set
        if flags.issuperset(['--complete']):
            self.mold_argv = mold_argv[1:]
        else: 
            self.mold_argv = mold_argv
        self.command = query(self.mold_argv, 1)
        self.task = query(self.mold_argv, 2)
        self.options = self.mold_argv[3:]
        self.flags = flags

        # PARSED ENVIRON AND CONSTANTS
        self.HOME = query(os_environ, 'HOME')
        self.EDITOR = query(os_environ, 'EDITOR') or system.which('vim') or system.which('nano')
        self.MOLD_ROOT = query(os_environ, 'MOLD_ROOT') or (HOME +'/.mold')
        self.MOLD_DOCS = __file__.replace('context.py', 'asset/docs')
        self.MOLD_DEBUG = bool(query(os_environ, 'MOLD_DEBUG'))
        self.MOLD_COLOR = system.check_is_tty() or bool(query(os_environ, 'MOLD_COLOR')) or self.check_flag_set('--color')
        self.MOLD_SIGN = bool(query(os_environ, 'MOLD_SIGN')) or self.check_flag_set('--sign')

        # colors 
        self.reset = '\033[39m' if self.MOLD_COLOR else ''
        self.red = '\033[31m' if self.MOLD_COLOR else ''
        self.blue = '\033[94m' if self.MOLD_COLOR else ''
        self.cyan = '\033[36m' if self.MOLD_COLOR else ''
        self.grey = '\033[38m' if self.MOLD_COLOR else ''
        self.green = '\033[32m' if self.MOLD_COLOR else ''
        self.yellow = '\033[33m' if self.MOLD_COLOR else ''
        self.magenta  = '\033[35m' if self.MOLD_COLOR else ''

        # EXIT CODES
        self.OK = 0
        self.FAIL = 1 
        self.IO_ERROR = 2
        self.MOLD_ROOT_ERROR = 3
        self.MOLD_ROOT_DIRS_ERROR = 4
        self.CRASH = 5 
        self.NEXT_COMMAND = 'NEXT_COMMAND'

    def check_has_options(self): 
        return len(self.options) != 0

    def get_option(self, index):
        return query(self.options, index)

    def check_flag_set(self, name):
        return self.flags.issuperset([name])

    def check_help_set(self):
        return self.check_flag_set('help') or self.check_flag_set('-h') or self.check_flag_set('--help')

    def check_color_mode_set(self):
        return self.MOLD_COLOR or self.check_flag_set('--color')

    def get_command_dir(self, command=None):
        command = command or self.command
        if not command:
            return None
        return self.MOLD_ROOT + '/' + command

    def get_command_dirlist(self, command=None):
        result = [] 
        command_dir  = self.get_command_dir(command)
        if command_dir == None:
            return result
        for current in fs.listdir(command_dir):
            if current != '.mold':
                result.append(current)
        return result

    def link_conf(self):
        if self.check_flag_set('--no-linking'):
            print('NOTICE: conf was NOT linked')
            return 
        for conf in self.get_command_dirlist('conf'):
            fs.force_link(self.MOLD_ROOT + '/conf/' + conf, self.HOME + '/' + conf)
            print(f'LINKING conf: {conf}')

