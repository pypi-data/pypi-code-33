class QalxEntity(dict):
    entity_type: str

    def __init__(self, pyqalxapi_dict):
        """Base class for qalx entities_response.

        QalxEntity children need to be populated with either a `requests.models.Response` which is the type returned
        by the methods on `pyqalxapi.api.PyQalxAPI` or with a `dict`.

        Entities will behave exactly like a `dict`. For example:

        >>> class AnEntity(QalxEntity):
        ...     pass
        >>> c = AnEntity({"guid":"123456789", "info":{"some":"info"}})
        >>> c['guid']
        '123456789'

        :param pyqalxapi_dict: a 'dict' representing a qalx entity object to populate the entity
        :type pyqalxapi_dict: dict
        """

        super().__init__(pyqalxapi_dict)

    # TODO: tricky for nested dicts
    #     self._dirty_keys = []
    #
    # def __setitem__(self, key, value):
    #     self._dirty_keys.append(key)
    #
    # @property
    # def keys_to_save(self):
    #     return {k: self[k] for k in self._dirty_keys}
    #
    # @property
    # def is_dirty(self):
    #     return self._dirty_keys is not []

    def __str__(self):
        return f"[{self.entity_name}] {self['guid']}"
