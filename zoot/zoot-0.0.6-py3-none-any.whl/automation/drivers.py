import abc

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Callable, Any

from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.ie.options import Options as IEOptions
from abc import ABC, abstractmethod


class Driver(ABC):

    def __init__(self, timeout:int, driver:any):
        self.__driver = driver
        self.set_implicit_wait(timeout)

    def find_element_by_xpath(self, xpath:str):
        raise NotImplementedError('Implementors must override "find_element_by_xpath" to use Driver class.')

    def find_elements_by_xpath(self, xpath:str):
        raise NotImplementedError('Implementors must override "find_elements_by_xpath" to use Driver class.')

    def set_implicit_wait(self, timeout:int):
        self.__timeout = timeout
        self.__driver.implicitly_wait(self.__timeout)

    def get_implicit_wait(self):
        return self.__timeout

    def get_raw(self):
        return self.__driver

    def get_url(self):
        raise NotImplementedError('Implementors must override "get_url" to use Driver class.')

    def navigate(self, url:str):
        self.__driver.get(url)

    @abstractmethod
    def close(self):
        pass

    
class SeleniumDriver(Driver):

    def __init__(self, driver:WebDriver):
        super().__init__(0, driver)

    def find_element_by_xpath(self, xpath:str):
        return self.__driver.find_element_by_xpath(xpath)

    def find_elements_by_xpath(self, xpath:str):
        raise self.__driver.find_elements_by_xpath(xpath)

    def get_url(self):
        return self.__driver.current_url

    def close(self):
        self.__driver.close()

class SafariDriver(SeleniumDriver):

    def __init__(self):
        super().__init__(webdriver.Safari())


class ChromeDriver(SeleniumDriver):

    def __init__(self, path:str, headless:bool=True):

        options = ChromeOptions()
        options.set_headless(headless)
        options.add_argument('--log-level=3')

        super().__init__(webdriver.Chrome(options=options, executable_path=path))

class FirefoxDriver(SeleniumDriver):

    def __init__(self, path:str, headless:bool=True):

        options = FirefoxOptions()
        options.set_headless(headless)

        super().__init__(webdriver.Firefox(options=options, executable_path=path))


class IEDriver(SeleniumDriver):

    def __init__(self, path:str):

        options = IEOptions()

        super().__init__(webdriver.Firefox(options=options, executable_path=path))