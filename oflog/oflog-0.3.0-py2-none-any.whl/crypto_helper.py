from base64 import urlsafe_b64decode
import Crypto
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto import Random
import ast

class CryptoHelper(object):
    @staticmethod
    def decrypt_rsa(ciphertext, private_key_file):
        if not private_key_file:
            print "Error: must pass --private-key to decrypt log with"
            return    
        try:
            f = open(private_key_file, 'rb')
            private_key = f.read()
            f.close()
            key = RSA.importKey(private_key)
        except Exception as e:
            print "Error parsing private key={0}".format(e)
            return

        try: 
            cipher = PKCS1_OAEP.new(key)
            decrypted_message = cipher.decrypt(ciphertext.decode("hex"))
            return decrypted_message
        except Exception as e:
            print "Error decrypting ciphertext"
            return


    @staticmethod
    def decrypt_aes(ciphertext, aes_key, iv):
        try:
            BS = 16
            cipher = AES.new(aes_key, AES.MODE_CBC, iv, segment_size=AES.block_size*8)
            return cipher.decrypt(ciphertext)

        except:
            print "Error decrypting ciphertext"
            return