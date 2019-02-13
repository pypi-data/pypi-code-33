 #!/usr/bin/env python3
 # -*- coding: utf-8 -*-

import os
from glob import glob

def main(args):

    '''
    Set up package
    '''

    print ('Scafolding...')

    # Projects folder structure
    p = args.name + '/' + args.name
    os.makedirs(p)
    with open(p + '/__init__.py', 'w'):
        pass
    if args.modules:
        for mod in args.modules.strip().split(','):
            os.makedirs('/'.join([p, mod]))
            with open(p + '/' + mod + '/__init__.py', 'w'):
                pass
    os.mkdir(args.name + '/bin')

    # Standard files
    path = os.path.realpath(__file__)
    path = path.replace('prefil_files.py','')
    for name in glob(path + '*template*'):
        file_name = name.strip().split('/')[-1].replace('_template','')
        if file_name == 'gitignore':
            file_name ='.gitignore'
        if file_name == 'main.py':
            core(args, name, args.name + '/bin', file_name)
        else:
            core(args, name, args.name, file_name)

def core(args, name, folder, file_name):

    '''
    Copy core files
    '''

    with open(name, 'r') as fin:
        with open(folder + '/' + file_name, 'w') as fout:
            for line in fin:
                fout.write(line.replace(
                    'Liam McIntyre', args.author).replace(
                    'shimbalama@gmail.com', args.email))




