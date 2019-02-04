import sys

from selenium.webdriver.common.by import By

class elements_to_be_present():

    def __init__(self, *locators):
        self.locators = locators

    def __call__(self, driver):
        for locator in self.locators:
            if locator.by == 'xpath':
                try: driver.find_element_by_xpath(locator.location)
                except:
                    return False
            else: return False
        return True

class elements_to_be_displayed():

    def __init__(self, *locators):
        self.locators = locators

    def __call__(self, driver):
        for locator in self.locators:
            if locator.by == 'xpath':
                try: 
                    if not driver.find_element_by_xpath(locator.location).is_displayed(): return False
                except:
                    return False
            else: return False
        return True