from typing import Dict
from appium import webdriver
from zoot.automation.drivers import Driver

class MobileDriver(Driver):

    def __init__(self, url:str, capabilities:Dict[str, any]):
        super().__init__(0, webdriver.Remote(url, capabilities))

    def find_element_by_xpath(self, xpath:str):
        return self.get_raw().find_element_by_xpath(xpath)

    def find_elements_by_xpath(self, xpath:str):
        return self.get_raw().find_elements_by_xpath(xpath)

    def get_url(self):
        return self.get_raw().get_url()

    def close(self):
        self.get_raw().close()
        

    