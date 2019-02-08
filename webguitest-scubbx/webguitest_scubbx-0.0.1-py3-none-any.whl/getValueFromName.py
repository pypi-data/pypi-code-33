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

if seleniumAvailable:
    def getValueFromName(driver,elementName,delay=10):
        numTries = 1
        elemToExtract = None
        print("    (0): locating {} ...".format(elementName))
        while (elemToExtract is None) and (numTries < delay):
            try:
                elemToExtract = driver.find_element_by_name(elementName)
            except Exception as exp:
                if isinstance(exp, selenium.common.exceptions.NoSuchElementException):
                    print("    ({}) locating {} ...".format(numTries,elementName))
                else:
                    print(exp)
                    break
            finally:
                numTries += 1
                time.sleep(1)
        if elemToExtract is None:
            print("    (x): could not locate name={}".format(elementName))
            return False
        return elemToExtract.get_attribute("value")

else:
    def getValueFromName(elementName,delay=10):
        print("ERROR: no module 'selenium' - 'getValueFromName()' is not available")
        return False
