def encrypt(plaintext='sample', key=1):
    if key < 0:
        key = key % -26
    elif key >= 0 :
        key = key % 26
    cyphertext = ''
    for character in plaintext:
        if character.isalpha():
            number = ord(character)
            number += key
            if character.isupper():
                if number > ord('Z'):
                    number -= 26
                elif number < ord('A'):
                    number += 26
            elif character.islower():
                if number > ord('z'):
                    number -= 26
                elif number < ord('a'):
                    number += 26
            character = chr(number)
        cyphertext += character
    return cyphertext




if __name__ == '__main__':
    print(encrypt('sample',2))
