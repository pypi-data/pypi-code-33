from abc import ABC, abstractmethod
from typing import List

from zoot.automation.pages import Page
from zoot.automation.drivers import Driver

class Automation(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def get_driver(self)->Driver:
        pass

    @abstractmethod
    def get_pages(self)->List[Page]:
        pass

    @abstractmethod
    def get_current_page(self)->Page:
        pass

    @abstractmethod
    def get_page(self)->Page:
        pass

    @abstractmethod
    def set_current_page(self, page:Page):
        pass

    @abstractmethod
    def add_pages(self, *page:Page):
        pass




    

    