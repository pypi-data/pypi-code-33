from hippodamia.enums import Health


class Properties:
    _logger = None

    _gid = None
    _necessity = None
    _type = None
    _name = None
    _location = None
    _room = None
    _device = None

    uuid = None
    onboarding_topic = None
    protocol_version = None
    version = None
    description = None
    host_name = None
    node_id = None
    ips = None
    config_hash = None
    health = None

    def __init__(self, logger):
        self._logger = logger

    def export_dict(self):
        try:
            health = self.health.name
        except AttributeError:
            health = None
        try:
            necessity = self.necessity.name
        except AttributeError:
            necessity = None

        result = {
            "gid": self.gid,
            "health": health,
            "necessity": necessity,
            "uuid": self.uuid,
            "onboarding_topic": self.onboarding_topic,
            "protocol_version": self.protocol_version,
            "type": self.type,
            "version": self.version,
            "name": self.name,
            "location": self.location,
            "room": self.room,
            "device": self.device,
            "description": self.description,
            "host_name": self.host_name,
            "node_id": self.node_id,
            "ips": self.ips,
            "config_hash": self.config_hash
        }
        return result

    def _set_necessity(self, necessity):
        if self._necessity is None:
            self._necessity = necessity
        elif self._necessity != necessity:
            msg = "set_necessity() is called with different value ({}) than the existing one ({})".format(necessity, self._necessity)
            self._logger.warning(msg)
            raise ValueError(msg)

    def _get_necessity(self):
        return self._necessity

    necessity = property(_get_necessity, _set_necessity)

    def _set_gid(self, gid):
        if self._gid is None:
            self._gid = str(gid)
        elif self._gid != str(gid):
            msg = "set_gid() is called with different value ({}) than the existing one ({})".format(gid, self._gid)
            self._logger.warning(msg)
            raise ValueError(msg)

    def _get_gid(self):
        return self._gid

    gid = property(_get_gid, _set_gid)
    
    def _set_type(self, type):
        if self._type is None:
            self._type = type
        elif self._type != type:
            msg = "set_type() is called with different value ({}) than the existing one ({})".format(type, self._type)
            self._logger.warning(msg)
            raise ValueError(msg)

    def _get_type(self):
        return self._type

    type = property(_get_type, _set_type)

    def _set_name(self, name):
        if self._name is None:
            self._name = name
        elif self._name != name:
            msg = "set_name() is called with different value ({}) than the existing one ({})".format(name, self._name)
            self._logger.warning(msg)
            raise ValueError(msg)

    def _get_name(self):
        return self._name

    name = property(_get_name, _set_name)
    
    def _set_location(self, location):
        if self._location is None:
            self._location = location
        elif self._location != location:
            msg = "set_location() is called with different value ({}) than the existing one ({})".format(location, self._location)
            self._logger.warning(msg)
            raise ValueError(msg)

    def _get_location(self):
        return self._location

    location = property(_get_location, _set_location)
    
    def _set_room(self, room):
        if self._room is None:
            self._room = room
        elif self._room != room:
            msg = "set_room() is called with different value ({}) than the existing one ({})".format(room, self._room)
            self._logger.warning(msg)
            raise ValueError(msg)

    def _get_room(self):
        return self._room

    room = property(_get_room, _set_room)

    def _set_device(self, device):
        if self._device is None:
            self._device = device
        elif self._device != device:
            msg = "set_device() is called with different value ({}) than the existing one ({})".format(device, self._device)
            self._logger.warning(msg)
            raise ValueError(msg)

    def _get_device(self):
        return self._device

    device = property(_get_device, _set_device)

