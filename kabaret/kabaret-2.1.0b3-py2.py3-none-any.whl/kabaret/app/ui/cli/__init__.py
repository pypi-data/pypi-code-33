
from __future__ import print_function

import os
import sys
import traceback

from ...session import KabaretSession


class CLIMode(object):

    def __init__(self, session):
        super(CLIMode, self).__init__()
        self.session = session
        self.alive = False
        self.locals = {}

    def prompt(self):
        return '//' + self.__class__.__name__ + '>'

    def stop(self):
        self.alive = False

    def start(self):
        self.alive = True
        while self.alive:
            line = raw_input(self.prompt())
            ret = self.process(line)
            if ret is not None:
                self.locals['_'] = ret
                self.echo(' ', ret)

    def get_cmd_method(self, cmd_name):
        try:
            return getattr(self, 'do_' + cmd_name)
        except AttributeError:
            self.echo('Unknown Command %r' % (cmd_name,))

    def echo(self, *words):
        print(' '.join([str(i) for i in words]))

    def do_help(self, cmd_name=None):
        '''
        Get help on available commands.
        help        -> list available commands
        help cmd    -> show the documentation for 'cmd'
        '''
        if cmd_name is None:
            self.echo('Commands:')
            for n in dir(self):
                if n.startswith('do_'):
                    meth = getattr(self, n)
                    doc = meth.__doc__ or ''
                    end = ''
                    doc = doc.strip()
                    if '\n' in doc:
                        end = '...'
                        doc = doc.split('\n', 1)[0]
                    maxlen = 40
                    if len(doc) > maxlen:
                        end = '...'
                        doc = doc[:maxlen - 3]
                    if doc:
                        doc = ': ' + doc
                    self.echo('%10s%s' % (n[3:], doc + end))
        else:
            meth = self.get_cmd_method(cmd_name)
            if meth is not None:
                self.echo('Help for ' + cmd_name + ':')
                self.echo(meth.__doc__ or '   No Help Defined :/')

    def process(self, line):
        self.session.tick()
        line = line.strip()
        if not line:
            return
        if ' ' in line:
            cmd_name, args = line.split(' ', 1)
        else:
            cmd_name = line
            args = ''
        argv = [i for i in args.split(' ') if i]
        meth = self.get_cmd_method(cmd_name)
        if meth is not None:
            try:
                return meth(*argv)
            except Exception:
                traceback.print_exc()


class Home(CLIMode):
    '''Navigate to available command spaces'''

    def __init__(self, session):
        super(Home, self).__init__(session)
        self.current_mode = None
        self._modes = {
            'CLUSTER': Cluster(session),
            'FLOW': Flow(session),
        }

    def prompt(self):
        if self.current_mode is not None:
            return self.current_mode.prompt()
        return super(Home, self).prompt()

    def do_quit(self):
        '''
        Quit the command line interface.
        '''
        self.stop()

    def do_q(self):
        '''
        Alias for quit.
        '''
        self.do_quit()

    def do_ls(self):
        '''
        Lists the available stuffs to cd to.
        '''
        for k in sorted(self._modes.keys()):
            self.echo('   %s - %s' % (k, self._modes[k].__doc__))

    def do_cd(self, name):
        '''
        Change current location.
        '''
        try:
            mode = self._modes[name]
        except Exception:
            self.echo('Unknown cd target %r' % (name,))
            return
        self.current_mode = mode
        mode.start()
        self.current_mode = None


class Cluster(CLIMode):
    '''Cluster tools'''

    def do_q(self):
        '''
        Alias for home.
        '''
        self.do_home()

    def do_home(self):
        '''
        Go back home.
        '''
        self.stop()

    def do_send(self, *words):
        '''Send a message to all sessions.'''
        self.session.cmds.Cluster.broadcast(*words)


class Flow(CLIMode):

    def __init__(self, session):
        super(Flow, self).__init__(session)
        self._pwd = None
        self._last_pwd = None

    def start(self):
        # clean up and resolve to default.
        self._pwd = self._join_path(self._pwd)
        super(Flow, self).start()

    def prompt(self):
        return 'Flow:/' + self._pwd + '>'

    def do_q(self):
        '''
        Alias for home.
        '''
        self.do_home()

    def do_home(self):
        '''
        Go back home.
        '''
        self.stop()

    def _join_path(self, a, b=None):
        if b is None:
            c = a
        else:
            c = os.path.join(a, b)
            c = os.path.normpath(c).replace('\\', '/')
            if c == '.':
                c = ''
        c = self.session.cmds.Flow.resolve_path(c)
        return c

    def do_lsa(self, path=None):
        self._do_ls(path, all=True)

    def do_ls(self, path=None):
        self._do_ls(path)

    def _do_ls(self, path=None, all=False):
        oid = self._join_path(self._pwd, path)

        relations, mapped_names = self.session.cmds.Flow.ls(oid, show_hidden=all, show_protected=all)
        for (
            relation_name, relation_type,
            is_action, is_map,
            ui_config
        ) in relations:
            if is_action:
                self.echo('%15s' % ('[' + relation_name + ']'))
            elif relation_type == 'Param':
                try:
                    value_oid = self._join_path(oid, relation_name)
                    value = self.session.cmds.Flow.get_value(value_oid)
                except Exception as err:
                    value = '%s/%s Error: %s' % (self._pwd,
                                                 relation_name, err,)
                self.echo('%15s=%r' % (relation_name, value))
            elif relation_type == 'Child':
                self.echo('%15s/' % (relation_name))
            else:
                self.echo('%15s (%s)' % (relation_name, relation_type))

        for mapped_name in mapped_names:
            self.echo('%15s/' % (mapped_name,))

    def do_cd(self, name=None):
        if name is None:
            name = '/'

        if name == '-':
            curr = self._pwd
            self._pwd = self._last_pwd
            self._last_pwd = curr
            return

        tmp = self._pwd
        self._pwd = self._join_path(self._pwd, name)
        if self._pwd != tmp:
            self._last_pwd = tmp

    def do_set(self, value_name, value):
        oid = self._join_path(self._pwd, value_name)
        try:
            value = eval(value)
        except Exception:
            pass
        self.session.cmds.Flow.set_value(oid, value)

    def do_get(self, value_name):
        oid = self._join_path(self._pwd, value_name)
        self.echo(self.session.cmds.Flow.get_value(oid))

    def do_run(self, action_name):
        oid = self._join_path(self._pwd, action_name)
        buttons = self.session.cmds.Flow.get_action_buttons(oid)
        if buttons:
            for i, button in enumerate(buttons):
                print('%i) %s' % (i, button))
            r = raw_input('Enter a number or nothing to cancel: ')
            try:
                r = int(r)
                button = buttons[r]
            except Exception:
                if not r:
                    return
                self.echo('Invalid entry: %r' % (r,))
                return
        else:
            button = None
        result = self.session.cmds.Flow.run_action(oid, button)
        self.echo('>>>', result)


class KabaretCLISession(KabaretSession):

    def __init__(self, session_name='KCLIS'):
        # create this before base init bc self.log might be called uppon init
        self.cli = Home(self)
        super(KabaretCLISession, self).__init__(session_name)

    def log(self, context, *words):
        if self.cli.alive:
            print('')
        super(KabaretCLISession, self).log(context, *words)
        if self.cli.alive:
            print('\n' + self.cli.prompt(), end='')

    def start(self):
        self.cli.start()
