# -*- coding: utf-8 -*-
"""
@author: Allen
"""
import os
import click

@click.group()
def cmd():
    pass
    
@cmd.command()
@click.argument('src')
@click.option('--verbose', default = True)
@click.option('--o', default = None)
@click.option('--n', default = 10)
@click.option('--start', default = 0)
@click.option('--encoding', default = None)
def topline(**kwargs):
    src,output = kwargs['src'],kwargs['o']
    n,start = kwargs['n'],kwargs['start']
    encoding = kwargs['encoding']
    verbose = kwargs['verbose']
    n,start = int(n),int(start)
    with open(src) as f:
        if output:
            fo = open(output, "w")
        i = 0
        while i < n:
            i = i + 1
            line = f.readline()
            if not line:
                break
            if i > start:
                if not output and verbose:
                    print(line)
                if output:
                    fo.writelines(line)
        if output:
            fo.close()
    
if __name__=='__main__':
    cmd()
    