#!/usr/bin/env python3
import os.path
import pyAesCrypt
import os
import getpass
from enum import Enum
import argparse
import base64
import platform
import shutil
from Crypto.Cipher import AES
from Crypto.Random import new as Random
from hashlib import sha256

SUFFIX = ".pcaes"
BUFFER_SIZE = 32 * 1024

class CryptAction(Enum):
    ENCRYPT = 1
    DECRYPT = 2
    TOGGLE = 3


class CryptStats:
    def __init__(self):
        self.action = CryptAction.TOGGLE
        self.folders_total = 0
        self.folders_failed = 0
        self.folders_crypted = 0
        self.folders_skipped = 0
        self.files_total = 0
        self.files_failed = 0
        self.files_crypted = 0
        self.files_skipped = 0


class AESCipher:
    def __init__(self, data, key):
        self.block_size = 16
        self.data = data
        self.key = sha256(key.encode()).digest()[:32]
        self.pad = lambda s: s + (self.block_size - len(s) % self.block_size) * chr(
            self.block_size - len(s) % self.block_size)
        self.unpad = lambda s: s[:-ord(s[len(s) - 1:])]

    def encrypt(self):
        plain_text = self.pad(self.data)
        iv = Random().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_OFB, iv)
        return base64.urlsafe_b64encode(iv + cipher.encrypt(plain_text.encode('ascii'))).decode('ascii')

    def decrypt(self):
        cipher_text = base64.urlsafe_b64decode(self.data.encode('ascii'))
        iv = cipher_text[:self.block_size]
        cipher = AES.new(self.key, AES.MODE_OFB, iv)
        return self.unpad(cipher.decrypt(cipher_text[self.block_size:])).decode('ascii')


CRYPT_STATS = CryptStats()

def __is_encrypted(fl_path):
    global SUFFIX
    return fl_path.endswith(SUFFIX)


def version1_encrypt_filename(fl_name):
    fl_basename = os.path.basename(fl_name)
    fl_folder = os.path.dirname(fl_name)
    b64str = base64.urlsafe_b64encode(fl_basename.encode('ascii')).decode('ascii')
    global SUFFIX
    nm = ''.join([hex(ord(b))[2:] for b in b64str]) + SUFFIX
    return os.path.join(fl_folder, nm)


def encrypt_filename(fl_name, pwd):
    fl_basename = os.path.basename(fl_name)
    fl_folder = os.path.dirname(fl_name)
    b64str = AESCipher(fl_basename, pwd).encrypt()
    global SUFFIX
    return os.path.join(fl_folder, b64str + SUFFIX)


def decrypt_filename(fl_name, pwd):
    fl_encname = os.path.basename(fl_name)
    fl_folder = os.path.dirname(fl_name)
    global SUFFIX
    dec_name = fl_encname[:-len(SUFFIX)]
    try:
        nm = AESCipher(dec_name, pwd).decrypt()
        if len(nm) > 0:
            return os.path.join(fl_folder, nm)
    except Exception as e:
        pass

    try:
        cmps = [dec_name[i:i + 2] for i in range(0, len(dec_name), 2)]
        dec_name = ''.join([chr(int(i, 16)) for i in cmps])
        nm = base64.urlsafe_b64decode(dec_name.encode('ascii')).decode('ascii')

        return os.path.join(fl_folder, nm)
    except:
        raise Exception("Failed to decrypt the file/folder name!")


def __crypt_folder_name(fl_name, pwd, crypt_action, ignore_errors):
    global CRYPT_STATS
    CRYPT_STATS.folders_total += 1
    CRYPT_STATS.folders_failed += 1
    crypted = __is_encrypted(fl_name)
    if crypt_action == CryptAction.TOGGLE:
        crypting = not crypted
    elif (crypt_action == CryptAction.ENCRYPT and not crypted):
        crypting = True
    elif (crypt_action == CryptAction.DECRYPT and crypted):
        crypting = False
    else:
        print("Skipping folder %s ..." % fl_name)
        CRYPT_STATS.folders_failed -= 1
        CRYPT_STATS.folders_skipped += 1
        return

    if crypting:
        print("Encrypting folder %s ..." % fl_name, end=" ")
        new_name = encrypt_filename(fl_name, pwd)
    else:
        print("Decrypting folder %s ..." % fl_name, end=" ")
        new_name = decrypt_filename(fl_name, pwd)

    os.rename(fl_name, new_name)
    CRYPT_STATS.folders_failed -= 1
    CRYPT_STATS.folders_crypted += 1
    print("Done.")


