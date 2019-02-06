from string import ascii_letters, digits
alphabet_list = ascii_letters + digits


def caesar_code(text, shift):
    shift_text = ''

    for c in text:
        if c not in alphabet_list:
            shift_text += c
            continue

        i = (alphabet_list.index(c) + shift) % len(alphabet_list)
        shift_text += alphabet_list[i]

    return shift_text


if __name__ == '__main__':
	pass
