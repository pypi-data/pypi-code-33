# Import random string stuff
import random
import string

STRING_CHARACTERS = string.ascii_uppercase + string.ascii_lowercase + string.digits


def _get_extra_characters():
    return ''.join([random.choice(STRING_CHARACTERS) for _ in range(2)])


def obfuscate(s_in):
    # expand the string, filling with random
    s_work = "/" + ''.join([c + _get_extra_characters() for c in s_in])
    # decrement the chars in the string
    s_out = "".join([str(chr(ord(c) - 1)) for c in s_work])
    return s_out


def deobfuscate(s_in):
    # if it doesn't start with a '.' it's not obfuscated. Return as is.
    if s_in[0] != '.':
        return s_in
    # To deobfuscate, we can just ascii shift the chars in the string, and remove the unwanted chars.
    s_out = ''.join([str(chr(ord(s_in[i]) + 1)) for i in range(1, len(s_in) - 1, 3)])
    return s_out


if __name__ == '__main__':
    teststring = "12345--2019.01.01"
    obf = obfuscate("12345--2019.01.01")
    deobf = deobfuscate(obf)
    print(teststring)
    print(obf)
    print(deobf)
