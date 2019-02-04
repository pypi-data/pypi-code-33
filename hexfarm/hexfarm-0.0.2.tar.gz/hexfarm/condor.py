# -*- coding: utf-8 -*- #
#
# hexfarm/condor.py
#
#
# MIT License
#
# Copyright (c) 2018-2019 Brandon Gomes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

"""
Utilities for the HTCondor Parallel Computing Framework.

"""

# -------------- Standard Library -------------- #

import stat
import logging
import subprocess
from collections import UserList
from contextlib import contextmanager
from dataclasses import dataclass
from functools import partial
from inspect import cleandoc as code_format
from itertools import starmap
from pathlib import Path

# -------------- External Library -------------- #

from aenum import Enum, AutoValue

# -------------- Hexfarm  Library -------------- #

from .util import classproperty, value_or


logger = logging.getLogger(__name__)


__all__ = ('logger',
           'Command',
           'COMMANDS',
           'Universe',
           'Notification',
           'FileTransferMode',
           'TransferOutputMode',
           'Job',
           'JobConfig',
           'ConfigUnit',
           'PseudoDaemon')


try:
    import htcondor as ht
    __all__ = __all__ + ht.__all__
except Exception:
    logger.info('HTCondor could not be imported.')


class Command:
    """
    Basic Command Object.

    """

    @classproperty
    def prefix(cls):
        """Command Prefix."""
        return 'condor_'

    def __init__(self, name, *args, **kwargs):
        """Initialize Command."""
        self.name = name
        self.__args = list(args)
        self.__kwargs = kwargs

    @property
    def full_name(self):
        """Get Full Name of Command."""
        return type(self).prefix + self.name

    def run(self, *args, **kwargs):
        """Run Command."""
        return subprocess.run([self.full_name] + self.__args + list(args),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              **self.__kwargs,
                              **kwargs)

    def __call__(self, *args, **kwargs):
        """Run Command."""
        return self.run(*args, **kwargs)

    def help(self, *args, **kwargs):
        """Print Help Mode of Command."""
        return self('--help', *args, **kwargs)

    def man(self, *args, **kwargs):
        """Print Man Pages of Command."""
        return subprocess.run(['man', self.full_name] + list(args), **kwargs)


COMMANDS = ('advertise',
            'c-gahp',
            'c-gahp_worker_thread',
            'check_userlogs',
            'checkpoint',
            'ckpt_server',
            'cod',
            'collector',
            'compile',
            'config_val',
            'configure',
            'continue',
            'credd',
            'dagman',
            'drain',
            'fetchlog',
            'findhost',
            'ft-gahp',
            'gather_info',
            'gridmanager',
            'gridshell',
            'had',
            'history',
            'hold',
            'init',
            'install',
            'kbdd',
            'master',
            'master_s',
            'negotiator',
            'off',
            'on',
            'ping',
            'power',
            'preen',
            'prio',
            'procd',
            'q',
            'qedit',
            'qsub',
            'reconfig',
            'release',
            'replication',
            'reschedule',
            'restart',
            'rm',
            'root_switchboard',
            'router_history',
            'router_q',
            'router_rm',
            'run',
            'schedd',
            'set_shutdown',
            'shadow',
            'shadow.std',
            'shadow_s',
            'ssh_to_job',
            'startd',
            'starter',
            'starter.std',
            'stats',
            'status',
            'store_cred',
            'submit',
            'submit_dag',
            'suspend',
            'tail',
            'test_match',
            'transfer_data',
            'transferd',
            'updates_stats',
            'userlog',
            'userlog_job_counter',
            'userprio',
            'vacate',
            'vacate_job',
            'version',
            'vm-gahp',
            'vm-gahp-vmware',
            'vm_vmware',
            'vm_vmware.pl',
            'wait',
            'who')


def _make_commands(commands, dct):
    for name in commands:
        setname = ('condor_' + name).replace('.', '').replace('-', '_')
        dct[setname] = Command(name)


_make_commands(COMMANDS, globals())


class _NameEnum(Enum, settings=AutoValue):
    """"""

    def __str__(self):
        """"""
        return self.name


class Universe(_NameEnum):
    """
    Condor Universe Enum.

    """

    Vanilla, Standard, Scheduler, Local, Grid, Java, VM, Parallel, Docker


