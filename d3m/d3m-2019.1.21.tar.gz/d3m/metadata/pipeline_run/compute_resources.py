import logging
import os
import re
import traceback
import typing

import GPUtil  # type: ignore

from d3m.environment_variables import D3M_CPU, D3M_RAM

__all__ = ('CPUResources', 'MemoryResources', 'GPUResources', 'ComputeResources')

logger = logging.getLogger(__name__)

PROC_INFO_RE = re.compile(r'^([^:]+?)\s*:\s*(.*)$')
PROC_MEMORY_PATH = '/proc/meminfo'
PROC_TOTAL_MEMORY_KEY = 'MemTotal'
CGROUP_MEMORY_LIMIT_PATH = '/sys/fs/cgroup/memory/memory.limit_in_bytes'
CGROUP_CPU_SHARES_PATH = '/sys/fs/cgroup/cpu/cpu.shares'


# TODO: Move these methods to utils?
def _get_configured_available(environment_variable: str) -> typing.Optional[int]:
    configured_available = None
    is_d3m_limited = environment_variable in os.environ
    if is_d3m_limited:
        configured_available = int(os.environ[environment_variable])
    return configured_available


def _get_cgroup_cpu_shares() -> typing.Optional[float]:
    cpu_shares = None
    with open(CGROUP_CPU_SHARES_PATH) as fp:
        for line in fp:
            line = line.strip()
            cpu_shares = int(line)
            is_limited_memory = cpu_shares < 1e5
            if is_limited_memory:
                cpu_shares = cpu_shares
            break
    return cpu_shares


def _get_proc_meminfo() -> typing.Optional[int]:
    total_memory_bytes = None
    with open(PROC_MEMORY_PATH) as fp:
        for line in fp:
            line = line.strip()
            match = PROC_INFO_RE.match(line)
            if match is None:
                raise ValueError("Error parsing /proc/meminfo")
            key, value = match.groups()
            if key == PROC_TOTAL_MEMORY_KEY:
                total_memory_kb = int(value.split()[0])
                total_memory_bytes = total_memory_kb * 1024
    return total_memory_bytes


def _get_cgroup_memory_limit() -> typing.Optional[int]:
    mem_cgroup_limit = None
    with open(CGROUP_MEMORY_LIMIT_PATH) as fp:
        for line in fp:
            line = line.strip()
            mem_bytes = int(line)
            # TODO: Use highest positive signed 64-bit integer rounded down to multiples of the page size on the system instead of 9e15.
            is_limited_memory = mem_bytes < 9e15
            if is_limited_memory:
                mem_cgroup_limit = mem_bytes
            break
    return mem_cgroup_limit


