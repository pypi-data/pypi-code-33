import os

"""
This module provides utility functions for working with files.
"""


class FileUtils:
    """
    This class provides utility functions for working with files.
    """
    def __init__(self):
        pass

    @staticmethod
    def get_file_name(file_path):
        """
         Given a file path, return the file name part.  <path to file>/<file name>

         :param file_path:  Full path to the file.  String value.
         :returns:  The file name.  String value.
         """
        tokens = os.path.split(file_path)
        if len(tokens) == 2:
            return tokens[1]
        elif len(tokens) == 1:
            return tokens[0]
        else:
            raise ValueError('Got an invalid file_path!')

    @staticmethod
    def get_file_dir(file_path):
        """
         Given a file path, return the path part.  <path to file>/<file name>
         :param file_path:  Full path tothe file.  String value.
         :returns:  The path name.  String value.
         """
        tokens = os.path.split(file_path)
        if len(tokens) == 2:
            return tokens[0]
        else:
            raise ValueError('file_path is a bare file name!')

    # Give us an normalized, absolute path to this file.
    @staticmethod
    def process_raw_file_path(raw_file_path):
        """
         Given a raw file path, give us an normalized, expanded full file path.
         :param raw_file_path:  Raw file path.  May just be the file name, could be a relative path,
                                or an absolute path.  Can have '~' chars, these should be expanded.
         :returns:  Normalized, expanded full file path.  String value.
         """
        return os.path.abspath(os.path.expanduser(raw_file_path))

    @staticmethod
    def create_output_dir(output_dir):
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        else:
            if not os.path.isdir(output_dir):
                raise ValueError('Expected a directory!')
