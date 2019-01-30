#!usr/bin/env python
#-*- coding:utf-8 -*-

def data_transfer(src, desc, data):
    if src == 'PortScanPlugin' and desc == 'PocScanPlugin':
        return data
    elif src == 'src' and desc == 'desc':
        return data

    return data

