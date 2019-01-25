from ctypes import *
from struct import *
import os, sys, re

class WinColorConsole(object):
    """Class that provides methods to output color on Windows-based consoles"""
    STD_OUTPUT_HANDLE = -11
    COLORS = [0, 4, 2, 6, 1, 5, 3, 7]
    
    def __init__(self, stream):
        self.stream = stream
        # windows specific stuff from kernel32 API
        self.GetStdHandle = windll.kernel32.GetStdHandle
        self.GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo
        self.SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
        self.hConsoleHandle = self.GetStdHandle(self.STD_OUTPUT_HANDLE)

    def write(self, msg):
        rest = msg
        colorlist = re.findall(r'\x1B\[[^A-Za-z]*[A-Za-z]', msg)
        pos = 0
        for i in colorlist:
            color = i[i.find('[') + 1 : i.find('m')]
            pos = rest.find(i)
            if pos == 0:
                # the color code is the first part of the string
                # change color and slice the bytes, next color
                self.setcolor(int(color))
                rest = rest.replace(i, '')
                continue
            elif pos > 0:
                # otherwise write the color text
                # then change color again
                self.stream.write(rest[:pos])
                self.setcolor(int(color))
                rest = rest.replace(i , '')
                continue
                
        self.stream.write(rest[pos:])
        
    def flush(self):
        self.stream.flush()

    def setcolor(self, color):
        csbi = chr(0) * 22
        self.GetConsoleScreenBufferInfo(self.hConsoleHandle, csbi)
        wAttr = unpack('H', csbi[8:10])[0]
        
        if int(color) == 0: # reset
            wAttr = 0x07
        elif int(color) == 1: # bold
            wAttr |= 0x08
        elif int(color) == 2: # unbold
            wAttr &= -0x09
        elif int(color) == 7: # reverse
            wAttr = ((wAttr & 0x0f) << 4) | ((wAttr & 0xf0) >> 4)
        elif int(color) == 8: # conceal
            wAttr &= -16
        elif int(color) in range(30, 38): # foreground colors
            wAttr = ((wAttr & (-8)) | (self.COLORS[color - 30]))
        elif int(color) in range(40, 48): # background colors
            wAttr = ((wAttr & (-113)) | (self.COLORS[color - 40] << 4))
        
        self.SetConsoleTextAttribute(self.hConsoleHandle, wAttr)	
