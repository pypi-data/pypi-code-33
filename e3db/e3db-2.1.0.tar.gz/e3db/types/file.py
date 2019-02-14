from datetime import datetime
import uuid


class File():

    def __init__(self, checksum, compression, size, writer_id, user_id,
                record_type, file_url=None, file_name=None, record_id=None,
                created=None, last_modified=None, version=None, plain={}):
        """
        Initialize the e3db.File class.

        Parameters
        ----------
        checksum: str
            Base64 encoded MD5 Checksum of the Encrypted File, including E3DB Header information

        compression: str
            The type of compression the file is using, before encryption. Reserved for future use.

        size: int
            Size of the encrypted file, in bytes, including E3DB Header information

        writer_id: str
            Writer id of the File

        user_id: str
            User id of the File

        record_type: str
            Type of the Record

        file_url: str
            Optional. Signed url used for PUT/GET to storage server

        file_name: str
            Optional. Name of the file stored on the server. File name consists of UUID + timestamp. Returned by the server after the file has been uploaded.

        record_id: str
            Optional. ID of the Record in a UUID format. Returned by the server after the file has been uploaded.

        created: str
            Optional. Created timestamp of the file, returned by the server after the file has been uploaded.

        last_modified: str
            Optional. Last Modified timestamp of the file, returned by the server after the file has been uploaded.

        version: str
            Optional. The version of the file based on File structure and cryptographic methods.

        plain: dict
            Optional. Plaintext metadata attached to the File.

        Returns
        -------
        None
        """
        # required parameters
        # Data always empty dict, since data is stored on separate storage server
        self.__data = {}
        self.__writer_id = writer_id
        self.__user_id = user_id
        self.__record_type = str(record_type)
        self.__checksum = str(checksum)
        self.__compression = str(compression)
        self.__size = int(size)
        # optional, as some get set by the server
        # set these to None if they are not included when init is called.
        if record_id is not None and not isinstance(record_id, uuid.UUID):
            self.__record_id = uuid.UUID(record_id)
        else:
            self.__record_id = None
        # Have to check if specified or else we may end up with the string 'None'
        # >>> str(None)
        # 'None'
        self.__file_url = str(file_url) if file_url is not None else None
        self.__file_name = str(file_name) if file_name is not None else None

        # When "printing" the timestamp (or converting to str), the T and Z characters are removed
        # Therefore, we need to parse both formats.
        try:
            self.__created = datetime.strptime(created, '%Y-%m-%dT%H:%M:%S.%fZ') if created is not None else None
        except ValueError:
            self.__created = datetime.strptime(created, '%Y-%m-%d %H:%M:%S.%f') if created is not None else None
        try:
            self.__last_modified = datetime.strptime(last_modified, '%Y-%m-%dT%H:%M:%S.%fZ') if last_modified is not None else None
        except ValueError:
            self.__last_modified = datetime.strptime(last_modified, '%Y-%m-%d %H:%M:%S.%f') if last_modified is not None else None

        self.__version = str(version) if version is not None else None
        self.__plain = plain

    # writer_id getters and setters
    @property
    def writer_id(self):
        """
        Get writer_id

        Parameters
        ----------
        None

        Returns
        -------
        uuid.UUID
            writer_id
        """
        return self.__writer_id

    @writer_id.setter
    def writer_id(self, value):
        """
        Set writer_id

        Parameters
        ----------
        value : uuid.UUID
            writer id

        Returns
        -------
        None
        """
        self.__writer_id = value

    # user_id getters and setters
    @property
    def user_id(self):
        """
        Get user_id

        Parameters
        ----------
        None

        Returns
        -------
        uuid.UUID
            user_id
        """
        return self.__user_id

    @user_id.setter
    def user_id(self, value):
        """
        Set user_id

        Parameters
        ----------
        value : uuid.UUID
            user_id

        Returns
        -------
        None
        """
        self.__user_id = value

    # record_type getters and setters
    @property
    def record_type(self):
        """
        Get record_type

        Parameters
        ----------
        None

        Returns
        -------
        str
            Type of the Record
        """
        return self.__record_type

    @record_type.setter
    def record_type(self, value):
        """
        Set record_type

        Parameters
        ----------
        value : str
            record_type

        Returns
        -------
        None
        """
        self.__record_type = value

    # plain getters and setters
    @property
    def plain(self):
        """
        Get plaintext metadata

        Parameters
        ----------
        None

        Returns
        -------
        dict
            Plaintext metadata attached to the File.
        """
        return self.__plain

    @plain.setter
    def plain(self, value):
        """
        Set plaintext metadata

        Parameters
        ----------
        value : dict
            Plaintext metadata attached to the File.

        Returns
        -------
        None
        """
        self.__plain = value

    # record_id getters
    @property
    def record_id(self):
        """
        Get record_id

        Parameters
        ----------
        None

        Returns
        -------
        uuid.UUID
            ID of the Record in a UUID format.
        """
        return self.__record_id

    @record_id.setter
    def record_id(self, value):
        """
        Set record_id

        Parameters
        ----------
        value : str
            ID of the Record

        Returns
        -------
        None
        """
        self.__record_id = uuid.UUID(value)

    # created getters
    @property
    def created(self):
        """
        Get created time of record.

        Parameters
        ----------
        None

        Returns
        -------
        datetime
            Time record was created.
        """
        return self.__created

    # last_modified getters
    @property
    def last_modified(self):
        """
        Get last_modified time of record.

        Parameters
        ----------
        None

        Returns
        -------
        datetime
            Time record was last_modified.
        """
        return self.__last_modified

    # version getters
    @property
    def version(self):
        """
        Get version of record.

        Parameters
        ----------
        None

        Returns
        -------
        str
            version of the record type
        """
        return self.__version

    # checksum getters
    @property
    def checksum(self):
        """
        Get checksum

        Parameters
        ----------
        None

        Returns
        -------
        str
            Base64 encoded MD5 Checksum of the Encrypted File, including E3DB Header information
        """
        return self.__checksum

    # compression getters
    @property
    def compression(self):
        """
        Get compression

        Parameters
        ----------
        None

        Returns
        -------
        str
            The type of compression the file is using, before encryption. Reserved for future use.
        """
        return self.__compression

    # size getters
    @property
    def size(self):
        """
        Get size of file in bytes

        Parameters
        ----------
        None

        Returns
        -------
        int
            Size of the encrypted file, in bytes, including E3DB Header information
        """
        return self.__compression

    # file_url getters and setters
    @property
    def file_url(self):
        """
        Get file_url

        Parameters
        ----------
        None

        Returns
        -------
        str
            Signed url used for PUT/GET to storage server
        """
        return self.__file_url

    @file_url.setter
    def file_url(self, value):
        """
        Set file_url

        Parameters
        ----------
        value : str
            Signed url used for PUT/GET to storage server

        Returns
        -------
        None
        """
        self.__file_url = str(value)

    # file_name getters and setters
    @property
    def file_name(self):
        """
        Get file_name

        Parameters
        ----------
        None

        Returns
        -------
        str
            Name of the file stored on the server. File name consists of UUID + timestamp.
        """
        return self.__file_name

    @file_name.setter
    def file_name(self, value):
        """
        Set file_name

        Parameters
        ----------
        value : str
            Name of the file stored on the server. File name consists of UUID + timestamp.

        Returns
        -------
        None
        """
        self.__file_name = str(value)

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
            JSON-style document containing the Meta elements.
        """

        to_serialize = {
            'meta': {
                'record_id': str(self.__record_id),
                'writer_id': str(self.__writer_id),
                'user_id': str(self.__user_id),
                'type': str(self.__record_type),
                'created': str(self.__created),
                'last_modified': str(self.__last_modified),
                'version': str(self.__version),
                'file_meta': {
                    'file_url': str(self.__file_url),
                    'file_name': str(self.__file_name),
                    'checksum': str(self.__checksum),
                    'compression': str(self.__compression),
                    'size': int(self.__size)
                },
                'plain': self.__plain,
            },
            'data': self.__data,
        }

        # remove None (JSON null) objects
        return self.__remove_empty(to_serialize)
