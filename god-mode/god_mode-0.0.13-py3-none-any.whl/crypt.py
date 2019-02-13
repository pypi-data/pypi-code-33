#!/usr/bin/python

import sys
import pyAesCrypt
import getopt
import os
import io
import errno
import tempfile
import uuid
import re
import argparse
import yaml
import ntpath
import codecs
from zipfile import ZipFile
from colorama import init, Fore, Back, Style
from god_mode.metadata_rw import yaml_init

# -*- coding: utf-8 -*-

def main():

    init(autoreset=True)

    parser = argparse.ArgumentParser(description='Simple encryption/decryption script.')
    parser.add_argument('argFiles', nargs="*", type=str, help='List o files to encrypt/decrypt')
    parser.add_argument('-v','--verbose', help='Show what the script is doing.', action='store_true')
    parser.add_argument('-f','--files', help='File containing a list of files to encrypt/decrypt.', type=str)
    parser.add_argument('-d','--destination', help='Path to the encrypted/decrypted file(s). (Do NOT include any file or extension. Only the location to store the file(s).)', type=str, required=True)
    parser.add_argument('-m','--mode', help='Choose whether to encrypt or decrypt the file(s).', choices=['encrypt', 'decrypt'], type=str, required=True)
    parser.add_argument('-p','--password', help='The password to encrypt and decrypt the files.', type=str, required=True)
    parser.add_argument('-b','--buffer-multiplier', help='Choose the buffer size multiplier. (x * 1024). Default is 64. MUST BE THE SAME TO DECRYPT AND ENCRYPT.', default=64, type=int)
    parser.add_argument('-k','--kill', help="Choose this flag if you want to delete the original file when the encryption/decryption finish.", action='store_true')
    parser.add_argument('-e','--extension', help='Extension of the file(s) to be encrypted or decrypted.', default=".aes", type=str)
    parser.add_argument('--decryptor-file', help='File containing encrypted file information, such as original file name and original extension. To use this file, the name of the encrypted file must be the same as it was assigned.', type=str)
    args = parser.parse_args()

    decryptor = False
    # search for decrypt file
    if(args.mode == 'decrypt'):
        if args.decryptor_file:
            path, filename = os.path.split(args.decryptor_file)
            result = find(filename, path)
            if(result):
                metadataFile = True
                decryptor = True


    
    if args.verbose:
        print("[verbose]: Argument Passed Files ", args.argFiles)
        print('[verbose]: Files [',args.files,']')
        print('[verbose]: Destination [',args.destination,']')
        print('[verbose]: Mode [',args.mode,']')
        if(decryptor):
            print('[verbose]: Decryptor file given: ' + args.decryptor_file)
        print('[verbose]: Password [',args.password,']')
        print('[verbose]: Extension [',args.extension,']')
        print('[verbose]: Buffer Multiplier [',args.buffer_multiplier,']')
        #print('[verbose]: Real Buffer-Size [',bufferSize,']')
        print('[verbose]: Kill [',args.kill,']')
        print('[verbose]: Crypt version: 0.0.1b\n')

    noFiles = False
    noArgFiles = False

    if not args.files and not args.argFiles:
        if(args.mode == 'decrypt'):
            if(args.decryptor_file == '' or not metadataFile):
                print("Error: No files given.\n")               
                sys.exit()
        else:
            print("Error: No files given.\n")               
            sys.exit()

    if not args.files:
        noFiles = True
    if not args.argFiles:
        noArgFiles = True
    
    bufferSize = args.buffer_multiplier * 1024

    if not os.path.isfile(args.destination):
        if not os.path.exists(args.destination):
            print(Style.BRIGHT + Fore.WHITE + Back.RED + ' [Error]=> ' + Style.RESET_ALL + ' Destination "' + args.destination + '" not found. Use -h or --help.')
    else:
        print(Style.BRIGHT + Fore.WHITE + Back.RED + ' [Error]=> ' + Style.RESET_ALL + ' Destination cannot be a file. Use -h or --help.')

    if args.argFiles:
        for item in args.argFiles:
            if not os.path.exists(item):
                print(Style.BRIGHT + Fore.WHITE + Back.RED + ' [Error]=> ' + Style.RESET_ALL + ' Invalid argument: "' + item + '" Use -h or --help.')
                sys.exit(1)
            if not os.path.isfile(item):
                print(Style.BRIGHT + Fore.WHITE + Back.RED + ' [Error]=> ' + Style.RESET_ALL + ' Invalid argument: "' + item + '" Use -h or --help.')
                sys.exit(1)
    if args.files:
        if not os.path.exists(args.files):
            print(Style.BRIGHT + Fore.WHITE + Back.RED + ' [Error]=> ' + Style.RESET_ALL + ' File not found: "' + args.files + '" Use -h or --help.')
            sys.exit(1)



    if args.argFiles:
        for item in args.argFiles:
            if(args.mode == "encrypt"):
                generated_filename = str(uuid.uuid4())
                if(args.verbose):
                    print('Adding new encrypted file to metadata file.')
                try:
                    base = os.path.basename(item)
                    filename = os.path.splitext(base)[0]
                    extension = os.path.splitext(base)[1]
                    data = [[filename, generated_filename, extension, bufferSize]]
                    yaml_init(['w', args.destination + '/metadata.yaml', data, args.verbose])
                except:
                    print(Style.BRIGHT + Fore.WHITE + Back.RED + ' [Error]=> ' + Style.RESET_ALL + ' Unable to write metadata in: "' + args.destination + "/" + 'metadata.yaml' + '" Use -h or --help.')
                    sys.exit(1)

                print('Encrypting: ' + item)
                pyAesCrypt.encryptFile(item, args.destination + "/" + generated_filename + args.extension, args.password, bufferSize)
                
                if(args.kill):
                    os.remove(item)
                    print('File: "', item, '"Deleted (-k, --kill)"')
            
            elif(args.mode == "decrypt"):
                generated_filename = str(uuid.uuid4())
                
                print('Decrypting: ' + item)
                pyAesCrypt.decryptFile(item, args.destination + "/" + generated_filename + args.extension, args.password, bufferSize)
                
                if(args.kill):
                    os.remove(item)
                    print('File: "', item, '"Deleted (-k, --kill)"')

    names = []
    if args.files:
        lines = open(args.files, encoding='utf-8').read().split("\n")
        for item in lines:
            if not path_leaf(item) in names and item != '': 
                if(args.mode == "encrypt"):
                    generated_filename = str(uuid.uuid4())
                    if(args.verbose):
                        print('Adding new encrypted file to metadata file.')
                    try:
                        base = os.path.basename(item)
                        filename = os.path.splitext(base)[0]
                        extension = os.path.splitext(base)[1]
                        data = [[filename, generated_filename, extension, bufferSize]]
                        yaml_init(['w', args.destination + '/metadata.yaml', data, args.verbose])
                    except:
                        print(Style.BRIGHT + Fore.WHITE + Back.RED + ' [Error]=> ' + Style.RESET_ALL + ' Unable to write metadata in: "' + args.destination + "/" + 'metadata.yaml' + '" Use -h or --help.')
                        sys.exit(1)
                    print('Encrypting: ' + item)
                    pyAesCrypt.encryptFile(item, args.destination + "/" + generated_filename + args.extension, args.password, bufferSize)
                    if(args.kill):
                        os.remove(item)
                        print('File: "', item, '"Deleted (-k, --kill)"')
                elif(args.mode == "decrypt"):
                    generated_filename = str(uuid.uuid4())
                    print('Decrypting: ' + item)
                    pyAesCrypt.decryptFile(item, args.destination + "/" + generated_filename + args.extension, args.password, bufferSize)
                    if(args.kill):
                        os.remove(item)
                        print('File: "', item, '"Deleted (-k, --kill)"')

    if(decryptor):
        if(args.verbose):
            print('Decrypting via decryptor file.')
        # Get the path of the decryptor file
        # Where the files to decrypt are stored.
        path, filename = os.path.split(args.decryptor_file)

        # Decrypt the decryptor file
        pyAesCrypt.decryptFile(args.decryptor_file, path + "/metadata.yaml", args.password, (64 * 1024))

        # Loop through the files in $path
        # If one the file name match with one of the decryptor file,
        # Decrypts it with the data.
        fileData = yaml_init(['r', path + "/metadata.yaml", args.verbose])
        print('\nStarting...\n')
        counter = 0
        items = 0
        skip = 0
        for fileDecrypt in os.listdir(path):
            for item in fileData:
                if(item[1] == os.path.splitext(fileDecrypt)[0]):
                    if not find(item[0] + item[2], args.destination + '/'):
                        print(str(counter) + ': |' + fileDecrypt + '|')
                        pyAesCrypt.decryptFile(path + '/' + fileDecrypt, args.destination + '/' + item[0] + item[2], args.password, item[3])
                        if(args.kill):
                            os.remove(path + '/' + fileDecrypt)
                        counter += 1
                    else:
                        skip += 1
                        if(args.verbose):
                            print('Found duplicated. Skipping.')
            items += 1

        os.remove(path + "/metadata.yaml")
        if(args.kill):
            os.remove(args.decryptor_file)

        print('Decryption successful: ('+ str(counter) +' files decrypted out of '+ str(items) +') ('+ str(skip) +' skipped.)')

    if(args.mode == "encrypt"):
        print('Encrypting metadata file...')
        pyAesCrypt.encryptFile(args.destination + "/" + 'metadata.yaml', args.destination + "/libs.yaml", args.password, (64 * 1024))
        os.remove(args.destination + "/" + 'metadata.yaml')        

    print('done.')

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def getSize(path):
    st = os.stat(path)
    return st.st_size

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

if __name__ == "__main__":
    main()