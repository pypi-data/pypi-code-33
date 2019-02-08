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
    def clickTextElement(driver,elementText,delay=10):
        numTries = 1
        elemToClick = None
        print("     0 : locating {} ...".format(elementText))
        while (elemToClick is None) and (numTries < delay):
            try:
                elemToClickResults = driver.find_elements_by_xpath("//*[text() = '{}']".format(elementText))
                elemToClick = elemToClickResults[0]
                if len(elemToClickResults) > 1: 
                    print("        found multiple '{}' - selecting only the first one".format(elementText))
            except Exception as exp:
                if isinstance(exp, selenium.common.exceptions.NoSuchElementException):
                    print("     {}  locating {} ...".format(numTries,elementText))
                else:
                    print(exp)
                    break
            finally:
                numTries += 1
                time.sleep(1)
        if elemToClick is None:
            print("    (x): could not locate Text={}".format(elementText))
            return False
        elemToClick.click()
        print("    (✓): clicked on {}".format(elementText))
        return True

else:
    def clickTextElement(driver,elementText,delay=10):
        print("ERROR: no module 'selenium' - 'enterValueToName()' is not available")
        return False
