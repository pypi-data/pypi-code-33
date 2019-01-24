
import enum


VOLCANO_DEFAULT_TCP_PORT = 8091
VOLCANO_PROTOCOL_VERSION_STR = '0.2'


class ValueType(enum.Enum):
    VT_VOID = 'void'
    VT_BOOL = 'bool'
    VT_INT = 'int'
    VT_FLOAT = 'float'
    VT_STR = 'str'

    VT_ALL_LIST = (VT_VOID, VT_BOOL, VT_INT, VT_FLOAT, VT_STR)

    # Используется для сериализации в строку. Предполагается, что в дальнейшем могут
    # быть использованы не только строки для типов - в коде не должно быть жесткой привязки
    def stringify(self) -> str:
        return self.value

    # !ValueError
    @staticmethod
    def parse(s: str) -> 'ValueType':
        return ValueType(s)


class Quality(enum.IntEnum):    # IntFlag appeared in 3.6; Debian stretch has Py 3.5.3
    QUALITY_GOOD = 0
    QUALITY_COMM = 1
    QUALITY_NOT_INIT = 2
    QUALITY_NA = 4
    QUALITY_NA_TEMP = 8
