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
    from selenium.webdriver.common.keys import Keys
    seleniumAvailable = True
except ImportError:
    pass


if seleniumAvailable:
    def clickName(driver,elementName,delay=10):
        numTries = 1
        elemToClick = None
        print("    (0): locating {} ...".format(elementName))
        while (elemToClick is None) and (numTries < delay):
            try:
                elemToClick = driver.find_element_by_name(elementName)
            except Exception as exp:
                if isinstance(exp, selenium.common.exceptions.NoSuchElementException):
                    print("    ({}) locating {} ...".format(numTries,elementName))
                else:
                    print(exp)
                    break
            finally:
                numTries += 1
                time.sleep(1)
        if elemToClick is None:
            print("    (x): could not locate name={}".format(elementName))
            return False
        elemToClick.click()
        print("    (✓): clicked on {}".format(elementName))
        return True

else:
    def clickName(driver,elementName,delay=10):
        print("ERROR: no module 'selenium' - 'enterValueToName()' is not available")
        return False
