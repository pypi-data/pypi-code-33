import sys
import yaml
from yaml import load, dump
import os
import io

def yaml_init(args):

    mode = args[0]
    read_write_file = args[1]
    data = []
    if(mode == 'w'):
        data = args[2]
        verbose = args[3]
    else:
        verbose = args[2]

    #cwd = os.getcwd()

    if(mode == 'w'):
        with io.open(read_write_file, 'a', encoding='utf8') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)
            if(verbose):
                print('Written: ' + str(data) + '\nin ' + read_write_file)
    else:
        with open(read_write_file, 'r') as stream:
            items = yaml.load(stream)
            if(verbose):
                print(str(items))
            return (items)