#!/usr/bin/env python
from __future__ import print_function
import sys
import os
import subprocess
import re


interface_re = re.compile('^\s+SSID\s+:\s+(.*)\s+$')
key_re = re.compile('Key\sContent\W+\s+\:\s+(.*?)\r')
ssid_re = re.compile('     \:\s+(.*?)\r')


def printerr(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    

def win_get_pw_for_names(names):
    
    creds = {}
  
    for ssid in names:
        try:
            cmd = r'netsh wlan show profile name="{}" key=clear'.format(ssid)
            output = subprocess.check_output(cmd)
        except subprocess.CalledProcessError as e:
            printerr ('failed querying clear passwords')
            return None

        r = key_re.search(output.decode("utf-8"))
        pwd = r.group(1) if r else ''        
        creds[ssid] = pwd
        
    return creds


def win_get_connected_names():
    try:
        output = subprocess.check_output(['Netsh','WLAN','show','interfaces'])
    except CalledProcessError as e:
        printerr ('failed querying interfaces')
        return None

    connected_wlans = []
    
    for l in output.decode("utf-8").split('\n'):
        r = interface_re.search(l)
        if r:
            connected_wlans.append(r.group(1))
    
    return None or connected_wlans


def win_get_names_substr(substr):
    
    try:
        output = subprocess.check_output(['netsh','wlan','show','profile'])
    except CalledProcessError as e:
        printerr ('failed querying known networks')
        return None

    ssids = []
    
    for l in output.decode("utf-8").split('\n'):
        r = ssid_re.search(l)
        if r:
            ssidname = r.group(1)
            lowssid =  ssidname.lower()
            if substr == '*' or substr.lower() in lowssid:
                ssids.append(ssidname)
    
    return ssids


def win_get_creds(substr=''):
    if substr:
        names = win_get_names_substr(substr)
    else:
        names = win_get_connected_names()
    
    if not names:
        return {}

    creds = win_get_pw_for_names(names) 
    if not creds:
        return {}
    
    return creds


def main():
    import platform
    win =  platform.system().lower() == 'windows'

    subname =sys.argv[1] if len(sys.argv) > 1 else ''

    if win:
        creds = win_get_creds(subname)
    else:
        printerr('platform not supported')
        exit(1)

    for ssid in creds:
        print ('{: <36} {}'.format(ssid, creds[ssid]))
    

if __name__ == '__main__':
    main()
