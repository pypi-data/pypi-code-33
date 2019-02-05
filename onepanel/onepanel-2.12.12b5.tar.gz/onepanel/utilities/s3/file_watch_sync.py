from watchdog.events import FileSystemEventHandler

from onepanel.utilities.s3.file_sync import FileDifference

class FileWatchSynchronizerEventHandler(FileSystemEventHandler):
    def __init__(self, path, remote_path, synchronizer, hook=None, skip_hidden=True):
        """

        :param path:
        :param remote_path:
        :param synchronizer:
        :type synchronizer onepanel.utilities.s3.file_sync.FileSynchronizer
        :param hook:
        """
        self.path = path
        self.path_length = len(path) + 1
        self.remote_path = remote_path
        self.hook = hook
        self.synchronizer = synchronizer
        self.skip_hidden = skip_hidden

    def on_created(self, event):
        if event.is_directory:
            return

        relative_path = event.src_path[self.path_length:]

        if self.should_skip(relative_path):
            return

        difference = FileDifference(event.src_path, self.remote_path + relative_path, FileDifference.State.NEW)
        self.synchronizer.synchronize_single(difference)
        self.call_hook(difference)

    def on_moved(self, event):
        if event.is_directory:
            return

        relative_path = event.src_path[self.path_length:]

        if self.should_skip(relative_path):
            return

        relative_destination = event.dest_path[self.path_length:]

        original_destination = self.remote_path + relative_path
        destination = self.remote_path + relative_destination

        difference = FileDifference(event.dest_path,
                                    destination,
                                    FileDifference.State.MOVED,
                                    event.src_path,
                                    original_destination)

        self.synchronizer.synchronize_single(difference)
        self.call_hook(difference)

    def on_deleted(self, event):
        if event.is_directory:
            return

        relative_path = event.src_path[self.path_length:]

        if self.should_skip(relative_path):
            return

        difference = FileDifference(event.src_path, self.remote_path + relative_path, FileDifference.State.DELETED)
        self.synchronizer.synchronize_single(difference)
        self.call_hook(difference)

    def on_modified(self, event):
        if event.is_directory:
            return

        relative_path = event.src_path[self.path_length:]

        if self.should_skip(relative_path):
            return

        difference = FileDifference(event.src_path, self.remote_path + relative_path, FileDifference.State.MODIFIED)
        self.synchronizer.synchronize_single(difference)
        self.call_hook(difference)

    def call_hook(self, file_difference):
        if self.hook is not None:
            self.hook(file_difference)

    def should_skip(self, relative_path):
        if self.skip_hidden and relative_path[0] == '.':
            return True

        return False


