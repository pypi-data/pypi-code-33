from zoot.automation.mobile.common import AppiumData
from zoot.automation.pages import Page, PageInfo
from zoot.automation.common import Automation
from zoot.testing.environments import Environment
from zoot.automation.drivers import Driver, ChromeDriver, FirefoxDriver, SafariDriver, IEDriver
from zoot.automation.mobile.drivers import MobileDriver
from zoot.utils import files

from typing import Dict, List

class AutomationEnvironment(Environment, Automation):

    def __init__(self, parse_json:bool=False,  *required_args:str, **optional_args:str):

        if optional_args:
            if 'appium_path' in optional_args: optional_args['appium_path'] = None
            if 'appium_url' in optional_args: optional_args['appium_url'] = None
            if 'appium_udid' in optional_args: optional_args['appium_udid'] = None
            if 'appium_dc_user' in optional_args: optional_args['appium_dc_user'] = None
            if 'appium_dc_key' in optional_args: optional_args['appium_dc_key'] = None
        else:
            optional_args = {
                'appium_path':None,
                'appium_url':None,
                'appium_udid':None,
                'appium_dc_user':None,
                'appium_dc_key':None
            }

        args = None

        if required_args:

            args = list(required_args)

            for arg in ['driver_path', 'os', 'browser', 'url']:
                args.append(arg)

        else:
            args = ['driver_path', 'os', 'browser', 'url']

        Environment.__init__(self, parse_json, self.post_build, *args, **optional_args)
        Automation.__init__(self)

        self.driver_path = None
        self.appium_path = None

        self.os = None
        self.browser = None
        self.url = None

        self.__driver = None
        self.__current_page = None
        self.__pages = {}
        self.__appium = None

    def post_build(self, args:Dict[str, any]):

        self.os = args['os']
        self.browser = args['browser']
        self.driver_path = args['driver_path']
        self.url = args['url']
        self.appium_path = args['appium_path']

        if not self.appium_path:
            if ('appium_url' in args and 'appium_udid' in args) and (args['appium_url'] and args['appium_udid']):

                data = {'udid':args['appium_udid']}

                if 'appium_dc_user' in args and 'appium_dc_key' in args:
                    data['deviceConnectUserName'] = args['appium_dc_user']
                    data['deviceConnectApiKey'] = args['appium_dc_key']

                self.__appium = AppiumData(args['appium_url'], data)

        else:
            data = files.parse_json(self.appium_path, 'url', 'udid')
            url = data['url']
            del data['url']
            self.__appium = AppiumData(url, data)

    def load_driver(self)->Driver:

        if self.os in ['windows', 'darwin', 'linux']:

            if self.browser == 'chrome':
                return ChromeDriver(self.driver_path)

            elif self.browser == 'firefox':
                return FirefoxDriver(self.driver_path)
            elif self.os == 'darwin' and self.browser == 'safari':
                return SafariDriver()
            elif self.os == 'windows' and self.browser == 'ie':
                return IEDriver(self.driver_path)
            else:
                raise Exception("OS '{}' does not support '{}' browser")
        elif self.os in ['ios', 'android']:
            return MobileDriver(self.__appium.get_url(), self.__appium.get_data())
        else:
            raise Exception("'{}' OS not yet supported".format(self.os))

    def get_driver(self) -> Driver:
        if not self.__driver:
            self.__driver = self.load_driver()

        return self.__driver

    def get_pages(self) -> List[Page]:

        return self.__pages.values()

    
    def get_page(self, name:str) -> Page:

        if name in self.__pages:
            return self.__pages[name]
        else:
            return None

    def get_current_page(self) -> Page:
        return self.__current_page

    def set_current_page(self, page:Page)->Page:
        self.__current_page = page

    def add_pages(self, *pages:Page):
        for page in pages:
            self.__pages[page.info.get_name()] = page
