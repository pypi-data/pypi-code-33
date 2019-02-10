# -*- coding: utf-8 -*- #
#
# hexfarm/condor/core.py
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
Core Utilities for the HTCondor Parallel Computing Framework.

"""

# -------------- Standard Library -------------- #

import tempfile
from collections import UserList, deque
from collections.abc import Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field, InitVar
from functools import partial
from itertools import starmap
from typing import Sequence

# -------------- External Library -------------- #

from inflection import underscore
from aenum import Enum, AutoValue
from path import Path

# -------------- Hexfarm  Library -------------- #

from ..shell import decoded, Command, me
from ..util import classproperty, map_value_or, value_or


__all__ = (
    'CondorCommand',
    'CONDOR_COMMANDS',
    'current_jobs',
    'user_jobs',
    'Universe',
    'Notification',
    'FileTransferMode',
    'TransferOutputMode',
    'This',
    'condor_format_mapping',
    'condor_format_sequence',
    'extract_job_ids',
    'CONDOR_SUBMIT_COMMANDS',
    'JobConfig',
    'minimal_config',
    'submit_config',
    'Job',
    'job_dict',
    'JobCompletedException',
    'JobMap',
    'ConfigUnitBase',
    'ProcessUnit',
    'ClusterUnit',
    'MultiClusterUnit',
    'ConfigRunner',
    'JobManager'
)


class CondorCommand(Command, prefix='condor_'):
    """Condor Command Object."""


CONDOR_COMMANDS = (
    'advertise',
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
    'who'
)


def add_condor_commands(commands, command_dict):
    """Build Condor Commands for Globals."""
    name_list = []
    for name in commands:
        setname = (CondorCommand.prefix + name).replace('.', '').replace('-', '_')
        name_list.append(setname)
        command_dict[setname] = CondorCommand(name)
    return tuple(name_list)


__all__ += add_condor_commands(CONDOR_COMMANDS, globals())


def current_jobs(*usernames):
    """List the Current Jobs by Users."""
    query = condor_q(' '.join(usernames)) if usernames else condor_q()
    text = decoded(query).strip().split('\n')
    user_dict = dict()
    for job_id, name, *_ in list(map(lambda l: l.strip().split(), text))[2:-2]:
        if name not in user_dict:
            user_dict[name] = []
        user_dict[name].append(job_id)
    return user_dict


def user_jobs(username=me()):
    """Get User's Jobs."""
    return current_jobs(username)[username]


class NameEnum(Enum, settings=AutoValue):
    """Named Enum Objects."""

    def __str__(self):
        """Get Name as String."""
        return self.name


class Universe(NameEnum):
    """Condor Universe Enum."""
    Vanilla, Standard, Scheduler, Local, Grid, Java, VM, Parallel, Docker


@dataclass
class Notification:
    """Notification Structure."""

    class Status(NameEnum):
        """Notification Status."""
        Always, Complete, Error, Never

    email: str
    status: Status
    attributes: Sequence[str] = field(default_factory=list)

    def __str__(self):
        """Get String Representation of Notification."""
        attributes = f'email_attributes={",".join(self.attributes)}'
        return '\n'.join((f'notification={self.status}',
                          f'notify-user={self.email}',
                          f'{attributes if self.attributes else ""}'))


class FileTransferMode(NameEnum):
    """File Transfer Mode."""
    Yes, No, IfNeeded


class TransferOutputMode(NameEnum):
    """Transfer Output Mode."""
    OnExit, OnExitOrEvict


class This(NameEnum):
    """Universal Condor Object Variables."""
    ClusterId, Cluster, ProcId, Process, Node, Step, ItemIndex, Row, Item

    def __str__(self):
        """Get String Form of Variable."""
        return f'$({super().__str__()})'


def kv_string(key, value, *, connector='='):
    """Make Key-Value String."""
    return f'{key}{connector}{value}'


def condor_format_mapping(mapping):
    """Format a Mapping According to Condor Conventions."""
    return ';'.join(starmap(kv_string, mapping.items()))


def condor_format_sequence(sequence):
    """Format a Sequence According to Condor Conventions."""
    return ' '.join(map(str, sequence))


