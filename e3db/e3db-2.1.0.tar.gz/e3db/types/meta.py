from datetime import datetime
from .file_meta import FileMeta
import uuid


class Meta():

    def __init__(self, json):
        """
        Initialize the Meta class.

        If certain keys, such as record_id, created, last_modified, and version
        are not missing (such as when a record is created, but these variables
        have not been set by the server yet).

        Parameters
        ----------
        json : dict
            JSON key-value store of Meta data configuration.

        Returns
        -------
        None
        """
        # required
        self.__writer_id = uuid.UUID(json['writer_id'])
        self.__user_id = uuid.UUID(json['user_id'])
        self.__record_type = str(json['type'])
        self.__plain = json['plain'] if 'plain' in json else {}
        # optional, as some get set by the server
        # set these to None if they are not included when init is called.
        # self.record_id = json['record_id'] if 'record_id' in json else None
        if 'record_id' in json:
            if json['record_id'] is not None and json['record_id'] != str(None):
                self.__record_id = uuid.UUID(json['record_id'])
            else:
                self.__record_id = json['record_id']
        else:
            self.__record_id = str(None)

        # When "printing" the timestamp (or converting to str), the T and Z characters are removed
        # Therefore, we need to parse both formats.
        try:
            self.__created = datetime.strptime(json['created'], '%Y-%m-%dT%H:%M:%S.%fZ') if 'created' in json else None
        except ValueError:
            self.__created = datetime.strptime(json['created'], '%Y-%m-%d %H:%M:%S.%f') if 'created' in json else None
        try:
            self.__last_modified = datetime.strptime(json['last_modified'], '%Y-%m-%dT%H:%M:%S.%fZ') if 'last_modified' in json else None
        except ValueError:
            self.__last_modified = datetime.strptime(json['last_modified'], '%Y-%m-%d %H:%M:%S.%f') if 'last_modified' in json else None

        self.__version = json['version'] if 'version' in json else None

        self.__file_meta = None
        if json.get('file_meta') is not None:
            self.__file_meta = FileMeta(checksum=json['file_meta'].get('checksum'), 
                                compression=json['file_meta'].get('compression'),
                                size=int(json['file_meta'].get('size', "-1")), 
                                file_url=json['file_meta'].get('file_url'),
                                file_name=json['file_meta'].get('file_name')
                                )

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
            record type
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
        str
            record type
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
            plaintext metadata
        """
        return self.__plain

    @plain.setter
    def plain(self, value):
        """
        Set plaintext metadata

        Parameters
        ----------
        value : dict
            plaintext metadata

        Returns
        -------
        str
            record type
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
            record_id
        """
        return self.__record_id

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

    # file_meta getter
    @property
    def file_meta(self):
        """
        Get file_meta of record if it exists
        
        Returns
        -------
        File
            File meta information returned when a record was uploaded with Large Files or None
        """
        return self.__file_meta

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
            'record_id': str(self.__record_id),
            'writer_id': str(self.__writer_id),
            'user_id': str(self.__user_id),
            'type': str(self.__record_type),
            'plain': self.__plain,
            'created': str(self.__created),
            'last_modified': str(self.__last_modified),
            'version': str(self.__version),
            'file_meta': None if self.__file_meta is None else self.__file_meta.to_json()
        }

        # remove None (JSON null) objects
        for key, value in list(to_serialize.items()):
            if value is None or value == 'None':
                del to_serialize[key]

        return to_serialize
