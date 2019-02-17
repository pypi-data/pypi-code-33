from .plumbing.bindings import ffi, lib
from .plumbing.fs_interface_trampoline import file_system_interface
from .plumbing.ntstatus import cook_ntstatus


class WinFSPyError(Exception):
    pass


class FileSystemAlreadyStarted(WinFSPyERror):
    pass


class FileSystemNotStarted(WinFSPyERror):
    pass


class FileSystem:
    def __init__(
        self,
        mountpoint,
        operations,
        debug=False,
        **volume_params
    ):
        self.mountpoint = mountpoint
        self.operations = operations

        self._file_system_ptr = ffi.new("FSP_FILE_SYSTEM**")
        # Avoid GC on the handle
        self._operations_handle = ffi.new_handle(operations)
        self._file_system_ptr[0].UserContext = self._operations_handle

        volume_params = volume_params_factory(
            **volume_params,
        )
        result = lib.FspFileSystemCreate(
            lib.WFSPY_FSP_FSCTL_DISK_DEVICE_NAME, volume_params, file_system_interface, self._file_system_ptr
        )
        if not nt_success(result):
            raise WinFSPyError(f"Cannot create file system: {cook_ntstatus(result).name}")

        if debug:
            lib.FspFileSystemSetDebugLog(self._file_system_ptr, 1);

    def start(self):
        if self.started:
            raise FileSystemAlreadyStarted()
        self.started = True

        result = lib.FspFileSystemSetMountPoint(self._file_system_ptr[0], self.mountpoint)
        if not nt_success(result):
            raise WinFSPyError(f"Cannot mount file system: {cook_ntstatus(result).name}")
        lib.FspFileSystemStartDispatcher(self._file_system_ptr[0], 0)

    def stop(self):
        if not self.started:
            raise FileSystemNotStarted()
        self.started = False

        lib.FspFileSystemDelete(self._file_system_ptr[0])
