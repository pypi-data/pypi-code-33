"""Utility methods and classes"""
import time

import selenium.common.exceptions


# wait fors stolen from http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html
def wait_for(condition_function, timeout=3):
    """Wait for a condition to be true"""
    start_time = time.time()
    while time.time() < start_time + timeout:
        if condition_function():
            return True
        else:
            time.sleep(0.1)
    raise RuntimeError(
        'Timeout waiting for {}'.format(condition_function.__name__)
    )


class wait_for_page_load(object):
    """Waits for page load to complete, use when submitting forms via keypresses etc"""

    def __init__(self, browser):
        self.browser = browser

    def __enter__(self):
        self.old_page = self.browser.find_element_by_tag_name('html')

    def page_has_loaded(self):
        new_page = self.browser.find_element_by_tag_name('html')
        return new_page.id != self.old_page.id

    def __exit__(self, *_):
        wait_for(self.page_has_loaded)


def element_found_by_name(driver, name):
    """Shortcut for checking that named element can be found"""
    try:
        driver.find_element_by_name(name)
        return True
    except selenium.common.exceptions.NoSuchElementException:
        return False


def dump_source_and_screen(driver, path_prefix=''):
    """Dumps a screenshot and page source"""
    driver.save_screenshot('{}screenshot.png'.format(path_prefix))
    html = driver.page_source
    with open('{}source.html'.format(path_prefix), 'wb') as fp:
        fp.write(html)
