import Exscript
import sys
from Exscript.protocols import SSH2, Telnet


class Cli:
    handler = None

    def __init__(self, address, port, protocol, username='', password='', logger=None,
                 prompt_list=None):
        """Connect to device with selected protocol

        :param address: address of the target host
        :param port: communication port
        :param protocol: SSH or Telnet
        :param username:
        :param password:
        :param logger: cloudshell.core.logger.qs_logger object
        :param prompt_list: optional custom list of prompt patterns used to match commnad prompt on receive
        :return:
        """

        self.account = Exscript.Account(username, password)
        self.default_prompt_list = prompt_list

        if logger:
            self.logger = logger
        else:
            self.logger = None

        self._write_log('Initializing: address=' + address + ';port=' + str(port) + ';protocol=' + protocol +
                        'prompt_list=' + str(self.default_prompt_list))
        if protocol.lower() == 'telnet':
            try:

                self.handler = Telnet()
                self._write_log('Got Telnet handler object')
                if not self.default_prompt_list:
                    self.default_prompt_list = self.handler.get_prompt()
                    self._write_log('Setting promp list to library default: ' + str(self.default_prompt_list))
                self.handler.set_prompt(self.default_prompt_list)
                self.handler.connect(address, port)
                self._write_log('Connected')

            except:
                self._write_log('Unable to connect to target', 'error')
                self._write_log(sys.exc_info()[0], 'error')
                raise

        elif protocol.lower() == 'ssh':
            try:
                self.handler = SSH2()
                self._write_log('Got SSH handler object')
                if not self.default_prompt_list:
                    self.default_prompt_list = self.handler.get_prompt()
                    self._write_log('Setting promp list to library default: ' + str(self.default_prompt_list))
                self.handler.set_prompt(self.default_prompt_list)
                self.handler.connect(address, port)
                self._write_log('Connected')
            except:
                self._write_log('Unable to connect to target', 'error')
                self._write_log(sys.exc_info()[0], 'error')
                raise

        else:
            self._write_log('invalid protocol: ' + protocol, 'error')
            raise AttributeError('invalid protocol')

    def login(self):
        """ Logs in to device usuing protocol login procedure

        :return:
        """
        try:
            self.handler.login(self.account)
            self._write_log('Logged In')
        except:
            print "unable to login to target"
            self._write_log('Unable to login to target', 'error')
            self._write_log(sys.exc_info()[0], 'error')
            raise

    def authenticate(self):
        """ Logs in to device usuing protocol authenticate procedure

        :return:
        """
        try:
            self.handler.authenticate(self.account)
            self._write_log('Authenticated!')
        except:
            self._write_log('Unable to authenticate to target', 'error')
            self._write_log(sys.exc_info()[0], 'error')
            raise

    def send_and_receive(self, command, pattern_list=None):
        """ Sends a command and receives the response using expect

        :param command:
        :param pattern_list: optional, if None uses the default for the session
        :return:
        """
        if pattern_list:
            if type(pattern_list) != list:
                pattern_list = [pattern_list]
            self.handler.set_prompt(pattern_list)
        else:
            pattern_list = self.default_prompt_list
            self.handler.set_prompt(self.default_prompt_list)

        pattern_index, match = self.handler.execute(command)

        return pattern_index, pattern_list[pattern_index], match.string  # Pattern index, pattern, buffer

    def send(self, command):
        """ Sends command without reading response buffer

        :param command:
        :return:
        """
        self.handler.send(command)

    def receive(self, pattern_list=None):
        """ Reads from current response buffer

        :param pattern_list: if None uses default pattern list for the session
        :return:
        """
        if pattern_list:
            if type(pattern_list) != list:
                pattern_list = [pattern_list]
        else:
            pattern_list = self.default_prompt_list

        pattern_index, match = self.handler.expect(pattern_list)

        return pattern_index, pattern_list[pattern_index], match.string  # Pattern index, pattern, buffer

    def _write_log(self, message, level='info'):
        if self.logger:
            method = getattr(self.logger, level)
            method(message)


def __main__():
    # Usage example
    session = Cli('localhost', 22, 'Telnet', 'USERNAME', 'PASSWORD', prompt_list=['.*>', '.*]', '.* ENTER'])
    session.login()
    result = session.send_and_receive('cli command')
    print result

if __name__ == '__main__':
    __main__()