def open_key_value_pairs(self, *pairs, connector='=', ignore_unpacking_error=True):
    """Open Pair and Check for Keys and Values."""
    if not pairs:
        return None, None
    if len(pairs) == 1:
        try:
            key, value = tuple(map(lambda o: o.strip(), pairs[0].split(connector)))
            return ((key, value), )
        except ValueError as value_error:
            if ignore_unpacking_error:
                return ((None, None), )
            raise value_error
    else:
        #TODO: replace recursive implementation
        return sum(tuple(open_key_value_pairs(line) for line in pairs), ())


def extract_job_ids(condor_submit_text):
    """Extract Job Ids from Condor Submit Text."""
    _, _, count, *_, cluster = condor_submit_text.strip().split()
    for process in map(str, range(int(count))):
        yield cluster + process


class WriteModeMixin:
    """
    Writing Mode Mixin Class.

    """

    def __init_subclass__(cls, write_mode_keywords, write_mode_invalid_keywords=None, **kwargs):
        """Initialize Write-Mode Keywords for Class."""
        super().__init_subclass__(**kwargs)
        cls._write_mode_keywords = set(write_mode_keywords)
        cls._write_mode_invalid_keywords = map_value_or(set, write_mode_invalid_keywords, set())

    def _write_mode_insert(self, name, value):
        """Insert Key-Value Pair into Object."""
        return NotImplemented

    def _write_mode_invalid_keyword(self, name, value):
        """Check if Write-Mode Key is valid."""
        raise ValueError(f'Key: {name} is an invalid Keyword.')

    @property
    @contextmanager
    def write_mode(self):
        """Writing Mode Context Manager."""
        try:
            self._write_mode = True
            yield self
        finally:
            self._write_mode = False

    def __setattr__(self, name, value):
        """Set attributes."""
        if self._write_mode:
            if name in type(self)._write_mode_invalid_keywords:
                self._write_mode_invalid_keyword(name, value)
            elif name in type(self)._write_mode_keywords:
                self._write_mode_insert(name, value)
        else:
            super().__setattr__(name, value)


CONDOR_SUBMIT_COMMANDS = {
    'accounting_group',
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
    'xen_root'
}


