import re
from math import fabs

from tracuni.define.const import MASK_PARAMS


def mask_partial(row, symbol='*', from_idx=4, to_idx=-4):
    """
    Частичное экранирование строки
    :param row: строка для экранирования
    :param symbol: экранирующий символ
    :param from_idx: стартовая позиция маски
    :param to_idx: конечная позиция маски
    :return:
    """
    row = str(row)
    mask_len = round(len(row) - fabs(from_idx) - fabs(to_idx))
    masked_row = row[:from_idx] + mask_len * symbol + row[to_idx:]
    return masked_row


def mask_full(row, symbol='x'):
    """
    Полное экранирование строки
    :param row: строка
    :param symbol: экранирующий символ
    :return:
    """
    row = str(row)
    masked_row = symbol * len(row)
    return masked_row


def replace_fn(match_obj):
    """
        Пробуем сохранитьб валидный JSON:
            * Если мы число поменяли на строку, оборачиваем в кавычки
            * Если у нас были параметры запроса внутри строки, то возвращаем
            хвостовую кавычку
    :param match_obj:
    :return:
    """
    groups = match_obj.groups()

    variant = MASK_PARAMS.get(groups[0])

    mask_fn = None
    if variant == 'full':
        mask_fn = mask_full
    elif variant == 'part':
        mask_fn = mask_partial

    if mask_fn:
        masked = mask_fn(groups[2] or groups[5])
        double_quotes_tail = groups[3] or ''
        double_quotes = '"' if groups[5] else ''
        sep = groups[1] or groups[4]

        return (
            groups[0]
            +
            sep
            +
            double_quotes
            +
            masked
            +
            double_quotes
            +
            double_quotes_tail
        )


kwords = r'(' + r'|'.join(MASK_PARAMS.keys()) + r')'
p = re.compile(
    kwords + r'(?:(\s*?=\s*)([^&\n"]*)("?)|([\'"]\s*?:\s*)"?([^,\n"]*)"?)'
)


def do(data):
    data = p.sub(replace_fn, data)
    return data
