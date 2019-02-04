#!/usr/bin/env python3
import os.path
import pyAesCrypt
import os
import getpass
from enum import Enum
import argparse
import base64


class CryptAction(Enum):
    ENCRYPT = 1
    DECRYPT = 2
    TOGGLE = 3


SUFFIX = ".pcaes"
BUFFER_SIZE = 32 * 1024


def __is_encrypted(fl_path):
    global SUFFIX
    return fl_path.endswith(SUFFIX)


def __encrypt_filename(fl_name):
    fl_basename = os.path.basename(fl_name)
    fl_folder = os.path.dirname(fl_name)
    b64str = base64.urlsafe_b64encode(fl_basename.encode('ascii')).decode('ascii')
    global SUFFIX
    nm = ''.join([hex(ord(b))[2:] for b in b64str]) + SUFFIX
    return os.path.join(fl_folder, nm)


def __decrypt_filename(fl_name):
    fl_encname = os.path.basename(fl_name)
    fl_folder = os.path.dirname(fl_name)
    global SUFFIX
    dec_name = fl_encname[:-len(SUFFIX)]
    cmps = [dec_name[i:i + 2] for i in range(0, len(dec_name), 2)]
    dec_name = ''.join([chr(int(i, 16)) for i in cmps])
    nm = base64.urlsafe_b64decode(dec_name.encode('ascii')).decode('ascii')
    return os.path.join(fl_folder, nm)


def __crypt_folder_name(fl_name, crypt_action, ignore_errors):
    crypted = __is_encrypted(fl_name)
    if crypt_action == CryptAction.TOGGLE:
        crypting = not crypted
    elif (crypt_action == CryptAction.ENCRYPT and not crypted):
        crypting = True
    elif (crypt_action == CryptAction.DECRYPT and crypted):
        crypting = False
    else:
        print("Skipping folder %s ..." % fl_name)
        return

    if crypting:
        print("Encrypting folder %s ..." % fl_name, end=" ")
        new_name = __encrypt_filename(fl_name)
    else:
        print("Decrypting folder %s ..." % fl_name, end=" ")
        new_name = __decrypt_filename(fl_name)

    os.rename(fl_name, new_name)
    print("Done.")


def __crypt_file(abs_fl, pwd, crypt_action=CryptAction.TOGGLE, ignnore_errors=False):
    crypted = __is_encrypted(abs_fl)
    if crypt_action == CryptAction.TOGGLE:
        crypting = not crypted
    elif (crypt_action == CryptAction.ENCRYPT and not crypted):
        crypting = True
    elif (crypt_action == CryptAction.DECRYPT and crypted):
        crypting = False
    else:
        print("Skipping file%s ..." % abs_fl)
        return

    try:
        if crypting:
            # encrypt
            print("Encrypting file %s ..." % abs_fl, end=" ")
            pyAesCrypt.encryptFile(abs_fl, __encrypt_filename(abs_fl), pwd, BUFFER_SIZE)
        else:
            # decrypt
            print("Decrypting file %s ..." % abs_fl, end=" ")
            pyAesCrypt.decryptFile(abs_fl, __decrypt_filename(abs_fl), pwd, BUFFER_SIZE)

        print("Done.")
        os.remove(abs_fl)
    except Exception as e:
        if ignnore_errors:
            return
        error_msg = "ERROR: Failed to %s file \"%s\" (%s)!" % ("encrypt" if crypting else "decrypt", abs_fl, str(e))
        print(error_msg)
        raise Exception(error_msg)


def __crypt_folder_names(abs_folder, crypt_action, ignore_errors):
    for root, subdirs, files in os.walk(abs_folder):
        for subdir in subdirs:
            full_subdir = os.path.join(root, subdir)
            __crypt_folder_names(full_subdir, crypt_action, ignore_errors)
            __crypt_folder_name(os.path.join(root, subdir), crypt_action, ignore_errors)


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

    __crypt_folder_names(abs_folder, crypt_action, ignore_errors)

    if (len(error_list) == 0):
        return

    raise Exception("\n".join([str(e) for e in error_list]))


def __main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to the file or folder", type=str)
    parser.add_argument("-p", "--password", help="The password used for encryption", type=str, default=None)
    parser.add_argument("-e", "--encrypt", help="Encrypt the file(s)/folder(s)", action="store_true")
    parser.add_argument("-d", "--decrypt", help="Decrypt the file(s)/folder(s)", action="store_true")
    parser.add_argument("-n", "--noerrors", help="Ignore errors", action="store_true")
    args = parser.parse_args()

    path = args.path.encode('ascii', 'ignore').decode('ascii')

    action = CryptAction.TOGGLE
    if args.encrypt:
        action = CryptAction.ENCRYPT
    elif args.decrypt:
        action = CryptAction.DECRYPT

    if not os.path.exists(path):
        print("ERROR: \"%s\" is not a valid path!" % str(args.path))
        return

    password = args.password
    if password is None:
        password = getpass.getpass("Please provide the password: ")

    try:
        if os.path.isdir(path):
            __crypt_folder(path, password, action, args.noerrors)
        else:
            __crypt_file(path, password, action, args.noerrors)
    except Exception as e:
        print(str(e))


if __name__ == "__main__":
    __main()
