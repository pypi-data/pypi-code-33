from cybele.aes import AESCipher, passphrase_to_key


def test_encrypt_decrypt():
    plaintext = "plaintext"
    passphrase = "passphrase"
    key = passphrase_to_key(passphrase)
    cipher1 = AESCipher(key)
    cipher2 = AESCipher(key)
    encrypted = cipher1.encrypt(plaintext)
    decrypted = cipher2.decrypt(encrypted)
    assert decrypted == plaintext


def test_different_encryption_for_same_plaintext():
    plaintext = "plaintext"
    passphrase = "passphrase"
    key = passphrase_to_key(passphrase)
    cipher1 = AESCipher(key)
    cipher2 = AESCipher(key)
    encrypted1 = cipher1.encrypt(plaintext)
    encrypted2 = cipher2.encrypt(plaintext)
    assert encrypted1 != encrypted2
