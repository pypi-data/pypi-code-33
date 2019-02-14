import cryptography
import e3db
import os
import pytest
import nacl.utils
import nacl.secret
import nacl.public
import hashlib


def crypto_mode():
    if 'CRYPTO_SUITE' in os.environ and os.environ['CRYPTO_SUITE'] == 'NIST':
        return 'nist'

    return 'sodium'


def test_base64():
    # ensure encoding and decoding string results in same string as original
    string = "testing base64 is the best! #testing1"
    encoded = e3db.Crypto.base64encode(string)
    decoded = e3db.Crypto.base64decode(encoded)
    assert(string == decoded.decode())


def test_generate_keypair():
    if crypto_mode() != 'sodium':
        pytest.skip("Skipping Libsodium-reliant test")

    pubkey, privkey = e3db.Crypto.generate_keypair()
    assert(type(privkey) == nacl.public.PrivateKey)
    assert(type(pubkey) == nacl.public.PublicKey)


def test_public_key_encoding():
    if crypto_mode() != 'sodium':
        pytest.skip("Skipping Libsodium-reliant test")

    pubkey = 'RMG04iil2HDaUWye9wMVG8RmIL_s5tPOilRoiLUjLT8'
    decoded = e3db.Crypto.decode_public_key(pubkey)
    encoded = e3db.Crypto.encode_public_key(decoded)
    assert(pubkey == encoded.decode())
    assert(type(decoded) == nacl.public.PublicKey)


def test_private_key_encoding():
    if crypto_mode() != 'sodium':
        pytest.skip("Skipping Libsodium-reliant test")

    privkey = '_wSGC32a3g_VOPPy3kILDqzKLa1tPwdTNW3DQrJMPxk'
    decoded = e3db.Crypto.decode_private_key(privkey)
    encoded = e3db.Crypto.encode_private_key(decoded)
    assert(privkey == encoded.decode())
    assert(type(decoded) == nacl.public.PrivateKey)


def test_public_key_sharing():
    if crypto_mode() != 'sodium':
        pytest.skip("Skipping Libsodium-reliant test")
    # based on https://pynacl.readthedocs.io/en/latest/public/, but with e3db wrappers

    # create bob keys
    pkbob, skbob = e3db.Crypto.generate_keypair()
    skbob_encoded = e3db.Crypto.encode_private_key(skbob)
    skbob_decoded = e3db.Crypto.decode_private_key(skbob_encoded)
    pkbob_encoded = e3db.Crypto.encode_public_key(pkbob)
    pkbob_decoded = e3db.Crypto.decode_public_key(pkbob_encoded)

    # create alice keys
    pkalice, skalice = e3db.Crypto.generate_keypair()
    skalice_encoded = e3db.Crypto.encode_private_key(skalice)
    skalice_decoded = e3db.Crypto.decode_private_key(skalice_encoded)
    pkalice_encoded = e3db.Crypto.encode_public_key(pkalice)
    pkalice_decoded = e3db.Crypto.decode_public_key(pkalice_encoded)

    bob_box = e3db.Crypto.box(skbob_decoded, pkalice_decoded)

    message = "Tozny is awesome."

    nonce = e3db.Crypto.random_nonce()
    encrypted = bob_box.encrypt(message.encode(), nonce)
    alice_box = e3db.Crypto.box(skalice_decoded, pkbob_decoded)
    plaintext = alice_box.decrypt(encrypted).decode("utf-8")

    assert(message == plaintext)


def test_large_file_streaming_crypto():
    if crypto_mode() != 'sodium':
        pytest.skip("Skipping Libsodium-reliant test")
    # based on https://pynacl.readthedocs.io/en/latest/public/, but with e3db wrappers

    plaintext_filename = "10mb.txt"
    # Generate 10MB Large File to Upload
    with open(plaintext_filename, "w+") as f:
        for i in range(1, 1024):
            f.write('b' * 1024 * 10)

    with open(plaintext_filename, 'rb') as f:
        pre_encrypt_md5 = hashlib.md5(f.read()).hexdigest()
    ak = e3db.Crypto.random_key()
    encrypted_filename, hash, length = e3db.Crypto.encrypt_file(plaintext_filename, ak)
    destination_filename = "decrypted-{0}".format(plaintext_filename)
    e3db.Crypto.decrypt_file(encrypted_filename, destination_filename, ak)
    with open(destination_filename, 'rb') as f:
        post_decrypt_md5 = hashlib.md5(f.read()).hexdigest()
    assert(pre_encrypt_md5 == post_decrypt_md5)


