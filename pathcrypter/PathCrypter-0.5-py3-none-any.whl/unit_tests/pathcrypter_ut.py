from unittest import TestCase
from pathcrypter.pathcrypter import decrypt_filename, version1_encrypt_filename, encrypt_filename
import os.path


class TestFilenameEncryption(TestCase):
    def test_decrypt_v1_file_name(self):
        fl_name = "/usr/testing/path/testfile.fl"
        v1_fl_name = version1_encrypt_filename(fl_name)
        decrypted_fl_name = decrypt_filename(v1_fl_name, "")
        if fl_name != decrypted_fl_name:
            self.fail("Decrypting a pre v0.5 filename failed")

    def test_encrypt_decrypt_file_name(self):
        fl_name = "/usr/testing/path/testfile.fl"
        pwd = "password"
        enc_name = encrypt_filename(fl_name, pwd)
        decrypted_fl_name = decrypt_filename(enc_name, pwd)
        if fl_name != decrypted_fl_name:
            self.fail("Decrypting a pre v0.5 filename failed")

    def test_encrypt_basename_only(self):
        fl_name = "/usr/testing/path/testfile.fl"
        pwd = "password"
        enc_name = encrypt_filename(fl_name, pwd)
        if os.path.dirname(fl_name) != os.path.dirname(enc_name):
            self.fail("The directory structure was not left unchanged!")

    def test_decryption_incorrect_password(self):
        fl_name = "/usr/testing/path/testfile.fl"
        pwd = "password"
        enc_name = encrypt_filename(fl_name, pwd)
        try:
            decrypted_fl_name = decrypt_filename(enc_name, pwd+"suffix")
        except:
            return #this is OK. Decryption should fail
        self.fail("Decryption with an incorrect password is not reported as error!")