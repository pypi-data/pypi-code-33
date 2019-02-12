import re
import textwrap


NAME_REGEX = r'^[a-zA-Z0-9_]{1,99}$'
OP_PUSHDATA1 = '4c'
OP_PUSHDATA2 = '4d'
OP_PUSHDATA4 = '4e'


class Registration:
    def __init__(self, name, payment_info):
        validate_name(name)
        self.name = name
        self.payment_info = payment_info

    def __str__(self):
        payment_info = textwrap.indent(str(self.payment_info), '  ')
        return ('name:      {}\n'
                'op_return: {}\n'
                'payment info:\n'
                '{}'.format(self.name, opreturn(self), payment_info))


def validate_name(n):
    if re.match(NAME_REGEX, n):
        return
    raise ValueError(r'"{}" does not meet cash account name requirements: {}'
                     r''.format(n, NAME_REGEX))


def electron_markdown(registration):
    template = ('<push><hex>01010101'
                '<push><hex>{hex_name}'
                '<push><hex>{payment_info}')
    return template.format(hex_name=str_to_utf8hex(registration.name),
                           payment_info=registration.payment_info.cashaccount_hex())


def opreturn(registration):
    name_hex = str_to_utf8hex(registration.name)
    info_hex = registration.payment_info.cashaccount_hex()
    result = ''.join([
        '04',                    # OP_RETURN
        '01010101',              # cash account protocol
        _minpush_for(name_hex),  # push code for name
        name_hex,
        _minpush_for(info_hex),  # push code for payment info
        info_hex,
    ])
    return result


def str_to_utf8hex(s):
    return s.encode('utf-8').hex()


def utf8hex_to_str(hex_string):
    return bytes.fromhex(hex_string).decode('utf-8')


def _minpush_for(hex_string):
    """Choose the most efficient OP_PUSH for the given data.

    Thank you to James Cramer and Mark Lundeberg for pointing
    this issue out to me and to the cash account protocol in general.
    """
    bytelen = len(hex_string) // 2
    if len(hex_string) % 2 != 0:
        raise ValueError('got an odd number of hex digits ({}). require 1-byte hex pairs'.format(bytelen+1))
    if bytelen == 0:
        raise ValueError('expected at least one byte of data but got zero')
    elif bytelen < 76:
        return '{:02x}'.format(bytelen)
    elif bytelen < 2**8:
        return OP_PUSHDATA1 + '{:02x}'.format(bytelen)
    # nah...
    # elif bytelen < 2**16:
    #     return OP_PUSHDATA2 + '{:04x}'.format(bytelen)
    # elif bytelen < 2**32:
    #     return OP_PUSHDATA4 + '{:08x}'.format(bytelen)
    raise ValueError('only data up to 255 bytes are supported but got {} bytes'.format(bytelen))
