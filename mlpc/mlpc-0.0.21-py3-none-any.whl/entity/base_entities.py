from mlpc.storage.folderstorage import FolderStorage


class BaseEntity:
    def __init__(self, storage):
        assert isinstance(storage, FolderStorage)
        self._storage = storage


class BaseEntityWithRegularStorage(BaseEntity):
    def __init__(self, storage, entity_type):
        super().__init__(storage)
        self._entity_type = entity_type

    def get_folderpath_for_writing(self, folder_name):
        return self._storage.get_folderpath_for_writing(self._entity_type, folder_name)

    def get_filepath_for_writing(self, file_name, file_type=None):
        return self._storage.get_filepath_for_writing(self._entity_type, file_name, file_type)

    def save(self, file_name, data, file_type=None):
        return self._storage.save_to_file(self._entity_type, file_name, data, file_type)