class CPUResources:
    def __init__(
        self, *, devices: typing.Optional[typing.Sequence[str]] = None,
        physical_present: int = None, logical_present: int = None, configured_available: int = None,
        constraints: typing.Dict = None
    ) -> None:
        self._cpus: typing.Optional[typing.List] = None

        self.devices = devices
        if self.devices is None:
            self.devices = self._get_devices()

        self.physical_present = physical_present
        if self.physical_present is None:
            self.physical_present = self._get_physical_present()

        self.logical_present = logical_present
        if self.logical_present is None:
            self.logical_present = self._get_logical_present()

        self.configured_available = configured_available
        if self.configured_available is None:
            self.configured_available = _get_configured_available(D3M_CPU)

        self.constraints = constraints
        if self.constraints is None:
            self.constraints = self._get_constraints()

    def to_json_structure(self) -> typing.Optional[typing.Dict]:
        json_structure: typing.Dict[str, typing.Any] = {}

        if self.devices is not None:
            json_structure['devices'] = [{'name': name} for name in self.devices]

        if self.physical_present is not None:
            json_structure['physical_present'] = self.physical_present

        if self.logical_present is not None:
            json_structure['logical_present'] = self.logical_present

        if self.configured_available is not None:
            json_structure['configured_available'] = self.configured_available

        if self.constraints is not None:
            json_structure['constraints'] = self.constraints

        if json_structure:  # not empty
            return json_structure
        else:
            return None

    def _get_cpus(self) -> typing.Sequence[dict]:
        if self._cpus is None:
            cores = os.sched_getaffinity(0)
            self._cpus = []
            with open('/proc/cpuinfo') as fp:
                cpu: typing.Dict = {}
                for line in fp:
                    line = line.strip()
                    if not line:
                        if cpu and int(cpu['processor']) in cores:
                            self._cpus.append(cpu)
                            cpu = {}
                    else:
                        match = PROC_INFO_RE.match(line)
                        if match is None:
                            raise ValueError("Error parsing /proc/cpuinfo")
                        cpu[match.group(1)] = match.group(2)
        return self._cpus

    def _get_devices(self) -> typing.Optional[typing.Sequence[str]]:
        devices: typing.Optional[typing.List[str]] = None
        try:
            cpus = self._get_cpus()
            devices = list(set([cpu['model name'] for cpu in cpus]))  # TODO: is it possible to have multiple with the same model name?
        except Exception as error:
            logger.warning('Failed to get CPU information.', exc_info=error)
        return devices

    def _get_physical_present(self) -> typing.Optional[int]:
        num_physical_cores: typing.Optional[int] = None
        try:
            cpus = self._get_cpus()
            num_physical_cores = self._get_num_physical_cores()
        except Exception as error:
            logger.warning('Failed to get CPU information.', exc_info=error)
        return num_physical_cores

    def _get_logical_present(self) -> typing.Optional[int]:
        num_logical_present: typing.Optional[int] = None
        try:
            cpus = self._get_cpus()
            num_logical_present = len(cpus)
        except Exception as error:
            logger.warning('Failed to get CPU information.', exc_info=error)
        return num_logical_present

    def _get_constraints(self) -> typing.Optional[typing.Dict]:
        constraints: typing.Optional[typing.Dict] = None
        try:
            constraints = {
                'cpu_shares': _get_cgroup_cpu_shares()
            }
        except Exception as error:
            logger.warning('Failed to get CPU information.', exc_info=error)
        return constraints

    def _get_num_physical_cores(self) -> int:
        physical_ids: typing.List = []
        num_physical_cores = 0
        for cpu in self._cpus:
            physical_id = cpu['physical id']
            if physical_id in physical_ids:
                continue
            physical_ids.append(physical_id)
            num_physical_cores += int(cpu['cpu cores'])
        return num_physical_cores


class MemoryResources:
    def __init__(
        self, *, devices: typing.Sequence[typing.Dict[str, str]] = None, total_memory: int = None,
        configured_memory: int = None, constraints: typing.Dict = None
    ) -> None:
        self.devices = devices
        # if self.devices is None:
        #     self.devices = self._get_devices()  # todo

        self.total_memory = total_memory
        if self.total_memory is None:
            self.total_memory = self._get_total_memory()

        self.configured_memory = configured_memory
        if self.configured_memory is None:
            self.configured_memory = self._get_configured_memory()

        self.constraints = constraints
        if self.constraints is None:
            self.constraints = self._get_constraints()

    def to_json_structure(self) -> typing.Optional[typing.Dict[str, typing.Any]]:
        json_structure: typing.Dict[str, typing.Any] = {}

        if self.devices is not None:
            json_structure['devices'] = [{'name': name} for name in self.devices]

        if self.total_memory is not None:
            json_structure['total_memory'] = self.total_memory

        if self.configured_memory is not None:
            json_structure['configured_memory'] = self.configured_memory

        if self.constraints is not None:
            json_structure['constraints'] = self.constraints

        if json_structure:  # not empty
            return json_structure
        else:
            return None

    # def _get_devices(self) -> None:
    #     # TODO: Consider lshw.
    #     return None

    def _get_total_memory(self) -> typing.Optional[int]:
        total_memory: typing.Optional[int] = None
        try:
            total_memory = _get_proc_meminfo()
        except Exception as error:
            logger.warning('Failed to get memory information.', exc_info=error)
        return total_memory

    def _get_configured_memory(self) -> typing.Optional[int]:
        return _get_configured_available(D3M_RAM)

    def _get_constraints(self) -> typing.Optional[typing.Dict]:
        constraints: typing.Optional[typing.Dict] = None
        try:
            memory_limit = _get_cgroup_memory_limit()
            if memory_limit is not None:
                constraints = {
                    'memory_limit': memory_limit
                }
        except FileNotFoundError as error:
            logger.warning('Failed to get memory information.', exc_info=error)
        return constraints


