

class FileMeta(object):
    def __init__(self, size, compression, checksum, file_name=None, file_url=None):

        """
        Initialize the FileMeta class.
        Only returned if the record is associated with a Large File.

        Parameters
        ----------
        file_name: str
            Name of the large file that was uploaded

        size: int
            Size of the encrypted file, in bytes, including E3DB Header information

        compression: str
            The type of compression the file is using, before encryption. Reserved for future use.

        checksum: str
            Base64 encoded MD5 Checksum of the Encrypted File, including E3DB Header information

        file_url: str
            Optional. Signed url used for PUT/GET to storage server


        Returns
        -------
        FileMeta
        """
        self._file_url = file_url
        self._file_name = file_name
        self._size = size
        self._compression = compression
        self._checksum = checksum

    def __remove_empty(self, serialize):
        """
        Parameters
        ----------
        serialize: dict
            Dictionary to remove empty elements from

        Returns
        -------
        dict
            Dictionary with empty elements removed
        """
        for key, value in list(serialize.items()):
            if isinstance(value, dict):
                self.__remove_empty(value)
            elif value is None or value == 'None':
                del serialize[key]
        return serialize

    def to_json(self):
        """
        Serialize the configuration as JSON-style object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            JSON-style document containing the FileMeta elements.
        """
        to_serialize = {
            'file_url': str(self._file_url),
            'file_name': str(self._file_name),
            'checksum': str(self._checksum),
            'compression': str(self._compression),
            'size': int(self._size) if self._size is not None else -1
        }
        return self.__remove_empty(to_serialize)