class JobConfig(UserList, WriteModeMixin, write_mode_keywords=CONDOR_SUBMIT_COMMANDS):
    """
    Job Configuration Base.

    """

    @classproperty
    def command_names(cls):
        """Get Possible Command Names for Condor Config File."""
        return cls._write_mode_keywords

    @classmethod
    def from_file(cls, path, opener=open, *args, clean_input=str.strip, keep_path=True, **kwargs):
        """Load Job Config from File."""
        with opener(path, *args, **kwargs) as file:
            return cls(*(clean_input(line) for line in file), path=path if keep_path else None)

    def __init_subclass__(cls, special_key_map=None, **kwargs):
        """Initialize Subclasses with Special Key Maps."""
        super().__init_subclass__(**kwargs)
        if special_key_map is not None:
            cls.special_key_map = special_key_map

    def __init__(self, *lines, path=None):
        """Initialize Config."""
        self.__dict__['_write_mode'] = False
        super().__init__(*lines)
        self._path = path

    def _build_path_save_mechanism(self):
        """Build Path Save Mechanism."""
        if hasattr(self, 'save'):
            raise AttributeError('JobConfig has no attribute _build_path_save_mechanism.')

        def _save(self):
            Path(s.path).write_text(s.as_text)

        def _save_as(s, new_path):
            s._path = new_path
            return s.save()

        self.save = _save
        self.save.__doc__ = """Save Config to File."""
        self.save_as = _save_as
        self.save_as.__doc__ = """Save Config at New Path."""

    @property
    def path(self):
        """Get Path of Config if Exists."""
        if self._path is None:
            raise AttributeError('JobConfig has no attribute path.')
        try:
            self._build_path_save_mechanism()
        except AttributeError:
            pass
        return self._path

    @path.setter
    def path(self, value):
        """Set Path of Config if Exists."""
        self._path = value
        try:
            self._build_path_save_mechanism()
        except AttributeError:
            pass

    @property
    def lines(self):
        """Alias to Inner Structure."""
        return self.data

    @property
    def lines(self, new_lines):
        """Set Inner Structure."""
        self.data = new_lines

    def to_text(self, *, with_newlines=True):
        """Return Config as Multiline Text."""
        return ('\n' if with_newlines else '').join(self)

    @property
    def as_text(self):
        """Return Config as Multiline Text."""
        return self.to_text()

    def __repr__(self):
        """Representation of Config File."""
        data_string = f'[{str(self.data[0:6])[1:-1]}{", ...]" if len(self) > 6 else "]"}'
        return f'{type(self).__name__}({data_string})'

    def __str__(self):
        """Get Config File as a String."""
        return self.as_text

    def append(self, value, *, skip_special_key_search=False):
        """Append to Config."""
        if not skip_special_key_search and hasattr(type(self), 'special_key_map'):
            for key, internal_value in open_key_value_pairs(*value.strip().split('\n')):
                try:
                    special_name, factory = type(self).special_key_map[key]
                    setattr(self, special_name, factory(internal_value))
                except KeyError:
                    pass
        super().append(str(value))

    def insert(self, index, value):
        """Insert Value at Index."""
        return NotImplemented

    def append_key_value_pair(self, key, value, *args, **kwargs):
        """Append Key Value Pair to Config."""
        return self.append(kv_string(key, value), *args, **kwargs)

    def _write_mode_insert(self, name, value):
        """Insert Key-Value Pair into Object."""
        return self.append_key_value_pair(name, value)

    def extend(self, other, *args, **kwargs):
        """Extend Config by another Config."""
        for obj in other:
            self.append(str(obj), *args, **kwargs)

    def add_pairs(self, pairs, *args, **kwargs):
        """Append Key Value Pairs to Config."""
        self.extend(starmap(kv_string, pairs.items()), *args, **kwargs)

    def __add__(self, other):
        """Create Sum of Config."""
        if not isinstance(other, type(self)):
            return super().__add__(map(str, other))
        return super().__add__(other)

    def __iadd__(self, other):
        """Add to Config In Place."""
        self.extend(list(other))
        return self

    def with_arguments(self, *args):
        """Add Arguments to Config."""
        self.append_key_value_pair('arguments', condor_format_sequence(args))

    def append_comments(self, *comments):
        """Add Comments to Config."""
        if not comments:
            return
        if len(comments) == 1:
            comments = comments[0].split('\n')
        self.extend(map(lambda c: f'# {c}', comments))

    def append_email_notification(self, *notification):
        """Add Email Notification to Config."""
        if len(notification) == 1 and isinstance(notification[0], Notification):
            notification = str(notification)
        elif len(notification) == 2:
            notification = str(Notification(*notification))
        else:
            raise TypeError('Not a Notification Type.')
        self.extend(notification.split('\n'))

    def file_remapping(self, key='file_remaps', **mapping):
        """Add File Remapping to Config."""
        self.append_key_value_pair(str(key), condor_format_mapping(mapping),
                                   skip_special_key_search=True)

    def transfer_output_remapping(self, **mapping):
        """Transfer File Output Remapping."""
        self.file_remapping(key='transfer_output_remaps', **kwargs)

    def request_(self, name, value):
        """Special Request Tag."""
        self.append_key_value_pair(f'request_{name}', value)

    def queue(self, *args):
        """Add Queue to Config."""
        self.append(f'queue{(" " + condor_format_sequence(args)) if args else ""}')


def minimal_config(
    name,
    executable,
    directory,
    *,
    config_ext='cfg',
    log_ext='log',
    out_ext='out',
    error_ext='err',
    use_absolute_paths=True,
    keep_env=False
):
    """Construct Minimal Job Configuration."""
    directory = Path(directory)
    if use_absolute_paths:
        build_path = lambda ext: (directory / f'{name}.{ext}').abspath()
    else:
        build_path = lambda ext: directory / f'{name}.{ext}'
    config = JobConfig(path=build_path(config_ext))
    config.name = property(lambda s: name)
    with config.write_mode as config:
        config.executable = Path(executable).abspath()
        config.log = build_path(log_ext)
        config.getenv = keep_env
        config.initialdir = directory.abspath() if use_absolute_paths else directory
        config.output = build_path(out_ext)
        config.error = build_path(error_ext)
    return config


