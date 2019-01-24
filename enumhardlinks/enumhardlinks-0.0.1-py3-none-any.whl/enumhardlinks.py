__all__ = ["get_hardlinks"]

import os, os.path, sys, ctypes

from ctypes import windll, Structure, byref, c_uint, create_unicode_buffer, addressof
from ctypes import c_size_t, sizeof, c_wchar_p, get_errno, c_wchar
from ctypes.wintypes import HWND, UINT, LPCWSTR, BOOL, DWORD, LPDWORD

kernel32 = ctypes.windll.kernel32

#def getvolumeinfo(path):
    #"""
    #Return information for the volume containing the given path. This is going
    #to be a pair containing (file system, file system flags).
    #"""

    ## Add 1 for a trailing backslash if necessary, and 1 for the terminating
    ## null character.
    #volpath = ctypes.create_unicode_buffer(len(path) + 2)
    #rv = kernel32.GetVolumePathNameW(path, volpath, len(volpath))
    #print(volpath.value)
    #if rv == 0:
        #raise WinError()

    #fsnamebuf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH + 1)
    #fsflags = DWORD(0)
    #rv = kernel32.GetVolumeInformationW(volpath, None, 0, None, None, byref(fsflags),
                              #fsnamebuf, len(fsnamebuf))
    #if rv == 0:
        #raise WinError()

    #return (fsnamebuf.value, fsflags.value)
##getvolumeinfo(r"C:\tmp\1.txt")

def getvolumepathname(path):
    # Add 1 for a trailing backslash if necessary, and 1 for the terminating null character.
    volpath = ctypes.create_unicode_buffer(len(path) + 2)
    rv = kernel32.GetVolumePathNameW(path, volpath, len(volpath))
    return volpath.value
#print(getvolumepathname(r"C:\tmp\3.txt"))

def get_hardlinks(filepath):
    vol = getvolumepathname(filepath)
    harlinks = []
    fsnamebuf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH + 1)
    lngth = DWORD(ctypes.wintypes.MAX_PATH)
    findHandle = kernel32.FindFirstFileNameW(filepath, 0, byref(lngth), fsnamebuf)
    #print(fsnamebuf.value)
    #print(findHandle)
    #print('--------------------------')
    if (findHandle != -1):
        harlinks.append(os.path.join(vol, fsnamebuf.value))
        while True:
            fsnamebuf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH + 1)
            lngth = DWORD(ctypes.wintypes.MAX_PATH)
            result = kernel32.FindNextFileNameW(findHandle, byref(lngth), fsnamebuf)
            #print(result)
            if not result : break;
            harlinks.append(os.path.join(vol, fsnamebuf.value))
    
    kernel32.FindClose(findHandle)
    return harlinks
   
args = sys.argv[1:] 
if args:
    filepath = args[0]
    statinfo = os.stat(filepath)
    if os.path.islink(filepath):
        real_path = "\n\tSymlink (" + os.path.realpath(filepath) + ") => " + os.readlink(filepath)
        print(real_path)
    numlinks = statinfo.st_nlink
    if numlinks > 1:
        print(f"\n  Number of hardlinks {numlinks}:\n")
        t = get_hardlinks(filepath)
        t.sort()
        for x in t:
            print(f"    {x}")
    else:
        print(f"\n\t{filepath}")