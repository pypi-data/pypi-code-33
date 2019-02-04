from typing import Dict

from selenium.webdriver.support.ui import WebDriverWait

from zoot.automation.drivers import Driver

from zoot.automation.elements import Locator

from zoot.automation.wait import elements_to_be_present

class PageInfo():

    def __init__(self, name:str, url:str, wait:bool, timeout:int):
        self.__name = name
        self.__url = url
        self.__wait = wait
        self.__timeout = timeout

    def get_name(self) -> str:
        return self.__name

    def get_url(self) -> str:
        return self.__url

    def get_wait(self) -> bool:
        return self.__wait

    def get_timeout(self) -> int:
        return self.__timeout

class Page():  

    def __init__(self, info:PageInfo, locators:Dict[str,Locator]={}, data:Dict[str, any]={}):
        
        self.info = info
        self.locators = locators
        self.data = data

    def via(self, driver:Driver):
        driver.navigate(self.info.get_url())

    def at(self, driver:Driver):
    
        if self.info.get_wait():
            waiters = [ locator for name, locator in self.locators.items() if locator.wait ]
            WebDriverWait(driver.get_raw(), self.info.get_timeout()).until(elements_to_be_present(*waiters))
        else:
            waiters = [ locator for name, locator in self.locators.items() if locator.wait ]
            WebDriverWait(driver.get_raw(), 0).until(elements_to_be_present(*waiters))

    def to(self, driver:Driver):
        self.via(driver)
        self.at(driver)

    def isAt(self, driver:Driver) -> bool:
        try:
            self.at(driver)
        except Exception as e:
            return False
        return True   