class GPUResources:
    def __init__(
        self, *, devices: typing.Sequence = None, total_memory: int = None,
        configured_memory: int = None, constraints: typing.Dict = None
    ) -> None:
        self._gpus: typing.List[GPUtil.GPU] = None

        self.devices = devices
        # if self.devices is None:
        #     self.devices = self._get_devices()  # TODO

        self.total_memory = total_memory
        # If there are no devices, no point in computing total memory.
        if self.total_memory is None and self.devices:
            self.total_memory = self._get_total_memory()

        self.configured_memory = configured_memory
        # If there are no devices, no point in computing total memory.
        if self.configured_memory is None and self.devices:
            self.configured_memory = self._get_configured_memory()

        self.constraints = constraints
        # if self.constraints is None:
        #     self.constraints = self._get_constraints()  # TODO

    def to_json_structure(self) -> typing.Optional[typing.Dict[str, typing.Any]]:
        json_structure: typing.Dict[str, typing.Any] = {}

        if self.devices is not None:
            json_structure['devices'] = self.devices

        if self.total_memory is not None:
            json_structure['total_memory'] = self.total_memory

        if self.configured_memory is not None:
            json_structure['configured_memory'] = self.configured_memory

        if self.constraints is not None:
            json_structure['constraints'] = self.constraints

        if json_structure:  # not empty
            return json_structure
        else:
            return None

    def _get_gpus(self) -> typing.Optional[typing.Sequence[GPUtil.GPU]]:
        if self._gpus is None:
            self._gpus = GPUtil.getGPUs()
        return self._gpus

    # def _get_devices(self) -> None:
    #     # TODO: Consider lshw.
    #     return None

    def _get_total_memory(self) -> typing.Optional[int]:
        total_memory_bytes: typing.Optional[int] = None
        try:
            total_memory_mib = sum(gpu.memoryTotal for gpu in self._get_gpus())
            total_memory_bytes = int(total_memory_mib) * 2**20
        except FileNotFoundError as error:
            logger.warning('Failed to get GPU information.', exc_info=error)
        return total_memory_bytes

    def _get_configured_memory(self) -> typing.Optional[int]:
        # There is currently no limit on GPU memory through configuration.
        return self._get_total_memory()

    # def _get_constraints(self) -> None:  # TODO
    #     return None


class ComputeResources:
    def __init__(
        self, *, cpu: CPUResources = None, memory: MemoryResources = None,
        gpu: GPUResources = None
    ) -> None:
        self.cpu = cpu
        if self.cpu is None:
            self.cpu = CPUResources()

        self.memory = memory
        if self.memory is None:
            self.memory = MemoryResources()

        self.gpu = gpu
        if self.gpu is None:
            self.gpu = GPUResources()

    def to_json_structure(self) -> typing.Optional[typing.Dict[str, typing.Any]]:
        json_structure: typing.Dict[str, typing.Any] = {}

        if self.cpu is not None:
            cpu_json_structure = self.cpu.to_json_structure()
            if cpu_json_structure is not None:
                json_structure['cpu'] = cpu_json_structure

        if self.memory is not None:
            memory_json_structure = self.memory.to_json_structure()
            if memory_json_structure is not None:
                json_structure['memory'] = memory_json_structure

        if self.gpu is not None:
            gpu_json_structure = self.gpu.to_json_structure()
            if gpu_json_structure is not None:
                json_structure['gpu'] = gpu_json_structure

        if json_structure:  # not empty
            return json_structure
        else:
            return None
