
from volcano.general.stddef import ValueType


class Variant:
    vt_ = None
    value_ = None

    def vt(self) -> ValueType:  # pylint: disable=invalid-name
        return self.vt_

    def type_str(self) -> str:
        return self.vt_.stringify()

    def get_value(self):
        return self.value_

    # try set from given raw value. throw warning if conversion is required.
    def set_value_w(self, value) -> None:
        raise NotImplementedError()

    # None is not accepted
    def parse_value_w(self, s: str):    # pylint: disable=invalid-name
        raise NotImplementedError()

    def clone(self) -> 'Variant':
        raise NotImplementedError()

    # True if both not none & both not VOID & both have equal types
    def __eq__(self, x):
        if self.vt_ == x.vt_:
            v1 = self.get_value()
            v2 = x.get_value()

            return v1 is not None and v2 is not None and v1 == v2
        else:
            return False

    def __ne__(self, x):
        return not self.__eq__(x)

    def same_type(self, other: 'Variant'):
        assert isinstance(other, Variant), other

        return self.vt_ == other.vt_

    def __str__(self):
        return str(self.value_)

    def val_equal(self, value, none_eq_none: bool):
        my_val = self.value_

        if my_val is None and value is None:
            return none_eq_none

        return my_val == value  # None is not equal to 0/'' so no need to check if one argument is None

    def is_void(self) -> bool:
        return self.vt_ == ValueType.VT_VOID

    # asserts if types differ
    def copy_from_same_type(self, src: 'Variant'):
        assert isinstance(src, Variant), src
        assert self.vt_ == src.vt_, (self, src)

        self.value_ = src.value_

    @staticmethod
    def from_vt(vt: ValueType) -> 'Variant':
        if vt == ValueType.VT_VOID:
            return VOID_VALUE
        elif vt == ValueType.VT_BOOL:
            return BoolValue()
        elif vt == ValueType.VT_INT:
            return IntValue()
        elif vt == ValueType.VT_FLOAT:
            return FloatValue()
        else:
            assert vt == ValueType.VT_STR, vt
            return StrValue()

    # none is not supported
    @staticmethod
    def try_from_raw_value(value) -> ('Variant', None):
        if isinstance(value, bool):
            return BoolValue(value)
        if isinstance(value, int):
            return IntValue(value)
        if isinstance(value, float):
            return FloatValue(value)
        if isinstance(value, str):
            return StrValue(value)
        return None


class VoidValue(Variant):
    vt_ = ValueType.VT_VOID

    def clone(self):
        return self  # void value is immutable

    def set_value_w(self, value):
        raise Warning('VOID type cant set value: {}'.format(value))

    def parse_value_w(self, s: str):
        assert isinstance(s, str), s
        raise Warning('VOID type cant set value: {}'.format(s))


VOID_VALUE = VoidValue()


class BoolValue(Variant):
    vt_ = ValueType.VT_BOOL

    def __init__(self, value=None):
        if value is not None:
            self.set_value_w(value)

    def clone(self):
        rs = BoolValue()
        rs.value_ = self.value_  # this approach is faster than XXValue(self.value) coz we dont need to perform type checking
        return rs

    def set_value_w(self, value):
        if isinstance(value, bool):
            self.value_ = value
        elif value is None:
            self.value_ = None
        elif isinstance(value, int):
            if value == 1:
                self.value_ = True
            elif value == 0:
                self.value_ = False
            else:
                raise Warning('Value {} cannot be interpreted as bool'.format(value))
        else:
            raise Warning('Value {} cannot be interpreted as bool'.format(value))

    # none is not accepted
    def parse_value_w(self, s: str):
        assert isinstance(s, str), s
        if s == '1':
            self.value_ = True
        elif s == '0':
            self.value_ = False
        else:
            raise Warning('String "{}" cannot be parsed to bool. Use 1 and 0 values'.format(s))


class IntValue(Variant):
    vt_ = ValueType.VT_INT

    def __init__(self, value=None):
        if value is not None:
            self.set_value_w(value)

    def clone(self):
        rs = IntValue()
        rs.value_ = self.value_  # this approach is faster than XXValue(self.value) coz we dont need to perform type checking
        return rs

    def set_value_w(self, value):
        # in Python bool is subclass of int!
        if isinstance(value, bool):
            self.value_ = 1 if value else 0
        elif value is None or isinstance(value, int):
            self.value_ = value
        elif isinstance(value, float):
            if not value.is_integer():
                raise Warning('Value {} cannot be interpreted as int'.format(value))

            self.value_ = int(value)
        else:
            raise Warning('Value {} cannot be interpreted as int'.format(value))

    # none is not accepted
    def parse_value_w(self, s: str):
        assert isinstance(s, str), s
        try:
            self.value_ = int(s)
        except ValueError:
            raise Warning('Value {} cannot be interpreted as int'.format(s))


class FloatValue(Variant):
    vt_ = ValueType.VT_FLOAT

    def __init__(self, value=None):
        if value is not None:
            self.set_value_w(value)

    def clone(self):
        rs = FloatValue()
        rs.value_ = self.value_  # this approach is faster than XXValue(self.value) coz we dont need to perform type checking
        return rs

    def set_value_w(self, value):
        if value is None or isinstance(value, float):
            self.value_ = value
        elif isinstance(value, int):
            # here we also get bool!
            self.value_ = float(value)
        else:
            raise Warning('Value {} cannot be interpreted as float'.format(value))

    # none is not accepted
    def parse_value_w(self, s: str):
        assert isinstance(s, str), s
        try:
            self.value_ = float(s)
        except ValueError:
            raise Warning('Value {} cannot be interpreted as float'.format(s))


class StrValue(Variant):
    vt_ = ValueType.VT_STR

    def __init__(self, value=None):
        if value is not None:
            self.set_value_w(value)

    def clone(self):
        rs = StrValue()
        rs.value_ = self.value_  # this approach is faster than XXValue(self.value) coz we dont need to perform type checking
        return rs

    def set_value_w(self, value):
        if value is None or isinstance(value, str):
            self.value_ = value
        else:
            raise Warning('Value {} cannot be interpreted as str'.format(value))

    # none is not accepted
    def parse_value_w(self, s: str):
        assert isinstance(s, str), s
        self.value_ = s
