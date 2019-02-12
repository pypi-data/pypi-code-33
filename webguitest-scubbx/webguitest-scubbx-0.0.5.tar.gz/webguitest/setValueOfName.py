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
    from selenium.webdriver.support.ui import Select
    seleniumAvailable = True
except ImportError:
    pass

if seleniumAvailable:
    def setValueOfName(driver,elementName,valueToSet,delay=10):
        numTries = 1
        elemToSet = None
        print("    (0): locating {} ...".format(elementName))
        while (elemToSet is None) and (numTries < delay):
            try:
                elemToSet = Select(driver.find_element_by_name(elementName))
            except Exception as exp:
                if isinstance(exp, selenium.common.exceptions.NoSuchElementException):
                    print("    ({}) locating {} ...".format(numTries,elementName))
                else:
                    print(exp)
                    break
            finally:
                numTries += 1
                time.sleep(1)
        if elemToSet is None:
            print("    (x): could not locate name={}".format(elementName))
            return False
        elemToSet.select_by_visible_text(valueToSet)
        print("    (✓): set '{}' to '{}'".format(elementName,valueToSet))
        time.sleep(1)
        return True

else:
    def setValueOfName(driver,elementName,valueToSet,delay=10):
        print("ERROR: no module 'selenium' - 'setValueOfName()' is not available")
        return False
