
class TelegramType(object):
    FIELDS = dict()
    REQUIRED = set()

    def __init__(self, obj: dict):
        self._populated_fields = set()
        for field, ctor in self.FIELDS.items():
            val = obj.get(field)
            name = field

            if isinstance(ctor, tuple):
                name = ctor[0]
                ctor = ctor[1]
            
            if val is not None:
                val = ctor(val)
                if field not in self.REQUIRED:
                    self._populated_fields.add(name)
            else:
                assert field not in self.REQUIRED, 'missing required field "{0}".'.format(field)
            
            self.__setattr__(name, val)
