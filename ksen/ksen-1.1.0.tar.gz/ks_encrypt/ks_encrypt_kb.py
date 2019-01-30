# data
dictCap = 'Q W E R T Y U I O P A S D F G H J K L Z X C V B N M'.split(' ')
dictLow = 'q w e r t y u i o p a s d f g h j k l z x c v b n m'.split(' ')


# encrypt function
def encrypt_kb(text, key):
    encrypt_text = ''
    for char in text:
        if char.isalpha():
            char_encrypt = encrypt_alpha_by_alpha(char, key)
        encrypt_text += char_encrypt
    return encrypt_text


# encrypt one alpha function
def encrypt_alpha_by_alpha(alpha, key):
    if alpha.islower():
        pos = dictLow.index(alpha)
        pos += key
    elif alpha.isupper():
        pos = dictCap.index(alpha)
    if pos > 26:
        pos -= 26
    elif pos < 0:
        pos += 26
    if alpha.islower():
        return dictLow[pos]
    elif alpha.isupper():
        return dictCap[pos]


# main function
if __name__ == '__main__':
    print(encrypt_kb('sample', 2))