@dataclass
class Notification:
    """
    Notification Structure.

    """

    class Status(_NameEnum):
        """Notification Status."""
        Always, Complete, Error, Never

    email: str
    status: Status

    def __str__(self):
        """"""
        return ''


class FileTransferMode(_NameEnum):
    """
    File Transfer Mode.

    """

    Yes, No, IfNeeded


class TransferOutputMode(_NameEnum):
    """
    Transfer Output Mode.

    """

    OnExit, OnExitOrEvict


class Job:
    """
    Job Object.

    """

    @classmethod
    def _extract_job_id(cls, text):
        """Extract JobID from Condor Output."""
        try:
            return text.strip().split()[-1][0:-1]
        except IndexError:
            return None

    @classmethod
    def _construct_job(cls, submit_output, config):
        """Create Job from Condor Submit."""
        obj = cls()
        obj._submit_output = submit_output
        obj._job_id = cls._extract_job_id(submit_output.stdout.decode('utf-8'))
        obj._config = config
        return obj

    @classmethod
    def submit(cls, config, *args, **kwargs):
        """Submit Configuration and Return Job Object."""
        try:
            config_path = config.path
        except AttributeError:
            return cls()
        return cls._construct_job(condor_submit(config_path, *args, **kwargs), config)

    def __init__(self):
        """Initialize Job Object."""
        self._submit_output, self._job_id, self._config = None, None, None

    @property
    def submit_output(self):
        """Output from Condor Submit."""
        return self._submit_output

    @property
    def job_id(self):
        """Get JobID of Job."""
        return self._job_id

    @property
    def config(self):
        """Get Configuration for Job."""
        return self._config

    @property
    def is_empty_job(self):
        """Check if Job is Empty."""
        return self._job_id is None or self._config is None

    def remove(self, *args, **kwargs):
        """Remove Job."""
        return condor_rm(self.job_id, *args, **kwargs)

    def hold(self, *args, **kwargs):
        """Hold Job."""
        return condor_hold(self.job_id, *args, **kwargs)

    def release(self, *args, **kwargs):
        """Release Job."""
        return condor_release(self.job_id, *args, **kwargs)


