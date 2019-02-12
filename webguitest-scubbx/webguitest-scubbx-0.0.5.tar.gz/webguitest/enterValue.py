#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
pyautoguiAvailable = False
seleniumAvailable = False

try:
    import pyautogui
    pyautoguiAvailable = True
except ImportError:
    pass

try:
    import selenium
    seleniumAvailable = True
except ImportError:
    pass

if pyautoguiAvailable:
    def enterValue(textcontent,pressEnter=False,delay=10):
        time.sleep(0.5)
        pyautogui.typewrite(textcontent)
        print("    (✓): entered text '{}'".format(textcontent))
        if pressEnter:
            pyautogui.typewrite("\n")
        time.sleep(1)
        return True
else:
    def enterValue(textcontent,pressEnter=False,delay=10):
        print("ERROR: no module 'pyautogui' - 'clickGraphic()' is not available")
        print("       maybe you missed to also install the 'Xlib' library on which pyautogui depends on")
        return False
