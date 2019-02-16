from common.schematizer.exceptions import SimpleValidationError


class Base:
    def to_native(self, obj):
        raise NotImplementedError

    def to_primitive(self, obj):
        raise NotImplementedError


class BaseCoercible(Base):
    def coerce_primitive(self, obj):
        raise NotImplementedError

    def coerce_native(self, obj):
        raise NotImplementedError

    def to_native(self, obj):
        try:
            return self.coerce_primitive(obj)
        except (TypeError, ValueError) as exc:
            raise SimpleValidationError('UNMARSHABLE', extra={'message': str(exc)}) from exc

    def to_primitive(self, obj):
        return self.coerce_native(obj)
