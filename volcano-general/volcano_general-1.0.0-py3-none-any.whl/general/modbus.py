import enum
from . import stdint


'''
    раньше было 270, но я лично видел ответы на 100 функцию длиной 275
    байт (rtu + crc)
    Данное значение не дб точным, оно дб НЕ МЕНЬШЕ реального.
    Оно используется для выделения буферов.
    At this moment longest is request to write words:
    Slave(1),Fn(1),Addr(2),NbWords(2),NbBytes(1),DATA,Crc(2)
    Data can be up to 254bytes - cause NbBytes(1) field
    Total is 254+9 = 263 bytes
    Данная длина покрывает максимальный запрос + CRC + TCP Header, то есть по
    большому счету - несуществующий запрос
    (и crc, и tcp). Но в некоторых программах это испольуется (буфер один на rtu
    и tcp)
'''     # pylint: disable=pointless-string-statement

MAX_FRAME_SIZE_BYTES = 306
MAX_READ_WORDS_NB = 127
MAX_WRITE_WORDS_NB = 127
MAX_READ_BITS_NB = 2000  # See JBus_Modbus.pdf page 40
MAX_WRITE_BITS_NB = 1968  # See JBus_Modbus.pdf page 44

MB_FN_READ_OUT_BITS_1 = 1
MB_FN_READ_IN_BITS_2 = 2
MB_FN_READ_OUT_WORDS_3 = 3
MB_FN_READ_IN_WORDS_4 = 4
MB_FN_WRITE_BIT_5 = 5
MB_FN_WRITE_WORD_6 = 6
MB_FN_WRITE_BITS_15 = 15
MB_FN_WRITE_WORDS_16 = 16

MB_EXC_ILLEGAL_FN_CODE = 0x01
MB_EXC_ILLEGAL_DATA_ADDRESS = 0x02
# Величина, содержащаяся в поле данных запроса, является недопустимой величиной для подчиненного.
MB_EXC_ILLEGAL_DATA_VALUE = 0x03
MB_EXC_SERVER_FAILURE = 0x04


class MbLimits(enum.IntEnum):
    MAX_FRAME_SIZE_BYTES = 306
    MAX_READ_WORDS_NB = 127
    MAX_WRITE_WORDS_NB = 127
    MAX_READ_BITS_NB = 2000  # See JBus_Modbus.pdf page 40
    MAX_WRITE_BITS_NB = 1968  # See JBus_Modbus.pdf page 44


class MbFunctionCode(enum.IntEnum):
    MB_FN_READ_OUT_BITS_1 = 1
    MB_FN_READ_IN_BITS_2 = 2
    MB_FN_READ_OUT_WORDS_3 = 3
    MB_FN_READ_IN_WORDS_4 = 4
    MB_FN_WRITE_BIT_5 = 5
    MB_FN_WRITE_WORD_6 = 6
    MB_FN_WRITE_BITS_15 = 15
    MB_FN_WRITE_WORDS_16 = 16


'''
    Подчиненный принял запрос и обрабатывает его, но это требует много
    времени. Этот ответ предохраняет главного от генерации ошибки тайм-аута.
'''
MB_EXC_ACKNOWLEDGE = 0x05
'''
    Подчиненный занят обработкой команды. Главный должен повторить
    позже, когда подчиненный освободится.
'''
MB_EXC_SERVER_BUSY = 0x06
'''
    Подчиненный не может выполнить программную функцию, принятую в
    запросе. Этот код возвращается для неудачного программного запроса,
    использующего функции с номерами 13 или 14. Главный должен запросить
    диагностическую информацию или информацию об ошибках с подчиненного.
'''
MB_EXC_CANT_PROCESS_FN = 0x07
'''
    Подчиненный пытается читать расширенную память, но обнаружил ошибку
    паритета. Главный может повторить запрос, но обычно в таких случаях требуется ремонт.
'''
MB_EXC_MEM_PARITY = 0x08
MB_EXC_GATEWAY_PATHS_NA = 0x0A
MB_EXC_TARGETED_DEVICE_FAILED_TO_RESPOND = 0x0B


class MbExceptionCode(enum.IntEnum):
    MB_EXC_ACKNOWLEDGE = 0x05
    MB_EXC_SERVER_BUSY = 0x06
    MB_EXC_CANT_PROCESS_FN = 0x07
    MB_EXC_MEM_PARITY = 0x08
    MB_EXC_GATEWAY_PATHS_NA = 0x0A
    MB_EXC_TARGETED_DEVICE_FAILED_TO_RESPOND = 0x0B


class MbException(Exception):
    def __init__(self, code, msg=None):
        if msg:
            super().__init__('Modbus exception 0x{:x}: {}'.format(code, msg))
        else:
            super().__init__('Modbus exception 0x{:x}'.format(code))
        self.code = code


class ErrorCode(enum.IntEnum):
    BadData = 1
    UnknownFn = 2
    UnknownExc = 3
    BadCrc = 4
    NotEnoughSpace = 5  # при формировании сообщения буфер оказался недостаточным
    MismatchTrId = 6
    MismatchSlave = 7
    MismatchFn = 8
    MismatchData = 9


class MbError(Exception):
    def __init__(self, code, msg=None):
        if msg:
            super().__init__('Modbus error <{}>. {}'.format(code, msg))
        else:
            super().__init__('Modbus error <{}>'.format(code))
        self.code = code


# (fmt_id, fmt_size_words, fmt_min_n|None, fmt_max_n|None, fmt_struct_format, val_type)
MB_FORMATS_LIST = (
    ('i16',      1, stdint.MIN_I16, stdint.MAX_I16,     '>h', int),     # noqa: E241
    ('ui16',     1, 0,              stdint.MAX_UI16,    '>H', int),     # noqa: E241
    ('i32_be',   2, stdint.MIN_I32, stdint.MAX_I32,     '>i', int),     # noqa: E241
    ('ui32_be',  2, 0,              stdint.MAX_UI32,    '>I', int),     # noqa: E241
    ('i64_be',   4, stdint.MIN_I64, stdint.MAX_I64,     '>q', int),     # noqa: E241
    ('ui64_be',  4, 0,              stdint.MAX_UI64,    '>Q', int),     # noqa: E241
    ('f32_be',   2, None,           None,               '>f', float),   # noqa: E241
)


MB_FORMATS_DICT = {}
for f in MB_FORMATS_LIST:
    MB_FORMATS_DICT[f[0]] = f