class JobConfig(UserList):
    """
    Job Configuration Structure.

    """

    @classproperty
    def command_names(cls):
        """Get Possible Command Names for Condor Config File."""
        if not hasattr(cls, '_cmd_names'):
            cls._cmd_names = ('accounting_group',
                              'accounting_group_user',
                              'allow_startup_script',
                              'append_files',
                              'arguments',
                              'azure_admin_key',
                              'azure_admin_username',
                              'azure_auth_file',
                              'azure_image',
                              'azure_location',
                              'azure_size',
                              'batch_queue',
                              'boinc_authenticator_file',
                              'buffer_block_size',
                              'buffer_files',
                              'buffer_size',
                              'compress_files',
                              'concurrency_limits',
                              'concurrency_limits_expr',
                              'copy_to_spool',
                              'coresize',
                              'cream_attributes',
                              'cron_day_of_month',
                              'cron_day_of_week',
                              'cron_hour',
                              'cron_minute',
                              'cron_month',
                              'cron_prep_time',
                              'cron_window',
                              'dagman_log',
                              'deferral_prep_time',
                              'deferral_time',
                              'deferral_window',
                              'delegate_job_GSI_credentials_lifetime',
                              'description',
                              'docker_image',
                              'dont_encrypt_input_files',
                              'dont_encrypt_output_files',
                              'ec2_access_key_id',
                              'ec2_ami_id',
                              'ec2_availability_zone',
                              'ec2_block_device_mapping',
                              'ec2_ebs_volumes',
                              'ec2_elastic_ip',
                              'ec2_iam_profile_arn',
                              'ec2_iam_profile_name',
                              'ec2_instance_type',
                              'ec2_keypair',
                              'ec2_keypair_file',
                              'ec2_parameter_',
                              'ec2_parameter_names',
                              'ec2_secret_access_key',
                              'ec2_security_groups',
                              'ec2_security_ids',
                              'ec2_spot_price',
                              'ec2_tag_',
                              'ec2_tag_names',
                              'ec2_user_data',
                              'ec2_user_data_file',
                              'ec2_vpc_ip',
                              'ec2_vpc_subnet',
                              'email_attributes',
                              'encrypt_execute_directory',
                              'encrypt_input_files',
                              'encrypt_output_files',
                              'environment',
                              'error',
                              'executable',
                              'fetch_files',
                              'file_remaps',
                              'gce_auth_file',
                              'gce_image',
                              'gce_json_file',
                              'gce_machine_type',
                              'gce_metadata',
                              'gce_metadata_file',
                              'gce_preemptible',
                              'getenv',
                              'globus_rematch',
                              'globus_resubmit',
                              'globus_rsl',
                              'grid_resource',
                              'hold',
                              'hold_kill_sig',
                              'image_size',
                              'initialdir',
                              'input',
                              'jar_files',
                              'java_vm_args',
                              'job_ad_information_attrs',
                              'job_batch_name',
                              'job_lease_duration',
                              'job_machine_attrs',
                              'job_max_vacate_time',
                              'keep_claim_idle',
                              'keystore_alias',
                              'keystore_file',
                              'keystore_passphrase_file',
                              'kill_sig',
                              'kill_sig_timeout',
                              'leave_in_queue',
                              'load_profile',
                              'local_files',
                              'log',
                              'log_xml',
                              'machine_count',
                              'match_list_length',
                              'max_job_retirement_time',
                              'max_retries',
                              'max_transfer_input_mb',
                              'max_transfer_output_mb',
                              'my_proxy_credential_name',
                              'my_proxy_host',
                              'my_proxy_new_proxy_lifetime',
                              'my_proxy_password',
                              'my_proxy_refresh_threshold',
                              'my_proxy_server_dn',
                              'next_job_start_delay',
                              'nice_user',
                              'noop_job',
                              'noop_job_exit_code',
                              'noop_job_exit_signal',
                              'nordugrid_rsl',
                              'notification',
                              'on_exit_hold',
                              'on_exit_hold_reason',
                              'on_exit_hold_subcode',
                              'on_exit_remove',
                              'output',
                              'output_destination',
                              'periodic_hold',
                              'periodic_hold_reason',
                              'periodic_hold_subcode',
                              'periodic_release',
                              'periodic_remove',
                              'priority',
                              'queue',
                              'rank',
                              'remote_initialdir',
                              'remove_kill_sig',
                              'rendezvousdir',
                              'request_',
                              'request_cpus',
                              'request_disk',
                              'request_memory',
                              'requirements',
                              'retry_until',
                              'run_as_owner',
                              'should_transfer_files',
                              'skip_filechecks',
                              'stack_size',
                              'stream_error',
                              'stream_input',
                              'stream_output',
                              'submit_event_notes',
                              'success_exit_code',
                              'transfer_error',
                              'transfer_executable',
                              'transfer_input',
                              'transfer_input_files',
                              'transfer_output',
                              'transfer_output_files',
                              'transfer_output_remaps',
                              'universe',
                              'use_x509userproxy',
                              'vm_checkpoint',
                              'vm_disk',
                              'vm_macaddr',
                              'vm_memory',
                              'vm_networking',
                              'vm_networking_type',
                              'vm_no_output_vm',
                              'vm_type',
                              'vmware_dir',
                              'vmware_should_transfer_files',
                              'vmware_snapshot_disk',
                              'want_graceful_removal',
                              'want_name_tag',
                              'want_remote_io',
                              'when_to_transfer_output',
                              'x509userproxy',
                              'xen_initrd',
                              'xen_kernel',
                              'xen_kernel_params',
                              'xen_root')
        return cls._cmd_names

    @classmethod
    def load_from(cls, path, opener=open, *args, clean_input=lambda o: o.strip(), **kwargs):
        """Load Job Config from File."""
        config = cls(path=path)
        with opener(path, *args, **kwargs) as f:
            config.extend(clean_input(line) for line in f)
        return config

    def __init__(self, *lines, path=Path()):
        """Initialize Config."""
        self.__dict__['_write_mode'] = False
        super().__init__(*lines)
        self.path = path
        self._saved = False

    @property
    def lines(self):
        """Alias to Inner Structure."""
        return self.data

    @property
    def lines(self, new_lines):
        """Set Inner Structure."""
        self.data = new_lines

    def to_text(self, *, add_newline=True):
        """Return Config as Multiline Text."""
        base = '\n' if add_newline else ''
        return base.join(self)

    @property
    def as_text(self):
        """Return Config as Multiline Text."""
        return self.to_text()

    def save(self, path=None):
        """Save Job File to Path."""
        if not path:
            path = self.path
        path.write_text(self.as_text)
        self._saved = True

    def submit(self, *options, path=None, **kwargs):
        """Submit Job From Config."""
        if path:
            self.save(path=path)
        elif not self._saved:
            self.save()
        return Job.submit(self, *options, **kwargs)

    def __repr__(self):
        """Representation of Config File."""
        prefix = 'JobConfig('
        path_string = 'path="' + str(self.path) + '"|' if self.path else ''
        data_string = '[' + str(self.data[0:5])[1:-1] + (', ...]' if len(self) > 5 else ']')
        return prefix + path_string + data_string + ')'

    def __str__(self):
        """Get Config File as a String."""
        return self.as_text

    def _make_kv_string(self, key, value):
        """Make Key-Value String."""
        return str(key) + '=' + str(value)

    def add_keyvalues(self, **kwargs):
        """Append Key Value Pairs to Config."""
        self.extend(starmap(self._make_kv_string, kwargs.items()))

    def append(self, value):
        """Append to Config."""
        if not isinstance(value, str):
            super().append(str(value))
        else:
            super().append(value)

    def extend(self, other):
        """Extend Config by another Config."""
        if not isinstance(other, type(self)):
            super().extend(map(str, other))
        else:
            super().extend(other)

    def __add__(self, other):
        """Create Sum of Config."""
        if not isinstance(other, type(self)):
            return super().__add__(map(str, other))
        return super().__add__(other)

    def __iadd__(self, other):
        """Add to Config In Place."""
        self.extend(other)
        return self

    def queue(self, *args):
        """Add Queue to Config."""
        arg_string = (' ' + map(str, args)) if args else ''
        self.append('queue' + arg_string)

    @property
    @contextmanager
    def write_mode(self):
        """Use writing mode to add lines to file."""
        try:
            self._write_mode = True
            yield self
        finally:
            self._write_mode = False

    def __setattr__(self, name, value):
        """Set attributes."""
        if self._write_mode and name in type(self).command_names:
            self.append(self._make_kv_string(name, value))
        else:
            self.__dict__[name] = value