def submit_config(config, path=None, logfile=None, *args, **kwargs):
    """Submit Configuration File."""
    # FIXME: (DRY) generalize path making
    if path is None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / 'config.txt'
            temp_path.touch()
            temp_path.write_text(config.as_text)
            submit_output = decoded(condor_submit(temp_path, *args, **kwargs))
    else:
        if not path.exists():
            path.parent.makedirs_p()
            path.touch()
            path.write_text(config.as_text)
        submit_output = decoded(condor_submit(path, *args, **kwargs))
    return tuple(Job(config, job_id, logfile=logfile) for job_id in extract_job_ids(submit_output))


class Job:
    """
    Job Object.

    """

    def __init__(self, config, job_id, submitter=me(), logfile=None):
        """Initialize Job Object."""
        self._config = config
        self._job_id = job_id
        self._submitter = submitter
        self._logfile = logfile
        if logfile is None:
            try:
                self._logfile = self.config.logfile
            except AttributeError:
                pass

    @property
    def config(self):
        """Get Configuration for Job."""
        return self._config

    @property
    def job_id(self):
        """Get JobID of Job."""
        return self._job_id

    @property
    def logfile(self):
        """Get Path of Log File for this Job."""
        return self._logfile

    @property
    def submitter(self):
        """Job Submitter."""
        return self._submitter

    @property
    def is_empty_job(self):
        """Check if Job is Empty."""
        return self._job_id is None or self._config is None

    def remove(self, *args, **kwargs):
        """Remove Job."""
        result = condor_rm(self.job_id, *args, **kwargs)
        self._job_id = None
        return result

    def hold(self, *args, **kwargs):
        """Hold Job."""
        return condor_hold(self.job_id, *args, **kwargs)

    def release(self, *args, **kwargs):
        """Release Job."""
        return condor_release(self.job_id, *args, **kwargs)

    def check(self, wait_timeout=None):
        """Check if Job Has Completed."""
        args = ('-wait', str(wait_timeout)) if wait_timeout else ()
        if self.logfile:
            return not bool(condor_wait(Path(self.logfile).abspath(), *args).returncode)
        else:
            return self.job_id not in user_jobs(self.submitter)

    @property
    def has_completed(self):
        """Check if Job Has Completed."""
        return self.check(wait_timeout=1)

    def on_completion(self, f, *args, wait_timeout=None, **kwargs):
        """Run On Completion of Job."""
        if self.check(wait_timeout=wait_timeout):
            return f(self, *args, **kwargs)
        return False

    def __repr__(self):
        """Representation of Job."""
        return str(self)

    def __str__(self):
        """String conversion of Job."""
        return f'Job({self.job_id})'


def job_dict(*jobs):
    """Make Job Dictionary."""
    return {job.job_id: job for job in jobs}


class JobCompletedException(KeyError):
    """Job Completed Exception."""

    def __init__(self, job):
        """Initialize Exception."""
        super().__init__(f'Job {job.job_id} has already completed.')
        self._job = job

    @property
    def job(self):
        """Get Job which had Completed."""
        return self._job


class JobMap(Mapping):
    """
    Job Mapping Object.

    """

    def __init__(self, *jobs, remove_completed_jobs=False, remove_when_clearing=True):
        """Initialize Job Mapping."""
        self._jobs = job_dict(*jobs)
        self.remove_completed_jobs = remove_completed_jobs
        self.remove_when_clearing = remove_when_clearing

    @property
    def job_ids(self):
        """Return Job Ids."""
        return self.keys()

    @property
    def jobs(self):
        """Return Jobs."""
        return self.values()

    def __getitem__(self, key):
        """Get the Job at given Id."""
        job = self._jobs[key]
        if self.remove_completed_jobs and job.has_completed:
            del self._jobs[key]
            raise JobCompletedException(job)
        return job

    def pop_completed(self):
        """Pop off Jobs that have Completed."""
        out = []
        for job_id, job in tuple(self._jobs.items()):
            if job.has_completed:
                out.append(job)
                del self._jobs[job_id]
        return tuple(out)

    def __iter__(self):
        """Return Iterator over Jobs."""
        if self.remove_completed_jobs:
            self.pop_completed()
        return iter(self._jobs)

    def __len__(self):
        """Return Length of Job List."""
        if self.remove_completed_jobs:
            self.pop_completed()
        return len(self._jobs)

    def clear(self):
        """Clear All Jobs."""
        if self.remove_when_clearing:
            for job_id in self:
                self.remove_job(job_id)
        else:
            self._jobs.clear()

    def update(self, other):
        """Extend Job Map."""
        self._jobs.update(other)

    def append(self, *jobs):
        """Append Jobs to JobMap."""
        self.update(job_dict(*jobs))

    def pop(self, key, *default):
        """Pop Job Out of Map."""
        if len(default) not in (0, 1):
            raise TypeError('Only 1 Default Argument Allowed.')
        try:
            if self.remove_when_clearing:
                return self.remove_job(key)[0]
            else:
                return self._jobs.pop(key)
        except KeyError:
            if len(default) == 1:
                return default
            raise KeyError('Job Not Found.')

    def remove_job(self, job_id, *args, **kwargs):
        """Remove Job."""
        job = self[job_id]
        result = job.remove(*args, **kwargs)
        del self._jobs[job_id]
        return job, result

    def hold_job(self, job_id, *args, **kwargs):
        """Hold Job."""
        return self[job_id].hold(*args, **kwargs)

    def release_job(self, job_id, *args, **kwargs):
        """Release Job."""
        return self[job_id].release(*args, **kwargs)

    def __repr__(self):
        """Representation of JobMap."""
        return repr(self._jobs)

    def __str__(self):
        """String Conversion of JobMap."""
        return str(self._jobs)


