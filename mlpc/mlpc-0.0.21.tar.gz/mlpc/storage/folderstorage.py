import os
import time
from mlpc.metadata import Metadata
import mlpc.configuration
import glob


# TODO Move debug() calls to callers
class FolderStorage:
    def __init__(self, metadata):
        assert isinstance(metadata, Metadata)
        self._metadata = metadata
        self._check_if_folder_exists(mlpc.configuration.root_folder_path)
        self.run_path = self._create_folder_for_run_and_change_metadata()
        self.run_abs_path = os.path.abspath(self.run_path)
        self._paths_to_summarize = []

    def _create_folder_for_run_and_change_metadata(self):
        new_folder = self._metadata.run_path
        if os.path.exists(new_folder):
            time.sleep(1)
            self._metadata.update_timestamp()  # TODO Use .1 suffixes, this is easier to relate to for humans.
            return self._create_folder_for_run_and_change_metadata()
        else:
            os.mkdir(new_folder)
        return new_folder

    def get_filepath_for_writing(self, entity_type, file_name, file_type):
        folder_path = os.path.join(self.run_path, entity_type)
        self._create_folders_if_needed(folder_path)
        file_path = os.path.join(folder_path, file_name)
        file_path_with_number = self._get_unique_path(file_path, file_type)
        open(file_path_with_number, 'a').close()  # Create empty file to avoid collisions if writes are delayed
        self._paths_to_summarize.append(file_path_with_number)
        return file_path_with_number

    def get_folderpath_for_writing(self, entity_type, resource_name):
        folder_path = os.path.join(self.run_path, entity_type, resource_name)
        folder_path_with_number = self._get_unique_path(folder_path)
        self._create_folders_if_needed(folder_path_with_number)
        self._paths_to_summarize.append(folder_path_with_number)
        return folder_path_with_number

    def save_to_file(self, entity_type, resource_name, resource_content, file_type=None):
        file_path = self.get_filepath_for_writing(entity_type, resource_name, file_type)
        self._write_file(file_path, resource_content)
        self._paths_to_summarize.append(file_path)
        return file_path

    def get_num_files_and_bytes_of_resources_saved(self):
        num_files = 0
        files_bytes = 0
        for path_to_summarize in self._paths_to_summarize:
            paths = glob.glob(os.path.join(path_to_summarize, "**/*"), recursive=True)
            for path in paths:
                if os.path.isfile(path):
                    num_files += 1
                    files_bytes += os.path.getsize(path)
        return num_files, files_bytes

    @staticmethod
    def _write_file(file_path, content):
        with open(file_path, "w") as file:
            file.write(content)

    @staticmethod
    def _create_folders_if_needed(path):
        if not os.path.exists(path):
            os.makedirs(path)

    def _get_unique_path(self, path, file_type=None, suffix_number=1):
        path_with_number_and_file_type = \
            path + \
            "." + str(suffix_number) + \
            (("." + file_type) if len(file_type or "") > 0 else "")
        if os.path.exists(path_with_number_and_file_type):
            return self._get_unique_path(path, file_type, suffix_number=suffix_number + 1)
        return path_with_number_and_file_type

    @staticmethod
    def _check_if_folder_exists(path):
        abspath = os.path.abspath(path)
        if not os.path.isdir(abspath):
            raise ValueError("Folder does not exist: '" + abspath + "'. Set a valid root folder.")
