import logging
import datetime


class Cache:
    def __init__(self, default_duration: datetime.timedelta = datetime.timedelta(minutes = 5)):
        if not hasattr(self, 'log'):
            self.log = logging.getLogger(__name__)
        self.log.debug('Initialization complete')

        if default_duration is None:
            self._default_duration: datetime.timedelta = datetime.timedelta(minutes=5)
        else:
            self._default_duration: datetime.timedelta = default_duration

        self._cache = {}

    def get(self, id) -> any:
        if self.has(id):
            if not self.expired(id):
                return self._cache[id]['VALUE']
        return False

    def set(self, id, value, duration: datetime.timedelta = None, overwrite: bool = False):
        if not duration:
            duration = self._default_duration

        if not overwrite and not self.has(id):
            self._cache[id] = {'VALUE': value, 'EXPIRES': datetime.datetime.now() + duration}
            return True
        return False

    def has(self, id) -> bool:
        return id in self._cache

    def expired(self, id) -> bool:
        return not self.has(id) or self._cache[id]['EXPIRES'] < datetime.datetime.now()