def attach_ext(name, directory, extension):
    """Attach Extension to File."""
    return directory / (name + '.' + extension)


class ConfigUnit:
    """
    Configuration Unit.

    """

    def __init__(self, name, directory=None, *, exec_ext='py', config_ext='config', log_ext='log', output_ext='out', error_ext='error'):
        """Post-Initialize ConfigUnit."""
        self._name = name
        self._directory = Path(value_or(directory, '.'))
        self.job_config = JobConfig()
        self._rebuild(exec_ext, config_ext, log_ext, output_ext, error_ext, first_time=True)

    @property
    def file_dictionary(self):
        """File Dictionary of Keys against Paths."""
        return {'initialdir': self.directory,
                'log': self.logfile,
                'output': self.output,
                'error': self.errorfile,
                'executable': self.executable}

    def _name_map(self):
        """Map Extentions to Paths."""
        return partial(attach_ext, self.name, self.directory)

    def _rebuild(self, exec_ext='py', config_ext='config', log_ext='log', output_ext='out', error_ext='error', *, first_time=False):
        """Rebuild Configuration."""
        name_map = self._name_map()
        self.executable = name_map(exec_ext)
        self.configfile = name_map(config_ext)
        self.logfile = name_map(log_ext)
        self.output = name_map(output_ext)
        self.errorfile = name_map(error_ext)

        if not first_time:
            marked_indices = deque()
            for i, line in enumerate(self.job_config):
                if any(line.lower().startswith(key) for key in self.file_dictionary):
                    marked_indices.append(i)

            new_config = JobConfig()
            index = 0
            while marked_indices:
                mark = marked_indices.popleft()
                if mark > index:
                    new_config.extend(self.job_config[index:mark])
                    index = mark
                if index == mark:
                    key, _ = map(lambda s: s.strip(), self.job_config[index].strip().split('='))
                    new_config.add_keyvalues(**{key: self.file_dictionary[key.lower()]})
                    index += 1
            new_config.extend(self.job_config[index:])
            self.job_config = new_config

        self.job_config.path = self.configfile

    @property
    def name(self):
        """Get Name of Config Unit."""
        return self._name

    @name.setter
    def name(self, new_name):
        """Set Name of Config Unit."""
        self._name = new_name
        self._rebuild(first_time=False)

    @property
    def directory(self):
        """Get Home Directory of Config Unit."""
        return self._directory

    @directory.setter
    def directory(self, new_directory):
        """Set Home Directory of Config Unit."""
        self._directory = new_directory
        self._rebuild(first_time=False)

    def make_job_config(self, initial_vars, post_vars, *, save_configuration=False, absolute_paths=True, **kwargs):
        """Make Job Config."""
        configuration = JobConfig(path=self.configfile)
        configuration.add_keyvalues(**initial_vars)

        map_absolute = (lambda p: p.absolute()) if absolute_paths else (lambda p: p)
        with configuration.write_mode as config:
            config.initialdir = map_absolute(self.directory)
            config.log = map_absolute(self.logfile)
            config.output = map_absolute(self.output)
            config.error = map_absolute(self.errorfile)
            config.executable = map_absolute(self.executable)

        configuration.add_keyvalues(**post_vars)
        configuration.add_keyvalues(**kwargs)
        if save_configuration:
            self.job_config = configuration
        return configuration

    @property
    def as_text(self):
        """Return Job Config as Text."""
        return self.job_config.as_text

    def save(self, *args, make_new_config=False, **kwargs):
        """Save Config Setup."""
        if not self.directory.exists():
            self.directory.mkdir(parents=True, exist_ok=True)
        if make_new_config:
            self.make_job_config(*args, save_configuration=True, **kwargs)
        return self.job_config.save(path=self.configfile)

    def submit(self, *args, **kwargs):
        """Submit Job."""
        return self.job_config.submit(*args, **kwargs)


