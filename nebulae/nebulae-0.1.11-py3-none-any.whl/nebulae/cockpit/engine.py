#!/usr/bin/env python
'''
engine
Created by Seria at 23/11/2018 2:36 PM
Email: zzqsummerai@yeah.net

                    _ooOoo_
                  o888888888o
                 o88`_ . _`88o
                 (|  0   0  |)
                 O \   。   / O
              _____/`-----‘\_____
            .’   \||  _ _  ||/   `.
            |  _ |||   |   ||| _  |
            |  |  \\       //  |  |
            |  |    \-----/    |  |
             \ .\ ___/- -\___ /. /
         ,--- /   ___\<|>/___   \ ---,
         | |:    \    \ /    /    :| |
         `\--\_    -. ___ .-    _/--/‘
   ===========  \__  NOBUG  __/  ===========
   
'''
# -*- coding:utf-8 -*-
from ..law import Law

def Engine(config=None, device=None, available_gpus='', gpu_mem_fraction=1,
                        if_conserve=True, least_mem=2048):
    if config is None:
        param = {'device': device, 'available_gpus': available_gpus, 'gpu_mem_fraction': gpu_mem_fraction,
                      'if_conserve': if_conserve, 'least_mem': least_mem}
    else:
        config['available_gpus'] = config.get('available_gpus', available_gpus)
        config['gpu_mem_fraction'] = config.get('gpu_mem_fraction', gpu_mem_fraction)
        config['if_conserve'] = config.get('if_conserve', if_conserve)
        config['least_mem'] = config.get('least_mem', least_mem)
        param = config

    core = Law.CORE.upper()
    if core == 'TENSORFLOW':
        from .engine_tf import EngineTF
        return EngineTF(param)
    else:
        raise ValueError('%s has not been a supported core.' % core)