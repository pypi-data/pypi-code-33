def encrypt_s(text, key_text):
    key_text = key_text
    j = 0
    encrypt_text = ''
    for i in text:
        encrypt_text_one = i
        if i.isalpha():
            k = 1
            while k:
                if j >= key_text.__len__():
                    j = 0
                m = key_text[j]
                if not m.isalpha():
                    j += 1
                else:
                    k = 0
            encrypt_text_one = spot(i, key_text[j])
            j += 1
        encrypt_text += encrypt_text_one
    return encrypt_text


def spot(text, key):
    text_ord = ord(text)
    distance = ord(key) - ord('a')
    if text.isupper():
        if text_ord + distance > ord('Z'):
            distance -= 26
        elif text_ord + distance < ord('A'):
            distance += 26
    elif text.islower():
        if text_ord + distance > ord('z'):
            distance -= 26
        elif text_ord + distance < ord('a'):
            distance += 26
    return chr(distance + text_ord)


if __name__ == '__main__':
    print(encrypt_s('sample', 'key'))
