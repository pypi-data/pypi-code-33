from subprocess import (
    Popen,
    PIPE,
    STDOUT,
)


class Dmenu:
    '''represents an dmenu with all the arguments.'''

    def __init__(self, entries, *, lines=None):
        '''
        params:
            entries: iterable containing strings being the entries of dmenu
            lines: number of rows dmenu gets displayed with
        '''
        self.entries = entries
        self.lines = lines

    def run(self):
        cmd = ['dmenu']
        if self.lines:
            cmd.extend(('-l', str(self.lines)))
        dmenu = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        stdin_input = '\n'.join(self.entries).encode()
        stdout = dmenu.communicate(input=stdin_input)[0].decode().strip()
        return stdout
