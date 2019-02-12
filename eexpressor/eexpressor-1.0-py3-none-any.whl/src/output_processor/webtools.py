from selenium import webdriver
import requests
from .. import errors


def get_html(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.text
    else:
        raise errors.CONNECTION_ERROR(r.status_code)


def get_headless_web_driver_selenium_chrome(url):
    options = webdriver.chrome.options.Options()
    options.add_argument('headless')
    options.add_argument('disable-gpu')
    options.add_experimental_option('prefs', {'intl.accept_languages':
                                              'en'})
    driver = webdriver.Chrome('chromedriver', options=options)
    driver.get(url)
    return driver
