import fcntl
import os


class LockManager(object):

    STATUS_SERVER_STATUS = "SERVER-STATUS"

    @staticmethod
    def verify_lock_file(LOCKFILE_name):
        LOCKFILE_name = "%scvmfs_scheduler_lock" % LOCKFILE_name
        return not os.path.exists(LOCKFILE_name)

    def __init__(self, LOCKFILE_name, pid, force_lock=False):
        self.LOCKFILE_name = LOCKFILE_name
        self.pid = pid
        self.STATUS_SERVER_STATUS = "%s-%s" % (self.STATUS_SERVER_STATUS,
                                               self.pid)
        self.force_lock = force_lock
        self.other_is_running = None

    def __enter__(self):
        """
        Try to get the lock file or exit if other process has the lock
        """
        self.lock_file = "%scvmfs_scheduler_lock" % self.LOCKFILE_name
        current_process = None

        # Block other processes in getLock state
        lock_file_descriptor = None
        try:

            lock_file_descriptor = open(self.lock_file, 'a+')

            # temporary lock the file for reading
            fcntl.flock(lock_file_descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            lock_file_descriptor.seek(0, 0)
            val = lock_file_descriptor.readline()
            if val != "":
                current_process = val

            if not current_process:
                self.other_is_running = False
            else:
                # look up process if exists
                try:
                    open(os.path.join('/proc', current_process,
                                      'cmdline'), 'rb').read()
                    self.other_is_running = True
                except IOError:  # proc has already terminated
                    self.other_is_running = False
            if not self.other_is_running or self.force_lock:
                if self.force_lock:
                    self.other_is_running = False
                lock_file_descriptor.seek(0, 0)
                lock_file_descriptor.truncate()
                lock_file_descriptor.write("%s" % self.pid)
                lock_file_descriptor.truncate()
            else:
                raise RuntimeError(
                    "Process %s is still running" % current_process)
        except (IOError, RuntimeError) as e:
            raise
        finally:
            if lock_file_descriptor:
                fcntl.flock(lock_file_descriptor, fcntl.LOCK_UN)
                lock_file_descriptor.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Remove lock
        """
        if self.other_is_running:
            return True
        try:
            lock_file_descriptor = open(self.lock_file, 'r')
            fcntl.flock(lock_file_descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            val = lock_file_descriptor.readline()
            fcntl.flock(lock_file_descriptor, fcntl.LOCK_UN)
            # Remove only if the current process has not had
            # lock was "stolen" by an admin process
            if val == str(self.pid):
                os.remove(self.lock_file)
            return True
        except:
            return False