class ConfigUnitBase(WriteModeMixin, write_mode_keywords=set()):
    """Configuration Unit Base Structure."""

    def __init_subclass__(cls, class_ad_name, class_ad_id_name, fixed_keys, make_prefix_config=True, **kwargs):
        """Initialize Configuration Subclasses."""
        super().__init_subclass__(**kwargs)
        setattr(cls, underscore(class_ad_name),
                classproperty(lambda c: f'$({class_ad_name})'))
        setattr(cls, underscore(class_ad_id_name),
                classproperty(lambda c: f'$({class_ad_id_name})'))
        for name in fixed_keys:
            fget = lambda s, n=name: kv_string(n, getattr(s, n)) if getattr(s, n) else ''
            setattr(cls, f'{underscore(name)}_kv_str', property(fget))
        if make_prefix_config:
            def _prefix_config(s):
                return JobConfig(getattr(s, f'{underscore(name)}_kv_str') for name in fixed_keys)
            setattr(cls, 'prefix_config', property(_prefix_config))

    def __init__(self, *args, config_path=None, **kwargs):
        """Initialize Configuration Unit."""
        super().__init__(*args, **kwargs)
        self.path = config_path

    def __str__(self):
        """Get String Representation of ConfigUnit."""
        return str(self.config)


class ProcessUnit(ConfigUnitBase,
                  class_ad_name='Process',
                  class_ad_id_name='ProcId',
                  fixed_keys=('initialdir', 'output', 'error'),
                  write_mode_keywords=CONDOR_SUBMIT_COMMANDS,
                  write_mode_invalid_keywords=('executable', 'log')):
    """
    Process Configuration Unit.

    """

    def __init__(self, executable, initialdir=None, output=None, error=None, **kwargs):
        """Initialize Process Configuration Unit."""
        super().__init__(**kwargs)
        self.executable = executable
        self.initialdir = map_value_or(Path, initialdir, None)
        self.output = map_value_or(Path, output, None)
        self.error = map_value_or(Path, error, None)
        self._config = JobConfig()

    def _write_mode_insert(self, name, value):
        """Insert Key-Value Pair into Internal Config."""
        self._config._write_mode_insert(name, value)

    def _write_mode_invalid_keyword(self, name, value):
        """Catch Invalid Keywords for Write-Mode."""
        if name == 'executable':
            raise TypeError('Cannot modify executable in ProcessUnit Context.')
        if name == 'log':
            raise TypeError('Cannot modify log in ProcessUnit Context.')

    @property
    def config(self):
        """Full Configuration."""
        return self.prefix_config + self._config

    def queue(self, n=1, *args, **kwargs):
        """Add Queue Command."""
        self._config.queue(n=n, *args, **kwargs)

    def queue_in(self, n=1, *args, **kwargs):
        """"""
        #TODO: implement
        return NotImplemented

    def queue_matching(self, n=1, *args, **kwargs):
        """"""
        #TODO: implement
        return NotImplemented

    def queue_from(self, n=1, *args, **kwargs):
        """"""
        #TODO: implement
        return NotImplemented


