import os


class File(object):
    """
    File utility class.
    """

    def __init__(self):
        self.root_path = os.getenv("POC_BASE_ROOT", '')

    def get_shared_path(self, path: str = '') -> str:
        """
        Returns absolute path to `shared` directory.
        """
        return os.path.abspath(os.path.join(self.root_path, 'shared', path))

    def get_data_path(self, path: str = '') -> str:
        """
        Returns absolute path to `shared/data` directory.
        """
        return os.path.abspath(
            os.path.join(self.root_path, 'shared', 'data', path))

    def get_tmp_path(self, path: str = '') -> str:
        """
        Returns absolute path to `shared/tmp` directory.
        """
        return os.path.abspath(
            os.path.join(self.root_path, 'shared', 'tmp', path))
