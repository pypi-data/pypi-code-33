import perfecto
import os
import robot
import inspect
import PerfectoLibrary
import appium
from perfecto import *
from robot.libraries.BuiltIn import BuiltIn
# from appium import webdriver
from .keywordgroup import KeywordGroup
from ..listeners import *


class _DeviceKeywords(KeywordGroup):
    def __init__(self):
        self.bi = BuiltIn()

    def _check_driver(self):
        # self.bi.log_to_console("_check_driver")

        try:
            aplib = self.bi.get_library_instance('AppiumLibrary')
            self.driver = aplib._current_application()
            return True
        except:
            self.bi.log_to_console("Your script is not using Appium Driver, devices keywords will not be able to performed")
            return False

    def enable_proxy(self, str):
        proxy = str
        os.environ['http_proxy'] = proxy
        os.environ['HTTP_PROXY'] = proxy
        os.environ['https_proxy'] = proxy
        os.environ['HTTPS_PROXY'] = proxy

    def disable_proxy(self):
        proxy = ""
        os.environ['http_proxy'] = proxy
        os.environ['HTTP_PROXY'] = proxy
        os.environ['https_proxy'] = proxy
        os.environ['HTTPS_PROXY'] = proxy
        try:
            del os.environ['http_proxy']
            del os.environ['https_proxy']
            del os.environ['HTTP_PROXY']
            del os.environ['HTTPS_PROXY']
        except:
            pass


    def install_application(self, repoName, isSensorInstrument):
        if self._check_driver():
            sensorInstrument = 'nosensor'
            if isSensorInstrument.lower() == 'true':
                sensorInstrument = 'sensor'
            params = {}
            params['sensorInstrument'] = sensorInstrument
            params['file'] = repoName
            self.driver.execute_script('mobile:application:install', params)

    def uninstall_application(self, name):
        if self._check_driver():
            params = {}
            params['identifier'] = name
            self.driver.execute_script('mobile:application:uninstall', params)

    def start_application_by_name(self, name):
        if self._check_driver():
            params = {}
            params['identifier'] = name
            self.driver.execute_script('mobile:application:open', params)

    def close_application_by_name(self, name):
        if self._check_driver():
            params = {}
            params['identifier'] = name
            self.driver.execute_script('mobile:application:close', params)

    def open_system_browser(self):
        if self._check_driver():
            params = {}
            params['automation'] = 'os'
            self.driver.execute_script('mobile:browser:open', params)

    def browser_execute_script(self, scriptString):
        if self._check_driver():
            params = {}
            params['script'] = scriptString
            params['timeout'] = '35'
            self.driver.execute_script('mobile:browser:execute', params)

    def browser_execute_repo_script(self, scriptRepoLoc):
        if self._check_driver():
            params = {}
            params['repositoryFile'] = scriptRepoLoc
            params['timeout'] = '35'
            self.driver.execute_script('mobile:browser:execute', params)

    def maximize_window(self):
        if self._check_driver():
            self.driver.maximize_window()

    def scroll_to_element(self, elementxpath):
        if self._check_driver():
            params = {}
            params['element'] = (self.driver.findElement(By.xpath(elementxpath))).GetId()
            params['toVisible'] = 'any'
            self.driver.execute_script('mobile:scroll', params)

    # devices actions
    def rotate(self, state='landscape', method='device'):
        if self._check_driver():
            params = {}
            params['state'] = state
            params['method'] = method
            self.driver.execute_script('mobile:device:rotate', params)
            
    def browser_execute_script(self,text,timeout='20'):
        if self._check_driver():
            params = {}
            params['script'] = text
            params['timeout'] = timeout
            self.driver.execute_script('mobile:browser:execute', params)
            
    def drag(self, x1, y1, x2, y2, duration='5'):
        '''
        The touch event coordinates.
        Format - either "x1,y1,x2,y2" or "x1%,y1%,x2%,y2%"
        Coordinate value can be in pixels or in percentage of screen size (0-100).
        For percentage use the % sign. Example - "20%, 25%"
        It is recommended to use the percentage value as it translates to the screen resolution.
        :param duration: The duration, in seconds, for performing the drag operation.
        :return: None
        '''
        if self._check_driver():
            params = {}
            params['location'] = x1 + ',' + y1 + ',' + x2 + ',' + y2
            params['duration'] = duration
            self.driver.execute_script('mobile:touch:drag', params)

    def gesture(self, startx, starty, endx, endy, operation='Zoom', duration='5'):
        '''

        :param startx, starty:The start, touch down, event coordinates.
                Format - "x,y" or "x%,y%"
                Coordinate value can be in pixels or in percentage of screen size (0-100).
                For percentage use the % sign.
                Example - 50%, 50%
                It is recommended to use the percentage value as it does not rely on the screen resolution.
        :param endx,endy:The end, touch up, event coordinates.
                Format - "x,y" or "x%,y%"
                Coordinate value can be in pixels or in percentage of screen size (0-100).
                For percentage use the % sign.
                Example - 50%, 50%
                It is recommended to use the percentage value as it does not rely on the screen resolution.
        :param operation:    The gesture operation type.
                Zoom - performs pinch open operation from the start coordinates to the end coordinates.
                Pinch - performs pinch close operation from the start coordinates to the end coordinates
        :param duration: The duration, in seconds, for performing the operation.
        :return:None
        '''
        if self._check_driver():
            params = {}
            params['start'] = startx + ',' + starty
            params['end'] = endx + ',' + endy
            params['operation'] = operation
            params['duration'] = duration
            self.driver.execute_script('mobile:touch:gesture', params)

    def swipe(self, startx, starty, endx, endy, duration='5'):
        '''
        :param startx, starty:The start, touch down, event coordinates.
                Format - "x,y" or "x%,y%"
                Coordinate value can be in pixels or in percentage of screen size (0-100).
                For percentage use the % sign.
                Example - 50%, 50%
                It is recommended to use the percentage value as it does not rely on the screen resolution.
        :param endx,endy:The end, touch up, event coordinates.
                Format - "x,y" or "x%,y%"
                Coordinate value can be in pixels or in percentage of screen size (0-100).
                For percentage use the % sign.
                Example - 50%, 50%
                It is recommended to use the percentage value as it does not rely on the screen resolution.
        :param duration: The duration, in seconds, for performing the operation.
        :return:None
        '''
        if self._check_driver():
            params = {}
            params['start'] = startx + ',' + starty
            params['end'] = endx + ',' + endy
            params['duration'] = duration
            self.driver.execute_script('mobile:touch:swipe', params)

    def perfecto_tap(self, locx, locy, duration='5'):
        '''
        Note: As a best practice, this function should only be used in extreme circumstances because it is not
        accurate or adaptable to application modifications. Alternatively, screen analysis functions are recommended for robust automated testing.
        :param locx, locy:The touch event coordinates.
                Format - either "x1,y1,x2,y2" or "x1%,y1%,x2%,y2%"
                Coordinate value can be in pixels or in percentage of screen size (0-100).
                For percentage use the % sign. Example - "20%, 25%"
                It is recommended to use the percentage value as it translates to the screen resolution.
        :param duration:The duration, in seconds, for performing the touch operation.
                Use this to perform a "long-press".
        :return: none
        '''
        if self._check_driver():
            params = {}
            params['location'] = locx + ',' + locy
            params['duration'] = duration
            self.driver.execute_script('mobile:touch:tap', params)

    def trackball_roll(self, distance='0,0'):
        '''
        :param distance: The distance from the last location coordinates.
                Format - x,y
                Note: This command receives an x,y sequence relative to the last location coordinates that are not absolute coordinates on the screen.
        :return: none
        '''
        if self._check_driver():
            params = {}
            params['distance'] = distance
            self.driver.execute_script('mobile:trackball:roll', params)

    # Visual Analysis Functions
    def button_image_click(self, label, threhold=80):
        '''
        :param label: Repository path to image file (png, jpg). The image that appears on, or related to, the button
        :param threhold:The acceptable match level percentage, between 20 and 100.
                Too low values can lead to a false positive result, while too high values can lead to a false negative result.
        :return: none
        '''
        if self._check_driver():
            params = {}
            params['label'] = label
            params['threshold'] = threhold
            params['imageBounds.needleBound'] = 30
            self.driver.execute_script('mobile:button-image:click', params)

    def button_text_click(self, label, ignorecase='true'):
        '''
        :param label: Repository path to image file (png, jpg). The image that appears on, or related to, the button
        :param threhold:The acceptable match level percentage, between 20 and 100.
                Too low values can lead to a false positive result, while too high values can lead to a false negative result.
        :return: none
        '''
        if self._check_driver():
            if ignorecase.lower() == 'false':
                ignorecase = 'case'
            else:
                ignorecase = 'nocase'
            params = {}
            params['label'] = label
            params['ignorecase'] = ignorecase
            params['threshold'] = 80
            self.driver.execute_script('mobile:button-text:click', params)

    def find_image_in_screen(self, content, context='body'):
        '''
        :param content:The image to search for.
                    The image can be taken from the device screen using the preview tool or selected from the media repository.
                    If selected from the repository the image must be a JPEG, PNG or BMP file.
        :param context: all | body    Defines the screen region where to look for the needle.
        :return: String indicating success ("true") or failure ("false")
        '''
        if self._check_driver():
            params = {}
            params['content'] = content
            params['context'] = context
            return self.driver.execute_script('mobile:image:find', params)
        return False

    def find_text_in_screen(self, content, context='body'):
        '''
        :param content:The text to search for.
                It is recommended to use the entire string searched for, to ensure that if the OCR misses a few characters, the needle will still be found.
                The text-match algorithm is less error-prone when the provided string is longer.
        :param context: all | body    Defines the screen region where to look for the needle.
        :return: String indicating success ("true") or failure ("false")
        '''
        if self._check_driver():
            params = {}
            params['content'] = content
            params['context'] = context
            return self.driver.execute_script('mobile:text:find', params)
        return False