class ClusterUnit(ConfigUnitBase,
                  class_ad_name='Cluster',
                  class_ad_id_name='ClusterId',
                  fixed_keys=('executable', 'log'),
                  write_mode_keywords=CONDOR_SUBMIT_COMMANDS):
    """
    Cluster Configuration Unit.

    """

    def __init__(self, executable, log=None, *process_units, **kwargs):
        """Initialize Cluster Configuration Unit."""
        super().__init__(**kwargs)
        self.executable = executable
        self.log = map_value_or(Path, log, None)
        self.process_units = process_units

    def append_process(self, process_unit):
        """Append Process to Cluster Unit."""
        self.process_units.append(process_unit)

    def append_process_units(self, *process_units):
        """Extend Process Units."""
        self.process_units.extend(process_units)

    @property
    def config(self):
        """Full Configuration."""
        return sum(self.process_units, self.prefix_config)

    def save(self, path=None):
        """Save Config To Path."""
        path = value_or(path, self.path)
        if not path:
            raise TypeError('Path argument must be a valid file path if '
                            'stored config has no associated path.')
        Path(path).write_text(self.config.as_text)

    def submit(self, *args, use_temporary_file=False, **kwargs):
        """Submit Config As a Condor Job."""
        path = None if use_temporary_file else Path(self.path)
        if path and not path.exists():
            raise FileNotFoundError(f'Path {path} cannot be found.')
        return submit_config(self.config, path=path, logfile=self.log, *args, **kwargs)


class MultiClusterUnit:
    """
    Multi-Cluster Configuration Unit.

    """

    def __init__(self, prefix_config, *cluster_units):
        """Initialize Multi-Cluster Unit."""
        self.prefix_config = prefix_config
        self.cluster_units = cluster_units

    def append_cluster(self, cluster_unit):
        """Append Cluster to Units."""
        self.cluster_units.append(cluster_unit)

    def append_custer_units(self, *cluster_units):
        """Extend Cluster Units."""
        self.cluster_units.extend(cluster_units)

    @property
    def total_config(self):
        """Total Configuration."""
        return sum(self.cluster_units, self.prefix_config)

    def submit(self, *args, use_temporary_file=False, **kwargs):
        """Submit Config As a Condor Job."""
        #FIXME: figure out how to parse a multicluster unit condor_submit output so this can be
        #       joined into one file
        return tuple(cluster.submit(use_temporary_file=use_temporary_file, *args, **kwargs)
                     for cluster in self.cluster_units)


@dataclass
class ConfigRunner:
    """
    Configuration Runner.

    """

    config: JobConfig
    path: InitVar[Path]
    logfile: Path
    jobmap: JobMap

    def __post_init__(self, path):
        """Post-Initialize Config Runner."""
        if Path(path).abspath() != Path(self.config.path).abspath():
            self.config.save_as(path)

    @property
    def config_path(self):
        """Get Configuration Path."""
        return self.config.path

    @property
    def running_job_count(self):
        """Get Current Running Job Count."""
        return len(self.jobmap)

    def submit(self, *args, **kwargs):
        """Submit Jobs."""
        jobs = submit_config(self.config, path=self.config_path, logfile=self.logfile, *args, **kwargs)
        self.jobmap.append(*jobs)
        return jobs

    def submit_while(self, predicate, *args, wait=None, **kwargs):
        """Submit Jobs while predicate holds."""
        while predicate(self):
            self.submit(*args, **kwargs)
            if wait:
                time.sleep(wait)


class JobManager:
    """
    Job Manager.

    """

    def __init__(self):
        """Initialize Job Manager."""
        self._queue = deque()
        self._config_map = dict()

    def add_config(self, name, config, path=None, logfile=None, jobmap=None, **job_map_options):
        """Add Configuration to JobManager."""
        if path is None:
            try:
                path = config.path
            except AttributeError:
                pass
        if logfile is None:
            try:
                logfile = config.log
            except AttributeError:
                pass
        self[name] = ConfigRunner(config, path, logfile, value_or(jobmap, JobMap(**job_map_options)))
        return self[name]

    def __getitem__(self, name):
        """Get Configuration Runner."""
        return self._config_map[name]

    def __setitem__(self, name, value):
        """Set Configuration Runner."""
        self._config_map[name] = value