def __crypt_file(abs_fl, pwd, crypt_action=CryptAction.TOGGLE, ignore_errors=False):
    global CRYPT_STATS
    CRYPT_STATS.files_total += 1
    CRYPT_STATS.files_failed += 1
    crypted = __is_encrypted(abs_fl)
    if crypt_action == CryptAction.TOGGLE:
        crypting = not crypted
    elif (crypt_action == CryptAction.ENCRYPT and not crypted):
        crypting = True
    elif (crypt_action == CryptAction.DECRYPT and crypted):
        crypting = False
    else:
        print("Skipping file%s ..." % abs_fl)
        CRYPT_STATS.files_failed -= 1
        CRYPT_STATS.files_skipped += 1
        return

    try:
        if crypting:
            # encrypt
            print("Encrypting file %s ..." % abs_fl, end=" ")
            pyAesCrypt.encryptFile(abs_fl, encrypt_filename(abs_fl, pwd), pwd, BUFFER_SIZE)
        else:
            # decrypt
            print("Decrypting file %s ..." % abs_fl, end=" ")
            pyAesCrypt.decryptFile(abs_fl, decrypt_filename(abs_fl, pwd), pwd, BUFFER_SIZE)

        print("Done.")
        os.remove(abs_fl)
        CRYPT_STATS.files_failed -= 1
        CRYPT_STATS.files_crypted += 1
    except Exception as e:
        if ignore_errors:
            return
        error_msg = "ERROR: Failed to %s file \"%s\" (%s)!" % ("encrypt" if crypting else "decrypt", abs_fl, str(e))
        print(error_msg)
        raise Exception(error_msg)


def __crypt_folder_names(abs_folder, pwd, crypt_action, ignore_errors):
    for root, subdirs, files in os.walk(abs_folder):
        for subdir in subdirs:
            full_subdir = os.path.join(root, subdir)
            __crypt_folder_names(full_subdir, pwd, crypt_action, ignore_errors)
            __crypt_folder_name(os.path.join(root, subdir), pwd, crypt_action, ignore_errors)


def __crypt_folder(abs_folder, pwd, crypt_action=CryptAction.TOGGLE, ignore_errors=False):
    error_list = []
    for root, subdirs, files in os.walk(abs_folder):
        # for subdir in subdirs:
        #    __crypt_folder(os.path.join(root, subdir), pwd, crypt_action, ignore_errors)
        for fl in files:
            try:
                __crypt_file(os.path.join(root, fl), pwd, crypt_action, ignore_errors)
            except Exception as e:
                error_list.append(e)

    __crypt_folder_names(abs_folder, pwd, crypt_action, ignore_errors)

    if (len(error_list) == 0):
        return

    raise Exception("\n".join([str(e) for e in error_list]))


class InstallAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print('Installing platform specific services. Ignoring all other options.')
        if platform.system().lower() == 'darwin':
            # OS X - install services/workflows
            package_path = os.path.join(os.path.dirname(__file__), "static_data", "osx_workflows.zip")
            try:
                services_path = os.path.join(os.path.expanduser("~"), "Library", "Services")
                shutil.unpack_archive(package_path, services_path, "zip")
            except Exception as e:
                print("ERROR: Failed to unpack the services (%s)!" % str(e))
                return

            import zipfile
            zz = zipfile.ZipFile(package_path)
            for name in zz.namelist():
                print("Installed: %s" % name)
            zz.close()

            print("Done.")
        parser.exit()


class UninstallAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print('Uninstalling platform specific services. Ignoring all other options.')
        if platform.system().lower() == 'darwin':
            # OS X - uninstall services/workflows
            package_path = os.path.join(os.path.dirname(__file__), "static_data", "osx_workflows.zip")
            try:
                services_path = os.path.join(os.path.expanduser("~"), "Library", "Services")
                for name in os.listdir(services_path):
                    if not name.lower().startswith("pathcrypter"):
                        continue
                    full_name = os.path.join(services_path, name)
                    if os.path.isfile(full_name):
                        os.remove(full_name)
                        print("Uninstalled file: %s" % name)
                    if os.path.isdir(full_name):
                        shutil.rmtree(full_name)
                        print("Uninstalled folder: %s" % name)
                print("Done.")
            except Exception as e:
                print("ERROR: Failed to uninstall the services (%s)!" % str(e))
                return

        parser.exit()

def __fancy_process_stat(lst, val, label):
    if val > 0:
        lst.append("%s: %d" % (label, val))

def __main():
    parser = argparse.ArgumentParser()
    parser.register('action', 'install', InstallAction)
    parser.register('action', 'uninstall', UninstallAction)
    parser.add_argument("-p", "--password", help="The password used for encryption", type=str, default=None)
    parser.add_argument("-e", "--encrypt", help="Encrypt the file(s)/folder(s)", action="store_true")
    parser.add_argument("-d", "--decrypt", help="Decrypt the file(s)/folder(s)", action="store_true")
    parser.add_argument("-n", "--noerrors", help="Ignore errors", action="store_true")
    parser.add_argument("-i", "--install", help="Install platform specific services", action="install", nargs=0)
    parser.add_argument("-u", "--uninstall", help="Uninstall platform specific services", action="uninstall", nargs=0)
    parser.add_argument("-s", "--stats", help="Print stats", action="store_true")
    parser.add_argument("path", help="Path to the file or folder", nargs='+')

    try:
        args = parser.parse_args()
    except Exception as e:
        print("ERROR: Failed parsing the arguments (%s)!" % str(e))
    #
    # path = " ".join(args.path)
    # path = path.encode('ascii', 'ignore').decode('ascii')

    action = CryptAction.TOGGLE
    if args.encrypt:
        action = CryptAction.ENCRYPT
    elif args.decrypt:
        action = CryptAction.DECRYPT

    global CRYPT_STATS
    CRYPT_STATS.action = action

    password = args.password
    if password is None:
        password = getpass.getpass("Please provide the password: ")

    for p in args.path:
        path = p.encode('ascii', 'ignore').decode('ascii')
        if not os.path.exists(path):
            print("ERROR: \"%s\" is not a valid path!" % str(path))

        try:
            if os.path.isdir(path):
                __crypt_folder(path, password, action, args.noerrors)
            else:
                __crypt_file(path, password, action, args.noerrors)
        except Exception as e:
            print(str(e))

    # Print the stats
    print("\nStatistics:")

    fancy_print_action = "toggle encryption state"
    if CRYPT_STATS.action == CryptAction.ENCRYPT:
        fancy_print_action = "encrypt"
    elif CRYPT_STATS.action == CryptAction.DECRYPT:
        fancy_print_action = "decrypt"
    print("- Action: %s" % fancy_print_action)

    stats = []
    __fancy_process_stat(stats, CRYPT_STATS.folders_failed, "failed")
    __fancy_process_stat(stats, CRYPT_STATS.folders_skipped, "skipped")
    __fancy_process_stat(stats, CRYPT_STATS.folders_crypted, "crypted")
    if CRYPT_STATS.folders_total > 0:
        print("- Folders: %d (%s)" % (CRYPT_STATS.folders_total, ", ".join(stats)))
    else:
        print("- Folders: 0")

    stats = []
    __fancy_process_stat(stats, CRYPT_STATS.files_failed, "failed")
    __fancy_process_stat(stats, CRYPT_STATS.files_skipped, "skipped")
    __fancy_process_stat(stats, CRYPT_STATS.files_crypted, "crypted")
    if CRYPT_STATS.files_total > 0:
        print("- Files: %d (%s)" % (CRYPT_STATS.files_total, ", ".join(stats)))
    else:
        print("- Files: 0")

    print("- Path(s):")
    for p in args.path:
        print("   - %s" % p)

if __name__ == "__main__":
    __main()