def test_generate_nist_keypair():
    if crypto_mode() != 'nist':
        pytest.skip("Skipping NIST-specific test")

    pubkey, privkey = e3db.Crypto.generate_keypair()
    assert(type(privkey) == cryptography.hazmat.backends.openssl.ec._EllipticCurvePrivateKey)
    assert(type(pubkey) == cryptography.hazmat.backends.openssl.ec._EllipticCurvePublicKey)


def test_nist_public_key_encoding():
    if crypto_mode() != 'nist':
        pytest.skip("Skipping NIST-specific test")

    pubkey = 'LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUhZd0VBWUhLb1pJemowQ0FRWUZLNEVFQUNJRFlnQUVka3p1cXFQdWo5TzRUY0xkTzMxNVIvL2NsMXE5c3BtNApuck54UlMrS3R2SzZIdXZkMTBhcUVRZml1V0lFQnJzYkZuRllLaFV2bk9pKzBscVNpd29Wd3AvRTdJOUhyQ2NEClRIbks1RnY1ZEo4aFZBVTdmT3VreFJwOHVULzA1US9hCi0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQo'
    decoded = e3db.Crypto.decode_public_key(pubkey)
    encoded = e3db.Crypto.encode_public_key(decoded)
    assert(pubkey == encoded.decode())
    assert(type(decoded) == cryptography.hazmat.backends.openssl.ec._EllipticCurvePublicKey)


def test_nist_private_key_encoding():
    if crypto_mode() != 'nist':
        pytest.skip("Skipping NIST-specific test")

    privkey = 'LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JRzJBZ0VBTUJBR0J5cUdTTTQ5QWdFR0JTdUJCQUFpQklHZU1JR2JBZ0VCQkRDeDg1L3lENFIrSWFsRUNhbm8KQjBIUVdtWWpxYnNwK3hISEt5U3MrbDBZZ1d2M1BybXBXb0tvRGE1RTRQZDJ2czZoWkFOaUFBUUx0T213eWFVbQpmY25vRGNBQjQ4TC9yc2N4dlJ2a0g3Ri9lcWk1V0E4ZVRJbDAwSlZYNXFyZlR0a3drVTYwM2Q0aHA4R1FrOGlUCjl1RlMvLzhUdXdmVVE2VnJGd3IySThsc2wzUTcyTkhzSFhJQUhJdmgyZUlncXRnTUxtVEZWSEk9Ci0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS0K'
    decoded = e3db.Crypto.decode_private_key(privkey)
    encoded = e3db.Crypto.encode_private_key(decoded)
    assert(privkey == encoded.decode())
    assert(type(decoded) == cryptography.hazmat.backends.openssl.ec._EllipticCurvePrivateKey)


def test_nist_public_key_sharing():
    if crypto_mode() != 'nist':
        pytest.skip("Skipping NIST-specific test")
    # based on https://pynacl.readthedocs.io/en/latest/public/, but with e3db wrappers

    # create bob keys
    pkbob, skbob = e3db.Crypto.generate_keypair()
    skbob_encoded = e3db.Crypto.encode_private_key(skbob)
    skbob_decoded = e3db.Crypto.decode_private_key(skbob_encoded)
    pkbob_encoded = e3db.Crypto.encode_public_key(pkbob)
    pkbob_decoded = e3db.Crypto.decode_public_key(pkbob_encoded)

    # create alice keys
    pkalice, skalice = e3db.Crypto.generate_keypair()
    skalice_encoded = e3db.Crypto.encode_private_key(skalice)
    skalice_decoded = e3db.Crypto.decode_private_key(skalice_encoded)
    pkalice_encoded = e3db.Crypto.encode_public_key(pkalice)
    pkalice_decoded = e3db.Crypto.decode_public_key(pkalice_encoded)

    bob_exchange = e3db.Crypto._exchange(skbob_decoded, pkalice_decoded)

    message = b"Tozny is awesome."

    nonce = e3db.Crypto.random_nonce()
    encrypted = bob_exchange.encrypt(nonce, message, None)
    alice_box = e3db.Crypto._exchange(skalice_decoded, pkbob_decoded)
    plaintext = alice_box.decrypt(nonce, encrypted, None)

    assert(message == plaintext)