class PseudoDaemon(ConfigUnit):
    """
    Condor PseudoDaemon.

    """

    @classproperty
    def source_header(cls):
        """Default Source Header."""
        return code_format('''
            #!/usr/bin/env python3
            # -*- coding: utf-8 -*-

            import sys
            import time
            import logging

            logger = logging.getLogger(__name__)
            ''')

    @classproperty
    def source_try_hexfarm_import(cls):
        """Default Hexfarm Import."""
        return code_format('''
            try:
                import hexfarm as hex
                from hexfarm import condor
            except ImportError:
                pass
            ''')

    @classproperty
    def source_main_wrapper(cls):
        """Default Main Wrapper."""
        return code_format('''
            if __name__ == '__main__':
                sys.exit(main(sys.argv))
            ''')

    @classproperty
    def source_footer(cls):
        """Default Footer."""
        return cls.source_main_wrapper + '\n'

    @classproperty
    def default_source(cls):
        """Default Source Code."""
        return '\n\n'.join((cls.source_header,
                            cls.source_try_hexfarm_import,
                            code_format('''
                                def main(argv):
                                    argv = argv[1:]
                                    print(argv, len(argv), 'args')
                                    return 0
                                '''),
                            cls.source_footer))

    def __init__(self, name, directory=None, source=None, *args, **kwargs):
        """Initialize PseudoDaemon."""
        super().__init__(name, directory=directory, *args, **kwargs)
        self.source = value_or(source, type(self).default_source)

    def quick_start(self):
        """Quick Start PseudoDaemon."""
        self.make_job_config(initial_vars={'universe': Universe.Vanilla, 'getenv': True},
                             post_vars={'stream_output': True, 'stream_error': True},
                             save_configuration=True)
        self.job_config.queue()
        self.generate_executable(self.source)
        return self.start()

    def generate_executable(self, source=None, *, rewrite=True):
        """Generate PseudoDaemon Source Code."""
        if not self.directory.exists():
            self.directory.mkdir(parents=True, exist_ok=True)
        if rewrite and self.executable.exists():
            self.executable.unlink()
        self.executable.touch(exist_ok=True)
        self.executable.write_text(value_or(source, type(self).default_source))
        self.executable.chmod(self.executable.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        return self.executable

    def start(self, *args, **kwargs):
        """Start PseudoDaemon."""
        return self.submit(*args, **kwargs)
