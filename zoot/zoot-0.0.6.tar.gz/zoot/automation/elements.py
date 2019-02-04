from typing import Any
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from zoot.automation.drivers import Driver
from zoot.automation.wait import elements_to_be_displayed

class Locator():

    def __init__(self, name:str, by:str, location:str, wait:bool=False):
        self.name = name
        self.location = location
        self.wait = wait

        if by not in ['xpath']:
            raise Exception('By method not supported yet by framework: {}'.format(by))
        self.by = by

class Element():

    def __init__(self, wd:Driver, locator:Locator, eager_load:bool=False):
        self.__driver = wd
        self.__locator = locator
        self.refresh()
        self.__eager_load = eager_load

    def eager_load(self):
        if self.__eager_load:
            self.refresh()

    def refresh(self):
        if self.__locator.by == 'xpath':
            try: self.__element = self.__driver.find_element_by_xpath(self.__locator.location)
            except: raise Exception("Element not found ({}) at: {}".format(self.__locator.name, self.__locator.location))
        else: raise Exception("By method not supported yet by framework: {}".format(self.__locator.by))

    def parent_raw(self):
        if self.__locator.by == 'xpath':
            return self.__driver.find_element_by_xpath(self.__locator.location).parent
        return None

    def parent(self):
        if self.__locator.by == 'xpath':
            return Element(self.__driver, self.__driver.find_element_by_xpath(self.__locator.location).parent)
        return None

    def clear(self):
        self.__element.clear()

    def click(self):
        self.__element().click()

    def click_action(self):
        actions = ActionChains(self.__driver.driver)
        actions.move_to_element(self.__element)
        actions.click()
        actions.perform()

    def click_js(self):
        self.eager_load()
        self.__driver.driver.execute_script("arguments[0].click();", self.__element)

    def set_text(self, text:str):
        self.eager_load()
        self.__element.send_keys(text)

    def get_text(self):
        return self.__element.text

    def set_attr_value(self, attr:str, value:str):
        self.eager_load()
        self.__driver.driver.execute_script("arguments[0].{}='{}'".format(attr, value))
        self.__driver.driver.execute_script("arguments[0].onchange;", self.__element)

    def get_select(self):
        self.eager_load()
        return Select(self.__element)

    def set_value(self, value:str):
        self.eager_load()
        self.__element.set_value(value)

    def submit(self):
        self.eager_load()
        self.__element.submit()

    def is_present(self):
        try:
            self.refresh()
            return True
        except:
            return False

    def is_displayed(self):
        try:
            self.eager_load()
            return self.__element.is_displayed()
        except:
            return False
    
    def is_enabled(self):
        try:
            self.eager_load()
            return self.__element.is_enabled()
        except:
            return False

    def is_clickable(self):
        return self.is_displayed() and self.is_enabled()

    def wait_until_present(self, timeout:int):
        if self.__locator.by == 'xpath':
            WebDriverWait(self.__driver.driver, timeout).until(EC.presence_of_element_located((By.XPATH, self.__locator.location)))
        else: raise Exception("By method not supported by framework: "+self.__locator.by)

    def wait_until_displayed(self, timeout:int):
        if self.__locator.by == 'xpath':
            WebDriverWait(self.__driver.driver, timeout).until(elements_to_be_displayed((By.XPATH, self.__locator.location)))
        else: raise Exception("By method not supported by framework: "+self.__locator.by)

    def wait_until_clickable(self, timeout:int):
        if self.__locator.by == 'xpath':
            WebDriverWait(self.__driver.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, self.__locator.location)))
        else: raise Exception("By method not supported by framework: "+self.__locator.by)

