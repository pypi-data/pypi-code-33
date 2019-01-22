# Copyright (C) 2018  Sean Z <sean.z.ealous@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import shlex
import netaddr
from distutils.spawn import find_executable

root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, root)
# pylint: disable=no-name-in-module,import-error
from common import logger
from common import utils
from common.parser import line_parser

INSTALLED_OVS_VSCTL = find_executable('ovs-vsctl')

class VSCtl(object):
    def __init__(self):
        self.ovs_vsctl_path = INSTALLED_OVS_VSCTL
    
    def run(self, command, table_format='list', data_format='string', parser=None, ignore_errcode=False):
        """
        Executes ovs-vsctl command.

        `command` is an str type and the format is the same as 'ovs-vsctl`
        except for omitting 'ovs-vsctl' in command format.

        For example, if you want to get the list of ports, the command
        for 'ovs-vsctl' should like 'ovs-vsctl list port' and `command`
        argument for this method should be::

            >>> from ovs_vsctl import VSCtl
            >>> vsctl = VSCtl()
            >>> vsctl.run(command='list port')
            <subprocess.Popen object at 0x7fbbe9d549e8>

        :param command: Command to execute.
        :param table_format: Table format. Meaning is the same as '--format'
         option of 'ovs-vsctl' command.
        :param data_format: Cell format in table. Meaning is the same as
         '--data' option of 'ovs-vsctl' command.
        :param parser: Parser class for the outputs. If this parameter is
         specified `table_format` and `data_format` is overridden with
         `table_format='list'` and `data_format='json'`.
        :param ignore_errcode: if raise an exception when command return a non-zero code.
        :return: Output of 'ovs-vsctl' command. If `parser` is not specified,
         returns an instance of 'subprocess.Popen'. If `parser` is specified,
         the given `parser` is applied to parse the outputs.
        :raise: * vsctl.VSCtlCmdExecError -- When the given command fails.
                * vsctl.exception.VSCtlCmdParseError -- When the given parser fails to parse the outputs.
        """

        # Constructs command.
        args = [
            self.ovs_vsctl_path,
        ]

        if parser:
            table_format = 'list'
            data_format = 'json'
        args.extend([
            '--format={}'.format(table_format),
            '--data={}'.format(data_format),
        ])
        
        args.extend(shlex.split(command))

        # Executes command.
        # pylint: disable=undefined-variable
        process = utils.run(args)
        if (process.returncode != 0) and (not ignore_errcode):
            raise VSCtlCmdExecError(process.stderr.read())

        # If parser is specified, applies parser and returns it.
        if parser:
            try:
                if process.returncode != 0:
                    return parser(process.stderr.read())
                else:
                    return parser(process.stdout.read())
            except Exception as e:  # pylint: disable=invalid-name
                raise VSCtlCmdParseError(e)

        # Returns outputs in str type.
        return process
    
    def br_exist(self, br_name):
        process = self.run('br-exists {}'.format(br_name), ignore_errcode=True)
        return process.returncode == 0
    
    def add_br(self, br_name):
        if self.br_exist(br_name):
            logger.error('Bridge {} already exist.'.format(br_name))
            return 0
        
        self.run('add-br {}'.format(br_name))
    
    def del_br(self, br_name):
        if self.br_exist(br_name):
            self.run('del-br {}'.format(br_name))
    
    def add_port(self, br_name, port_name, tag_id=0):
        self.del_port(br_name, port_name)
        
        tag = "" if tag_id==0 or tag_id == "" else "tag={}".format(tag_id)
        cmd = "add-port {} {} {}".format(br_name, port_name, tag)
        result = self.run(cmd, parser=line_parser)
        logger.debug('\n'.join(result))
        return '\n'.join(result)
    
    def del_port(self, br_name, port_name):
        cmd = "del-port {} {}".format(br_name, port_name)
        result = self.run(cmd, parser=line_parser, ignore_errcode=True)
        logger.debug('\n'.join(result))
    
class VSCtlCmdExecError(Exception):
    """
    Raised exception when 'ovs-vsctl' command returns non-zero exit code.
    """

class VSCtlCmdParseError(Exception):
    """
    Raised exception when fails to parse the outputs of 'ovs-vsctl' command.
    """
